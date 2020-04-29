from flask_admin.contrib.sqla import ModelView
from app import db, admin
from app.models import User, Post, Comment, Scene

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Scene, db.session))
