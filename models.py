import datetime
import os
import urllib.parse
import smtplib
from peewee import *
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from email.mime.text import MIMEText

DB = Proxy()

class User(UserMixin, Model):
    username = CharField(max_length=10, unique=True)
    email = TextField(unique=True)
    first_name = TextField()
    last_name = TextField()
    password = TextField()
    avatar = TextField(default='data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBw0PDRANDQ0PDQ0NDQ0PDQ0NDw8ODg0NFRIWFhURExYYHTQgGBolGxUVLTEhJS03LjouFyAzODUsNygtLisBCgoKBQUFDgUFDisZExkrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrK//AABEIAKAAoAMBIgACEQEDEQH/xAAbAAEAAgMBAQAAAAAAAAAAAAAAAgMBBQYHBP/EADIQAAMAAQEGAwYFBQEAAAAAAAABAgMRBAUGITFBElFSImFxgZGxEzJicqEjNELB0TP/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8A9ZAAAAAADIGDI0MpAYB821bxwYuV5JT9K9qvojXZOJsK/LjyX73pIG6Boo4nxa88NpeaqaNlse9MGblF+16K9mvl5gfWYJaGNAMAyYAAAAAAAAAGQABnQykSSA+TeG2xgjx3z7TK62/JHJbdvjPm1TpxHohtL5vuS4g2t5dopf44tYlfDq/r9jWgAAAAAG72PiPLEqckLLpy8TpzTXv5czo9h2uM2NZI6Pk0+s0uqZwJv+EM7WTJib5XCpL9Uv8A4/4A6bQwTaItARBkwAAAAAyAJJGETSAJE1y5+XMJFinXl58gPMXWrbfVtt/FmDLWnLum0/kYAAAAAABt+Fv7uf2X9jUG94PjXam/Tit/ykB1rRBovaK2gKmjBNoi0BEGTAAkjBlASSJyiKRZKAlKLJRiUSttTTXVTTXxSA833viUbTmldFlvT5vX/Z8hmrdN1T1qm6p+bfNmAAAAAAAdDwU1+PkXd4eXv0panPH07t2l4s+PIn+W5198t6NfQD0ikV0i+kV0gKKRBotpFbAgzBJkQMokjCJSBOSyUQktkCcomlry8+RiSaA8puHLcvrLcv4p6EToOJdy5pz3lx46vFkbtuFr4K7po58AAAAAAF2x4/Hmxwv8skL60ik6bhTcuX8Wdoyw4xwtcark7p9Hp5AdhRXSLWV0BTSK6LaRXQFbIkmRAyickETkCyS2SuSyQLJLEQkmgDWq08zydzo2vJtfQ9ZPM99bJeHackUtNbq4faobbTQHwgAAAAPr3TiV7ThilqqyxqvNa66Hp7OD4Q3fWTaFm00x4dW3521ylfU7wCLK6LGQoCmiui2iqgK2QZNkWAROSCJyBbJbJTJbIFsk0QkmgMnC8Vb3jPX4U4//AByUlm8Wrrs0lp01+x0XEm9ls+FzL/rZE1CXWV3p/A89AAAAAAOo4c4gjHOLZaxeFOtPxVfLxU+rWn+zsjyVnoXDe9ltGFTVf1saStPrS7WviBtmQomyugK6KqLaKqAroiyTIMDKJIgj59q3lgxcsmRJ+le1X0QH3yTvLMT4rpTK61TSRym2cUV0wY/D+vJzfynsaLadpyZa8WW6t9vE+S+C7Addt3FeGOWGXmr1flhfPqzntt37teXrlcT6cXsL+OZrAA9/d9X5gAAAAAAAD3910fkABsti37tWHpldz6cvtr+eZ0Ow8VYb5ZpeGvUvah/PqjjAB6ZGWbnxRSqX0qWmiNHnezbTkxPxYrqH38L5P4rubzY+KK6Z8fi/Xj5P5yB0jIs+bZd5YMvLHkTfpfs19GfSwOX33vi6usWKnMS3NVL52+/PsjRksn5q/dX3IgAAAAAAAAAAAAAAAAAAAAAA3m5N8XNTiy14opqZqnzh9ufdGjJY/wA0/un7gYfUwAAAAAAAAAAAAAAAAAAAAAAADK6mAB//2Q==')
    joined_at = DateTimeField(default=datetime.datetime.now)
    bio = TextField(default='This person has not set a bio yet. Shame on that person.')
    default_view = CharField(default='following')

    @classmethod
    def create_user(cls, username, email, first_name, last_name, password):
        user = cls.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=generate_password_hash(password)
        )
        user.sendmail_to('You have now registered with Thunder Dynamics Internal Communication (TDIC)')

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

    def sendmail_to(self, msg_text):
        smtp = smtplib.SMTP_SSL('smtp.gmail.com')
        smtp.login('thethunderdynamics@gmail.com', 'Driselamri07')
        msg = MIMEText(msg_text + '\n\n\nSincerely,\nTDIC Admin')
        msg['Subject'] = 'Thunder Dynamics Internal Communication Sign Up'
        msg['From'] = 'Thunder Dynamics Internal Communication'
        msg['To'] = self.email
        smtp.sendmail('thethunderdynamics@gmail.com', self.email, msg.as_string())

    class Meta:
        database = DB
        order_by = ('-joined_at',)


class Post(Model):
    user = ForeignKeyField(User, related_name='posts')
    data = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    def get_comments(self):
        Comment.select().where(Comment.post == self)

    class Meta:
        database = DB
        order_by = ('-created_at',)

class Comment(Model):
    user = ForeignKeyField(User, related_name='user_comments')
    post = ForeignKeyField(Post, related_name='comments')
    data = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
        order_by = ('-created_at',)


class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relations')
    to_user = ForeignKeyField(User, related_name='relations_to')

    class Meta:
        database = DB


if 'HEROKU' in os.environ:
    urllib.parse.uses_netloc.append('postgres')
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    db_sql = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
    DB.initialize(db_sql)
else:
    db_sql = SqliteDatabase('DB')
    DB.initialize(db_sql)

DB.connect()
DB.create_tables([User, Post, Comment, Relationship], safe=True)

if __name__ == '__main__':
    post_id = int(input('Post id to delete: '))
    Post.get(Post.id==post_id).delete_instance()
