from app import db, mail, app
from app import login
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import render_template, flash, redirect, url_for, session
from flask_mail import Mail, Message
import random
from datetime import datetime, timedelta

rel = db.Table('rels',
               db.Column('book_isbn', db.Text, db.ForeignKey('books.isbn')),
               db.Column('user_username', db.Text, db.ForeignKey('user.username')),
               db.Column('from_user', db.Text),
               db.Column('date_to', db.Text)
               )

book_lib_rel = db.Table('book_lib_rel',
               db.Column('book_isbn', db.Text, db.ForeignKey('books.isbn')),
               db.Column('lib_id', db.Text, db.ForeignKey('libraries.id')),
               )

user_lib_rel = db.Table('user_lib_rel',
                db.Column('user_username', db.Text, db.ForeignKey('user.username')),
               db.Column('lib_id', db.Text, db.ForeignKey('libraries.id')),
               )


class Libraries(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, unique=True, primary_key=True)
    name = db.Column(db.Text)
    owner = db.Column(db.Text)
    subscribers = db.relationship('User', secondary=user_lib_rel, backref=db.backref('subscribed_libs', lazy='dynamic'))
    books_in = db.relationship('Books', secondary=book_lib_rel, backref=db.backref('parent_libs', lazy='dynamic'))


class User(UserMixin, db.Model):
    username = db.Column(db.String(64), index=True, unique=True, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    activated = db.Column(db.String(128))
    books = db.relationship('Books', secondary=rel, backref=db.backref('owners', lazy='dynamic'))
    libraries = db.relationship('Libraries', secondary=user_lib_rel, backref=db.backref('subscribers_u', lazy='dynamic'))

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


class Comments(UserMixin, db.Model):
    author_username = db.Column(db.Text)
    related_book = db.Column(db.Text)
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    text_value = db.Column(db.Text)
    date = db.Column(db.Text)


@login.user_loader
def load_user(id):
    return User.query.get(id)


def add_book_db(form, database):
    book = Books(isbn=form.isbn.data,
                 title=form.title.data,
                 author_name=form.author_name.data,
                 author_surname=form.author_surname.data,
                 status='free',
                 img_url=form.img_url.data,
                 description=form.description.data,
                 )
    database.session.add(book)
    database.session.commit()


def add_book_collection_db(isbn_p, username_p, database, date_to=None, from_user=None):
    if User.query.filter_by(username=username_p).first() is not None:
        if isbn_p in [b.isbn for b in User.query.filter_by(username=username_p).first().books]:
            return 0
    user = User.query.filter_by(username=username_p).first()
    book = Books.query.filter_by(isbn=isbn_p).first()
    book.owners.append(user)
    database.session.commit()


    lib = Libraries.query.filter_by(owner=username_p).first()
    book.parent_libs.append(lib)
    database.session.commit()


def remove_book_from_collection_db(isbn_p, username_p, database):
    user = User.query.filter_by(username=username_p).first()
    book = Books.query.filter_by(isbn=isbn_p).first()
    book.owners.remove(user)
    database.session.commit()
    lib = Libraries.query.filter_by(owner=username_p).first()
    book.parent_libs.append(lib)
    database.session.commit()


def view_book_model(lend_form, form, isbn):
    book = Books.query.filter_by(isbn=isbn).first()
    time = lend_form.time.data
    if lend_form.submitL.data and lend_form.validate_on_submit():
        book.status = 'free'
        book.current_owner = lend_form.username.data
        if not lend_form.outside.data and User.query.filter_by(username=lend_form.username.data).first() is None:
            flash("No such user!")
        else:
            if not lend_form.outside.data:
                add_book_collection_db(isbn, lend_form.username.data, db, time, session['username'])
                remove_book_from_collection_db(isbn, session['username'], db)
            else:
                add_book_collection_db(isbn, 'outside', db, time, session['username'])
            db.session.add(book)
            db.session.commit()
            return 'redirect', book
    return 'render', book

def register_model(form):
    user = User(username=form.username.data, email=form.email.data)
    lib = Libraries(name=form.username.data + '\'s Library', owner=form.username.data)
    user.set_password(form.password.data)
    msg = Message('Registration conformation', sender='yourId@gmail.com', recipients=[form.email.data])
    msg.body = "Please click link below to finish registration:"
    token = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    registration = Registrations(username=form.username.data, token=token, date=str(datetime.now()))
    db.session.add(registration)
    msg = Message('Registration confirmation', sender=app.config['ADMINS'][0],
                  recipients=['makaszml@gmail.com'])
    msg.body = 'Click following link to finish registration:  http://127.0.0.1:5000/activate?token=' + token
    msg.html = '<h1>Registration</h1>' \
               '<p>Click following link to finish registration: <a href=http://127.0.0.1:5000/activate?token=' + token + '>Activation link</a></p>'

    mail.connect()
    mail.send(msg)

    mail.send(msg)
    db.session.add(lib)
    db.session.add(user)
    db.session.commit()

    user.libraries.append(lib)
    db.session.commit()

    flash('Congratulations, you are now a registered user!')



