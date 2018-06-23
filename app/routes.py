from app import app
from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
from flask import g
from config_default import Config
from app.loginform import LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user, login_required, current_user, login_user
from app.models import User, Books
from werkzeug.security import generate_password_hash
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.loginform import RegistrationForm, BookForm, SearchBookForm


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['POST', 'GET'], endpoint='login_m')
def login_m():
    if current_user.is_authenticated:
        print(current_user)
        print("User logged" + str(current_user))
        return redirect(url_for('user_homepage', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login_m'))
        login_user(user)
        session['username'] = form.username.data
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user_homepage')
        return redirect(next_page)
    return render_template('index.html', title='Sign In', form=form)


@app.route('/index2', methods=['POST', 'GET'], endpoint='user_homepage')
@login_required
def user_homepage():
    username = session['username']
    books = Books.query.filter_by(owner=username)

    if request.args.get('value') is not None and len(request.args.get('value')) > 0:
        books = [b for b in books if request.args.get('value').lower() in b.title.lower()]
    form = SearchBookForm()
    return render_template('index2.html', title='Test Page', books=books, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_m'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_homepage'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login_m'))
    return render_template('register.html', title='Register', form=form)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    print(form)
    print(form.is_submitted())
    if form.validate_on_submit():
        book = Books(isbn=form.isbn.data,
                     title=form.title.data,
                     author_name=form.author_name.data,
                     author_surname=form.author_surname.data,
                     owner=form.owner.data,
                     status=form.status.data,
                     current_owner=form.current_owner.data,
                     img_url=form.img_url.data,
                     description=form.description.data,
                     )
        db.session.add(book)
        db.session.commit()
        flash('Congratulations, you added new book to collection!')
        return redirect(url_for('user_homepage'))
    return render_template('add_book.html', title='Add book', form=form)