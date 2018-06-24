import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = 'makaszml1@gmail.com'
    MAIL_PASSWORD = 'WitcheR6902'
    ADMINS = ['makaszml1@gmail.com']
