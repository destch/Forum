import sqlalchemy as db
#db section
engine = db.create_engine('sqlite:///posts.db',
connect_args={'check_same_thread': False})
connection = engine.connect()
metadata = db.MetaData()
posts = db.Table('RA', metadata, autoload=True, autoload_with=engine)

posts.query.filter(posts.post_id == 1).post_id
cur = posts.select().where(posts.c.post_id == 1)
res = connection.execute(cur)
for row in res:
    print(row)
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model)
    __tablename__ = 'posts'
    id = db.Column(db.integer, primary_key=True)
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

    def __repr__(self):
        return ('<Title %r>' % self.title)

class Comment(db.Model)
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.string(64), unique=True, index=True)
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)
    votes = db.Column(db.Integer)
    file_location = db.Column(db.String(256))

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return '<User %r>' % self.username
