from datetime import timedelta
import os


class Default:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'secret')
    DEBUG = os.getenv('FLASK_DEBUG', True)
    LOG_LEVEL = os.getenv('FLASK_LOG_LEVEL', 'INFO')

    JWT_TOKEN_LOCATION = 'cookies'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_CSRF_CHECK_FORM = True

    SQLALCHEMY_DATABASE_URI = os.getenv('FLASK_DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Default):
    ENV = 'development'


class Production(Default):
    ENV = 'production'

    JWT_COOKIE_SAMESITE = 'None'
    JWT_COOKIE_SECURE = True


class Debug(Default):
    DEBUG = True
    LOG_LEVEL = 'INFO'


class Testing(Default):
    ENV = 'development'
    TESTING = True
