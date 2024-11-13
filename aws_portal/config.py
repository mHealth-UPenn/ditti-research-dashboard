from datetime import timedelta
import os


class Default:
    ENV = "development"
    DEBUG = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "secret")

    CORS_ALLOW_HEADERS = ["Authorization", "Content-Type", "X-CSRF-TOKEN"]
    CORS_SUPPORTS_CREDENTIALS = True

    JWT_TOKEN_LOCATION = "headers"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_CSRF_CHECK_FORM = True
    JWT_CSRF_IN_COOKIES = False
    JWT_ACCESS_CSRF_HEADER_NAME = "X-Csrf-Token"

    SQLALCHEMY_DATABASE_URI = os.getenv("FLASK_DB")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_SYNC_HOST = os.getenv("APP_SYNC_HOST")
    AWS_TABLENAME_USER = os.getenv("AWS_TABLENAME_USER")
    AWS_TABLENAME_TAP = os.getenv("AWS_TABLENAME_TAP")
    AWS_TABLENAME_AUDIO_FILE = os.getenv("AWS_TABLENAME_AUDIO_FILE")
    AWS_TABLENAME_AUDIO_TAP = os.getenv("AWS_TABLENAME_AUDIO_TAP")
    AWS_AUDIO_FILE_BUCKET = os.getenv("AWS_AUDIO_FILE_BUCKET")

    COGNITO_PARTICIPANT_CLIENT_ID = os.environ.get(
        "COGNITO_PARTICIPANT_CLIENT_ID")
    COGNITO_PARTICIPANT_CLIENT_SECRET = os.environ.get(
        "COGNITO_PARTICIPANT_CLIENT_SECRET")
    COGNITO_PARTICIPANT_DOMAIN = "penn-ditti-dev-rev2.auth.us-east-1.amazoncognito.com"
    COGNITO_PARTICIPANT_REGION = "us-east-1"
    COGNITO_PARTICIPANT_REDIRECT_URI = "http://localhost:5000/cognito/callback"
    COGNITO_PARTICIPANT_LOGOUT_URI = "http://localhost:3000/login"
    COGNITO_PARTICIPANT_USER_POOL_ID = "us-east-1_yz8n85tm1"

    API_AUTHORIZE_REDIRECT = "http://localhost:3000"
    FITBIT_CLIENT_ID = os.environ.get("FITBIT_CLIENT_ID")
    FITBIT_CLIENT_SECRET = os.environ.get("FITBIT_CLIENT_SECRET")
    FITBIT_REDIRECT_URI = "http://localhost:5000/cognito/fitbit/callback"


class Production(Default):
    ENV = "production"
    DEBUG = False

    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "X-Amz-Date",
        "Authorization",
        "X-Api-Key",
        "X-Amz-Security-Token",
        "X-CSRF-TOKEN"
    ]

    CORS_ORIGINS = os.getenv("AWS_CLOUDFRONT_DOMAIN_NAME")


class Testing(Default):
    TESTING = True
    CORS_ORIGINS = "http://localhost:3000"
