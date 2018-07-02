from app import app, mail
from flask import render_template, flash, redirect, url_for, session
from flask import g
from app.loginform import LoginForm
from flask_login import LoginManager, logout_user, login_required, current_user, login_user
from app.models import User, Books, add_book_db, add_book_collection_db, Ownership, rel
from flask import request
from werkzeug.urls import url_parse
from app import db, metadata
from app.loginform import RegistrationForm, BookForm, SearchBookForm, LendBookToForm
from flask_mail import Mail, Message


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
    print(metadata.tables.keys())
    books = Books.query.all()
    if request.args.get('value') is not None and len(request.args.get('value')) > 0:
        books = [b for b in books if request.args.get('value').lower() in b.title.lower()]
    form = SearchBookForm()
    return render_template('index2.html', title='All books', books=books, form=form)


@app.route('/add', methods=['POST', 'GET'], endpoint='add_book_to_collection')
@login_required
def add_book_to_collection():
    isbn = request.args.get('isbn')
    add_book_collection_db(isbn, session['username'], db)
    return redirect(url_for('user_homepage'))


@app.route('/collection', methods=['POST', 'GET'], endpoint='user_collection')
@login_required
def user_collection():
    username = session['username']
    user = User.query.filter_by(username=username)
    for u in user:
        print(str(u.books))
        books = u.books
        print(books)
    if request.args.get('value') is not None and len(request.args.get('value')) > 0:
        books = [b for b in books if request.args.get('value').lower() in b.title.lower()]
    form = SearchBookForm()
    return render_template('collection.html', title='Your books', books=books, form=form)


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
        msg = Message('Registration conformation', sender='yourId@gmail.com', recipients=[form.email.data])
        msg.body = "Please click link below to finish registration:"
        mail.send(msg)
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
        add_book_db(form, db)
        return redirect(url_for('user_homepage'))
    return render_template('add_book.html', title='Add book', form=form)


@app.route('/book_details', methods=['GET', 'POST'])
@login_required
def view_book():
    lend_form = LendBookToForm()
    form = SearchBookForm()
    isbn = request.args.get('isbn')
    book = Books.query.filter_by(isbn=isbn).first()
    print(lend_form.username.data,lend_form.time.data, lend_form.submitL.data, lend_form.validate_on_submit())
    print(form.value.data, form.validate_on_submit())
    if lend_form.submitL.data and lend_form.validate_on_submit():
        book.status = lend_form.time.data
        book.current_owner = lend_form.username.data
        print(book)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('user_homepage'))
    return render_template('book_details.html', title='Book Details', lend_form=lend_form, book=book, form=form)