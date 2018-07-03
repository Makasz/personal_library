from app import db
from app import login
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

rel = db.Table('rels',
               db.Column('book_isbn', db.Text, db.ForeignKey('books.isbn')),
               db.Column('user_username', db.Text, db.ForeignKey('user.username'))
               )

class User(UserMixin, db.Model):
    username = db.Column(db.String(64), index=True, unique=True, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    activated = db.Column(db.String(128))
    books = db.relationship('Books', secondary=rel, backref=db.backref('owners', lazy='dynamic'))

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
    ownership = db.relationship('Ownership', lazy='dynamic')

    def __repr__(self):
        return '<ISBN: {} Title: {} Owner: {}>'.format(self.isbn, self.title, self.owner)


class Ownership(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True)
    isbn = db.Column(db.Text, db.ForeignKey('books.isbn'))
    username = db.Column(db.Text, db.ForeignKey('user.username'))

    def __repr__(self):
        return '<ISBN: {} Username: {}'.format(self.isbn, self.username)


class Registrations(UserMixin, db.Model):
    token = db.Column(db.Text, unique=True, primary_key=True)
    username = db.Column(db.Text)
    date = db.Column(db.Text)

    def __repr__(self):
        return '<Token: {} Username: {} Date: {}>'.format(self.token, self.username, self.date)


@login.user_loader
def load_user(id):
    return User.query.get(id)


def add_book_db(form, database):
    book = Books(isbn=form.isbn.data,
                 title=form.title.data,
                 author_name=form.author_name.data,
                 author_surname=form.author_surname.data,
                 status=form.status.data,
                 img_url=form.img_url.data,
                 description=form.description.data,
                 )
    database.session.add(book)
    database.session.commit()


def add_book_collection_db(isbn_p, username_p, database):
    if isbn_p in [b.isbn for b in User.query.filter_by(username=username_p).first().books]:
        return 0
    user = User.query.filter_by(username=username_p).first()
    book = Books.query.filter_by(isbn=isbn_p).first()
    book.owners.append(user)
    database.session.commit()


def remove_book_from_collection_db(isbn_p, username_p, database):
    user = User.query.filter_by(username=username_p).first()
    book = Books.query.filter_by(isbn=isbn_p).first()
    book.owners.remove(user)
    database.session.commit()
