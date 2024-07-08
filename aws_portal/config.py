from datetime import timedelta
import os


class Default:
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'secret')

    CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type', 'X-CSRF-Token']

    JWT_TOKEN_LOCATION = 'headers'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_CSRF_CHECK_FORM = True
    JWT_CSRF_IN_COOKIES = False

    SQLALCHEMY_DATABASE_URI = os.getenv('FLASK_DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Production(Default):
    ENV = 'production'
    DEBUG = False

    CORS_ORIGINS = os.getenv('AWS_CLOUDFRONT_DOMAIN_NAME')

    JWT_COOKIE_SAMESITE = 'None'
    JWT_COOKIE_SECURE = True


class Testing(Default):
    TESTING = True
