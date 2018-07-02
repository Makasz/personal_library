import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # MAIL_USE_SSL = True
    # MAIL_PORT = 465
    MAIL_USERNAME = 'haraldsilnonogi@gmail.com'
    MAIL_PASSWORD = 'marcepan1'
    ADMINS = ['haraldsilnonogi@gmail.com']
    # SQLALCHEMY_ECHO = True
    # EMAIL_USE_TLS = True
    # EMAIL_HOST = 'smtp.gmail.com'
    # EMAIL_HOST_USER = 'haraldsilnonogi@gmail.com'
    # EMAIL_HOST_PASSWORD = 'marcepan1'
    # EMAIL_PORT = 587