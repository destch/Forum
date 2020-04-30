from flask_admin.contrib.sqla import ModelView
from app import db, admin
from app.models import User, Post, Comment, Scene
from flask_login import current_user

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_administrator()


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Post, db.session))
admin.add_view(MyModelView(Comment, db.session))
admin.add_view(MyModelView(Scene, db.session))
