from datetime import datetime
from flask import current_app, request, url_for
from . import db

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    link = db.Column(db.String)
    source = db.Column(db.String(256))
    username = db.Column(db.String(64))
    file_location = db.Column(db.String(256))
    date = db.Column(db.DateTime)
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
