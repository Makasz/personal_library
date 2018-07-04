from app import app, mail
from flask import render_template, flash, redirect, url_for, session
from flask import g
from app.loginform import LoginForm
from flask_login import LoginManager, logout_user, login_required, current_user, login_user
from app.models import User, Books, add_book_db, add_book_collection_db, remove_book_from_collection_db, Registrations, view_book_model, register_model, Comments, Libraries
from flask import request
from werkzeug.urls import url_parse
from app import db, metadata
from app.loginform import RegistrationForm, BookForm, SearchBookForm, LendBookToForm, CommentForm
from flask_mail import Mail, Message
import random
from datetime import datetime, timedelta


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['POST', 'GET'], endpoint='login')
def login():
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
            return redirect(url_for('login'))
        if not user.activated == 'activated':
            flash('User not activated')
            return redirect(url_for('login'))
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
    print(metadata.tables.keys())
    books = Books.query.all()
    if request.args.get('value') is not None and len(request.args.get('value')) > 0:
        if request.args.get('search_type') == 'author':
            books = [b for b in books if request.args.get('value').lower() in b.author_surname.lower() + ' ' + b.author_name.lower()]
        else:
            books = [b for b in books if request.args.get('value').lower() in b.title.lower()]
    form = SearchBookForm()
    return render_template('index2.html', title='All books', books=books, form=form)


@app.route('/add', methods=['POST', 'GET'], endpoint='add_book_to_collection')
@login_required
def add_book_to_collection():
    isbn = request.args.get('isbn')
    add_book_collection_db(isbn, session['username'], db)
    return redirect(url_for('user_homepage'))


@app.route('/remove', methods=['POST', 'GET'], endpoint='remove_book_from_collection')
@login_required
def remove_book_from_collection():
    isbn = request.args.get('isbn')
    remove_book_from_collection_db(isbn, session['username'], db)
    return redirect(url_for('user_collection'))


@app.route('/collection', methods=['POST', 'GET'], endpoint='user_collection')
@login_required
def user_collection():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    lib = Libraries.query.filter_by(owner=username).first()
    print(list(lib.books_in))
    books = lib.books_in
    if request.args.get('value') is not None and len(request.args.get('value')) > 0:
        if request.args.get('search_type') == 'author':
            books = [b for b in books if request.args.get('value').lower() in b.author_surname.lower() + ' ' + b.author_name.lower()]
        else:
            books = [b for b in books if request.args.get('value').lower() in b.title.lower()]
    form = SearchBookForm()
    return render_template('collection.html', title='Your books', books=books, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_homepage'))
    form = RegistrationForm()
    if form.validate_on_submit():
        register_model(form)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    print(form)
    print(form.is_submitted())
    if form.validate_on_submit():
        add_book_db(form, db)
        return redirect(url_for('user_homepage'))
    return render_template('add_book.html', title='Add book', form=form)


@app.route('/book_details', methods=['GET', 'POST'])
@login_required
def view_book():
    lend_form = LendBookToForm()
    form = SearchBookForm()
    comment_form = CommentForm()
    isbn = request.args.get('isbn')
    res = view_book_model(lend_form, form, isbn)
    comments = Comments.query.filter_by(related_book=isbn)
    if res[0] == 'redirect':
        return redirect(url_for('user_collection'))
    else:
        return render_template('book_details.html', title='Book Details', lend_form=lend_form, book=res[1], form=form, comments=comments, comment_form=comment_form)


@app.route('/book_details_unowned', methods=['GET', 'POST'])
@login_required
def view_book_unowned():
    form = SearchBookForm()
    isbn = request.args.get('isbn')
    book = Books.query.filter_by(isbn=isbn).first()
    print(form.value.data, form.validate_on_submit())
    return render_template('book_details_unowned.html', title='Book Details', form=form, book=book)

@app.route('/activate', methods=['GET', 'POST'])
def activate():
    token = request.args.get('token')
    registration = Registrations.query.filter_by(token=token).first()
    yesterday = datetime.now() - timedelta(days=1)
    print(registration.date, yesterday)
    if registration is not None and datetime.strptime(registration.date, "%Y-%m-%d %H:%M:%S.%f") > yesterday:
        user = User.query.filter_by(username=registration.username).first()
        user.activated = 'activated'
        db.session.commit()
        return redirect(url_for('login'))
    return redirect(url_for('login'))


