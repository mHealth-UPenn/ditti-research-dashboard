from datetime import timedelta
import os


class Default:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'secret')
    DEBUG = os.getenv('FLASK_DEBUG', True)
    LOG_LEVEL = os.getenv('FLASK_LOG_LEVEL', 'INFO')

    JWT_TOKEN_LOCATION = 'cookies'
    JWT_COOKIE_SAMESITE = 'None'
    JWT_COOKIE_SECURE = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_CSRF_CHECK_FORM = True
    JWT_CSRF_IN_COOKIES = False

    SQLALCHEMY_DATABASE_URI = os.getenv('FLASK_DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Default):
    ENV = 'development'


class Production(Default):
    ENV = 'production'


class Debug(Default):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class Testing(Default):
    ENV = 'development'
    TESTING = True
