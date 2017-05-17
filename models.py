import datetime
import os
import ast
from urllib.parse import urlparse, uses_netloc
import smtplib
from peewee import *
from peewee import transaction
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from email.mime.text import MIMEText

DB = Proxy()


class ListField(Field):
    db_field = 'list'

    def db_value(self, value):
        return str(value)

    def python_value(self, value):
        return ast.literal_eval(value)


class User(UserMixin, Model):
    username = CharField(max_length=10, unique=True)
    email = TextField(unique=True)
    first_name = TextField()
    last_name = TextField()
    password = TextField()
    avatar = TextField(default='data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBw0PDRANDQ0PDQ0NDQ0PDQ0NDw8O'
                               'Dg0NFRIWFhURExYYHTQgGBolGxUVLTEhJS03LjouFyAzODUsNygtLisBCgoKBQUFDgUFDisZExkrKysrKysrKys'
                               'rKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrK//AABEIAKAAoAMBIgACEQEDEQH/xAAbAA'
                               'EAAgMBAQAAAAAAAAAAAAAAAgMBBQYHBP/EADIQAAMAAQEGAwYFBQEAAAAAAAABAgMRBAUGITFBElFSImFxgZGxE'
                               'zJicqEjNELB0TP/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMR'
                               'AD8A9ZAAAAAADIGDI0MpAYB821bxwYuV5JT9K9qvojXZOJsK/LjyX73pIG6Boo4nxa88NpeaqaNlse9MGblF+16'
                               'K9mvl5gfWYJaGNAMAyYAAAAAAAAAGQABnQykSSA+TeG2xgjx3z7TK62/JHJbdvjPm1TpxHohtL5vuS4g2t5dopf'
                               '44tYlfDq/r9jWgAAAAAG72PiPLEqckLLpy8TpzTXv5czo9h2uM2NZI6Pk0+s0uqZwJv+EM7WTJib5XCpL9Uv8A4'
                               '/4A6bQwTaItARBkwAAAAAyAJJGETSAJE1y5+XMJFinXl58gPMXWrbfVtt/FmDLWnLum0/kYAAAAAABt+Fv7uf2X'
                               '9jUG94PjXam/Tit/ykB1rRBovaK2gKmjBNoi0BEGTAAkjBlASSJyiKRZKAlKLJRiUSttTTXVTTXxSA833viUbTm'
                               'ldFlvT5vX/Z8hmrdN1T1qm6p+bfNmAAAAAAAdDwU1+PkXd4eXv0panPH07t2l4s+PIn+W5198t6NfQD0ikV0i+k'
                               'V0gKKRBotpFbAgzBJkQMokjCJSBOSyUQktkCcomlry8+RiSaA8puHLcvrLcv4p6EToOJdy5pz3lx46vFkbtuFr4'
                               'K7po58AAAAAAF2x4/Hmxwv8skL60ik6bhTcuX8Wdoyw4xwtcark7p9Hp5AdhRXSLWV0BTSK6LaRXQFbIkmRAyic'
                               'kETkCyS2SuSyQLJLEQkmgDWq08zydzo2vJtfQ9ZPM99bJeHackUtNbq4faobbTQHwgAAAAPr3TiV7Thilqqyxqv'
                               'Na66Hp7OD4Q3fWTaFm00x4dW3521ylfU7wCLK6LGQoCmiui2iqgK2QZNkWAROSCJyBbJbJTJbIFsk0QkmgMnC8V'
                               'b3jPX4U4//AByUlm8Wrrs0lp01+x0XEm9ls+FzL/rZE1CXWV3p/A89AAAAAAOo4c4gjHOLZaxeFOtPxVfLxU+rW'
                               'n+zsjyVnoXDe9ltGFTVf1saStPrS7WviBtmQomyugK6KqLaKqAroiyTIMDKJIgj59q3lgxcsmRJ+le1X0QH3yTv'
                               'LMT4rpTK61TSRym2cUV0wY/D+vJzfynsaLadpyZa8WW6t9vE+S+C7Addt3FeGOWGXmr1flhfPqzntt37teXrlcT'
                               '6cXsL+OZrAA9/d9X5gAAAAAAAD3910fkABsti37tWHpldz6cvtr+eZ0Ow8VYb5ZpeGvUvah/PqjjAB6ZGWbnxRS'
                               'qX0qWmiNHnezbTkxPxYrqH38L5P4rubzY+KK6Z8fi/Xj5P5yB0jIs+bZd5YMvLHkTfpfs19GfSwOX33vi6usWKn'
                               'MS3NVL52+/PsjRksn5q/dX3IgAAAAAAAAAAAAAAAAAAAAAA3m5N8XNTiy14opqZqnzh9ufdGjJY/wA0/un7gYfU'
                               'wAAAAAAAAAAAAAAAAAAAAAAADK6mAB//2Q==')
    joined_at = DateTimeField(default=datetime.datetime.now)
    bio = TextField(default='This person has not set a bio yet. Shame on that person.')
    email_enabled = CharField(default='email')

    def __str__(self):
        return self.username

    @classmethod
    def create_user(cls, username, email, first_name, last_name, password):
        user = cls.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=generate_password_hash(password)
        )
        user.sendmail_to(subject="Signup",
                         msg_text='You have now registered with Thunder Dynamics Internal Communication (TDIC)')

    def following(self):
        return User.select().join(Relationship, on=Relationship.to_user).where(Relationship.from_user == self)

    def followers(self):
        return User.select().join(Relationship, on=Relationship.from_user).where(Relationship.to_user == self)

    def get_following(self):
        return Post.select().where(
            (Post.user << self.following()) |
            (Post.user == self)
        )

    def get_followers(self):
        return Post.select().where(
            (Post.user << self.followers()) |
            (Post.user == self)
        )

    def sendmail_to(self, subject, msg_text, name="TDIC", link=None):
        if 'HEROKU' in os.environ:
            if self.email_enabled != 'noemail':
                print(name)
                smtp = smtplib.SMTP_SSL('smtp.gmail.com')
                smtp.login('thethunderdynamics@gmail.com', os.environ['email_pass'])
                msg = MIMEText(msg_text + '\n\n\nSincerely,\nTDIC Admin')
                if link:
                    link = 'https://td-ic.herokuapp.com' + link
                    link_text = " <a href='{}'>See here</a>".format(link)
                    msg = MIMEText(msg_text + '<br>' + link_text + '<br><br><br>Sincerely,<br>TDIC Admin', 'html')
                msg['Subject'] = subject
                msg['From'] = name
                msg['To'] = self.email
                smtp.sendmail('thethunderdynamics@gmail.com', self.email, msg.as_string())

    class Meta:
        database = DB
        order_by = ('-joined_at',)


class Post(Model):
    user = ForeignKeyField(User, related_name='posts')
    data = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)
    image = TextField(null=True)
    likes = ListField(default=[])
    dislikes = ListField(default=[])

    def get_comments(self):
        Comment.select().where(Comment.post == self)

    def __str__(self):
        return str(self.id)

    class Meta:
        database = DB
        order_by = ('-created_at',)


class Comment(Model):
    user = ForeignKeyField(User, related_name='user_comments')
    post = ForeignKeyField(Post, related_name='comments')
    data = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        database = DB
        order_by = ('-created_at',)


class Relationship(Model):
    def __str__(self):
        return '{} to {}'.format(self.from_user.username, self.to_user.username)
    from_user = ForeignKeyField(User, related_name='relations')
    to_user = ForeignKeyField(User, related_name='relations_to')

    class Meta:
        database = DB


if 'HEROKU' in os.environ:
    uses_netloc.append('postgres')
    url = urlparse(os.environ["DATABASE_URL"])
    db_sql = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, 
                                port=url.port, fields={'list': 'text'})
    PostgresqlDatabase.register_fields({'list': 'text'})
    DB.initialize(db_sql)
    transaction(DB).rollback()
else:
    db_sql = SqliteDatabase('DB', fields={'list': 'list'})
    SqliteDatabase.register_fields({'list': 'list'})
    DB.initialize(db_sql)


def del_user(username):
    del_posts_for_user(username)
    del_comments_for_user(username)
    del_relationships_for_user(username)

    user = User.get(User.username == username)
    user.delete_instance()


def del_posts_for_user(username):
    for post in Post.select():
        if post.user.username == username:
            for comment in Comment.select():
                if comment.post == post:
                    comment.delete_instance()
            post.delete_instance()


def del_comments_for_user(username):
    for comment in Comment.select():
        if comment.user.username == username:
            comment.delete_instance()


def del_relationships_for_user(username):
    for rel in Relationship.select():
        if rel.to_user.username == username or rel.from_user.username == username:
            rel.delete_instance()


def del_post():
    post_id = int(input('Post id to delete: '))
    Post.get(Post.id == post_id).delete_instance()

DB.connect()
DB.create_tables([User, Post, Comment, Relationship], safe=True)
