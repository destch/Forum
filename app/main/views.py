from datetime import datetime
from flask import (
    render_template,
    session,
    redirect,
    url_for,
    jsonify,
    flash,
    request,
    current_app,
    make_response,
)
from . import main
from .forms import (
    ThreadForm,
    LinkForm,
    EditProfileAdminForm,
    EditProfileForm,
    CommentForm,
    SearchForm,
    SceneForm,
)
from .. import db
from ..models import Post, Comment, User, Permission, Scene
import json
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import boto3
from sqlalchemy import or_
from flask_login import login_user, logout_user


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template("user.html", user=user, posts=posts)


@main.route("/", methods=["GET", "POST"])
def index():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        text = search_form.text.data
        return redirect(url_for(".results", text=text))
    page = request.args.get("page", 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get("show_followed", ""))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    return render_template(
        "index.html",
        posts=posts,
        show_followed=show_followed,
        pagination=pagination,
        search_form=search_form,
    )


@main.route("/<int:id>/posts", methods=["GET", "POST"])
def scene(id):
    form = SearchForm()
    if form.validate_on_submit():
        text = form.text.data
        return redirect(url_for(".results", text=text))
    page = request.args.get("page", 1, type=int)
    query = Post.query.filter_by(scene_id=id)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    return render_template(
        "scene.html", posts=posts, pagination=pagination, search_form=form
    )


@main.route("/results/<text>", methods=["GET", "POST"])
def results(text):
    form = SearchForm()
    if form.validate_on_submit():
        text = form.text.data
        return redirect(url_for(".results", text=text))
    page = request.args.get("page", 1, type=int)
    query = Post.query.join(Scene).filter(
        or_(
            Post.title.ilike("%" + text + "%"),
            Post.body.ilike("%" + text + "%"),
            Scene.name.ilike("%" + text + "%"),
        )
    )
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    return render_template(
        "results.html", posts=posts, pagination=pagination, search_form=form
    )


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        f = form.image.data
        if f is not None:
            user_id = current_user.id
            filename = str(user_id) + secure_filename(f.filename)
            s3_client = boto3.resource("s3")
            bucket = s3_client.Bucket("groovespotimages")
            bucket.Object(filename).put(Body=f)
            current_user.profile_pic_filename = filename
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for(".user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for(".user", username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("edit_profile.html", form=form, user=user)


@main.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    post = Post.query.get_or_404(id)
    result = None
    comment_form = None
    search_form = None

    if "submit_comment" in request.form:
        comment_form = CommentForm()
        result = process_comment_form(comment_form, post)
    elif "submit_search" in request.form:
        search_form = SearchForm()
        result = process_search_form(search_form)

    if result is not None:
        return result

    if comment_form is None:
        comment_form = CommentForm(formadata=None, obj=...)
    if search_form is None:
        search_form = SearchForm(formdata=None, obj=...)

    page = request.args.get("page", 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config[
            "FLASKY_COMMENTS_PER_PAGE"
        ] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"], error_out=False
    )
    comments = pagination.items
    return render_template(
        "post_test.html",
        post=post,
        comment_form=comment_form,
        search_form=search_form,
        comments=comments,
        pagination=pagination,
    )


def process_comment_form(comment_form, post):
    if comment_form.validate_on_submit():
        if current_user.__repr__() == "Anonymous":
            user = User.query.filter_by(username="Anonymous").first()
            login_user(user)
            author = current_user._get_current_object()
            logout_user()
        else:
            author = current_user._get_current_object()

        comment = Comment(body=comment_form.body.data, post=post, author=author)
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been published.")
        return redirect(url_for(".post", id=post.id, page=-1))


def process_search_form(search_form):
    if search_form.validate_on_submit():
        text = search_form.text.data
        return redirect(url_for(".results", text=text))


@main.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("The post has been updated.")
        return redirect(url_for(".post", id=post.id))
    form.body.data = post.body
    return render_template("edit_post.html", form=form)


@main.route("/follow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if current_user.is_following(user):
        flash("You are already following this user.")
        return redirect(url_for(".user", username=username))
    current_user.follow(user)
    db.session.commit()
    flash("You are now following %s." % username)
    return redirect(url_for(".user", username=username))


@main.route("/unfollow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if not current_user.is_following(user):
        flash("You are not following this user.")
        return redirect(url_for(".user", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash("You are not following %s anymore." % username)
    return redirect(url_for(".user", username=username))


@main.route("/followers/<username>")
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"], error_out=False
    )
    follows = [
        {"user": item.follower, "timestamp": item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        "followers.html",
        user=user,
        title="Followers of",
        endpoint=".followers",
        pagination=pagination,
        follows=follows,
    )


@main.route("/followed_by/<username>")
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"], error_out=False
    )
    follows = [
        {"user": item.followed, "timestamp": item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        "followers.html",
        user=user,
        title="Followed by",
        endpoint=".followed_by",
        pagination=pagination,
        follows=follows,
    )


@main.route("/all")
@login_required
def show_all():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "", max_age=30 * 24 * 60 * 60)
    return resp


@main.route("/followed")
@login_required
def show_followed():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "1", max_age=30 * 24 * 60 * 60)
    return resp


@main.route("/moderate")
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"], error_out=False
    )
    comments = pagination.items
    return render_template(
        "moderate.html", comments=comments, pagination=pagination, page=page
    )


@main.route("/moderate/enable/<int:id>")
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for(".moderate", page=request.args.get("page", 1, type=int)))


@main.route("/moderate/disable/", methods=["GET", "POST"])
@login_required
def moderate_disable():
    id = request.args.get("id", type=int)
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for(".post", id=request.args.get("post_id", type=int)))


@main.route("/moderate/disable/post", methods=["GET", "POST"])
@login_required
def moderate_disable_post():
    id = request.args.get("id", type=int)
    post = Post.query.get_or_404(id)
    post.disabled = True
    db.session.add(post)
    db.session.commit()
    return redirect(url_for(".index"))


@main.route("/new/thread", methods=["GET", "POST"])
@login_required
def new_thread():
    form = ThreadForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(
            body=form.body.data,
            title=form.title.data,
            scene=form.scene.data,
            type=form.type,
            author=current_user._get_current_object(),
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for(".index"))
    return render_template("new_thread.html", form=form)


@main.route("/new/link", methods=["GET", "POST"])
def new_link():
    form = LinkForm()
    scenes = Scene.query.all()
    if request.method == "POST":
        req = lambda x: request.form.get(x)
        if req('PostTitle') != '':
            post = Post(title=req('PostTitle'),
                        body=req('PostText'))
        elif req('FileTitle') != '':
            f = request.files['FileData']
            filename = ""
            if f is not None:
                post_id = Post.query.order_by(Post.id.desc()).first().id
                filename = str(post_id) + secure_filename(f.filename)
                s3_client = boto3.resource("s3")
                bucket = s3_client.Bucket("groovespotimages")
                bucket.Object(filename).put(Body=f)

            post = Post(title=req('FileTitle'),
                        thumbnail_file=filename)
            

        elif req('LinkTitle') != '':

            if "youtube.com" in str(req('LinkUrl')):
                link_noquery = str(req('LinkUrl')).split("&")[0]
                link = link_noquery.split("watch?v=")
                link_embed = "embed/".join(link)
                link_html = """
                    <div class="video-container">
                    <iframe width="500" height="300" src="{}" frameborder="0" 
                    allow="accelerometer; 
                    autoplay; 
                    encrypted-media; 
                    gyroscope; 
                    picture-in-picture" 
                    allowfullscreen></iframe>
                    </div>
                    """.format(link_embed) 

            elif "yout.be" in req('LinkUrl'):
                link_embed = str(req('LinkUrl')).split('/')[3]
                link_html = """
                    <div class="video-container">
                    <iframe width="500" height="300" src="{}" frameborder="0" 
                    allow="accelerometer; 
                    autoplay; 
                    encrypted-media; 
                    gyroscope; 
                    picture-in-picture" 
                    allowfullscreen></iframe>
                    </div>
                    """.format(link_embed)

            elif "soundcloud" in req('LinkUrl'):
                link_embed = str(req('LinkUrl'))
                link_html = """
                    <iframe width="500" height="200"
                    src="https://w.soundcloud.com/player/?url={}">
                    </iframe>
                    """.format(link_embed)

            else:
                link_html = str(req('LinkUrl'))

            post = Post(title=req('LinkTitle'),
                        link=link_html)

        else:
            flash('You must include a title')


        if current_user.__repr__() == "Anonymous":
            user = User.query.filter_by(username="Anonymous").first()
            login_user(user)
            author = current_user._get_current_object()
            logout_user()
        else:
            author = current_user._get_current_object()

        post.author = author
        post.scene_id = req('Scene')

        db.session.add(post)
        db.session.commit()

        return redirect(url_for(".index"))
    return render_template("new_link.html", scenes=scenes)


@main.route("/scenes", methods=["GET", "POST"])
def scenes():
    form = SearchForm()
    if form.validate_on_submit():
        text = form.text.data
        return redirect(url_for(".results", text=text))
    cities = Scene.query.filter_by(category="City").order_by(Scene.id).all()
    topics = Scene.query.filter_by(category="Topic").order_by(Scene.id).all()
    return render_template(
        "scenes.html", cities=cities, topics=topics, search_form=form
    )


@main.route("/new/scene", methods=["GET", "POST"])
def new_scene():
    form = SceneForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        if Scene.query.filter(Scene.name == form.name.data).all() == []:
            scene = Scene(
                name=form.name.data,
                category=form.category.data,
                description=form.description.data,
            )
            db.session.add(scene)
            db.session.commit()
            return redirect(url_for(".scenes"))
        else:
            flash("That scene already exists!")
            return redirect(url_for(".new_scene"))
    return render_template("new_scene.html", form=form)
