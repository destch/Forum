from datetime import datetime
from flask import current_app, request, url_for
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' %self.name

    users = db.relationship('User', backref='role', lazy='dynamic')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    link = db.Column(db.String)
    source = db.Column(db.String(256))
    username = db.Column(db.String(64))
    file_location = db.Column(db.String(256))
    date = db.Column(db.DateTime, default = datetime.utcnow)
    replies = db.Column(db.Integer)
    votes = db.Column(db.Integer)

    comments = db.relationship('Comment', backref='post', lazy = 'dynamic')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)
    votes = db.Column(db.Integer)
    file_location = db.Column(db.String(256))

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))



