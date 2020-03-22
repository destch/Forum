from datetime import datetime
from flask import render_template, session, redirect, url_for, jsonify
from . import main
from .forms import PostForm
from .. import db
from ..models import Post, Comment
import json

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@main.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@main.route('/newpost', methods=['GET', 'POST'])
def index():
    name = None
    form = PostForm()
    if form.validate_on_submit():
        #heres where we have to build stuff out
        #find a way to quickly create a new post id if one isnt auto created
        new_post = Post()
        db.session.add(new_post)
        db.session.commit()
        pass
    return render_template('post.html', form=form, name=name)

@main.route('/index_get_data')
def stuff():
    def example():
        query = Post.query.all()
        pre = [r.__dict__ for r in query]
        data = [r.pop('_sa_instance_state', None) for r in pre]
        return(pre)

    data = {
        "data": example()
        }
    return jsonify(data)

@main.route('/scenes')
def scenes():
    return render_template('scenes.html')


"""
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)
"""
