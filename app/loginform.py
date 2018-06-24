from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class BookForm(FlaskForm):
    isbn = StringField('ISBN', validators=[DataRequired()])
    title = StringField('Title')
    author_name = StringField('Author\'s Name')
    author_surname = StringField('Author\'s Surname')
    owner = StringField('Owner')
    status = StringField('Status')
    current_owner = StringField('Current Owner')
    img_url = StringField('Link to cover image')
    description = StringField('Description')
    submit = SubmitField('Add')


class SearchBookForm(FlaskForm):
    value = StringField('Value')


class LendBookToForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    submitL = SubmitField('Lend')
