from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post
from random import randint


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(
            email=fake.email(),
            username=fake.user_name(),
            password="password",
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.past_date(),
        )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        thread_int = randint(0, 1)
        p = Post(
            body=fake.text(),
            title=fake.text()[:30],
            type=["thread", "link"][thread_int],
            link="www.link.com" if thread_int == 0 else None,
            scene_id=randint(1, 3),
            timestamp=fake.past_date(),
            author=u,
        )
        db.session.add(p)
        db.session.commit()
