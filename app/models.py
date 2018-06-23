from app import db
from app import login
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    username = db.Column(db.String(64), index=True, unique=True, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User: {} Password: {} Email: {}>'.format(self.username, self.password_hash, self.email)

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password


class Books(UserMixin, db.Model):
    isbn = db.Column(db.Text, index=True, unique=True, primary_key=True)
    title = db.Column(db.Text)
    author_name = db.Column(db.Text)
    author_surname = db.Column(db.Text)
    owner = db.Column(db.Text)
    status = db.Column(db.Text)
    current_owner = db.Column(db.Text)
    img_url = db.Column(db.Text)
    description = db.Column(db.Text)

    def __repr__(self):
        return '<ISBN: {} Title: {} Owner: {}>'.format(self.isbn, self.title, self.owner)


@login.user_loader
def load_user(id):
    return User.query.get(id)
