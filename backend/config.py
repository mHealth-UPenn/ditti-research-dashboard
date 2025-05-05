# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
from typing import ClassVar


class Default:
    """
    Default configuration for development environment.

    Contains base configuration settings used across all environments.
    """

    ENV = "development"
    DEBUG = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "secret")

    CORS_ALLOW_HEADERS: ClassVar[list[str]] = [
        "Authorization",
        "Content-Type",
        "X-CSRF-TOKEN",
    ]

    # Headers for the client to access when downloading Excel files
    CORS_EXPOSE_HEADERS: ClassVar[list[str]] = [
        "Content-Type",
        "Content-Disposition",
    ]
    CORS_SUPPORTS_CREDENTIALS = True

    SQLALCHEMY_DATABASE_URI = os.getenv("FLASK_DB")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_SYNC_HOST = os.getenv("APP_SYNC_HOST")
    AWS_TABLENAME_USER = os.getenv("AWS_TABLENAME_USER")
    AWS_TABLENAME_TAP = os.getenv("AWS_TABLENAME_TAP")
    AWS_TABLENAME_AUDIO_FILE = os.getenv("AWS_TABLENAME_AUDIO_FILE")
    AWS_TABLENAME_AUDIO_TAP = os.getenv("AWS_TABLENAME_AUDIO_TAP")
    AWS_AUDIO_FILE_BUCKET = os.getenv("AWS_AUDIO_FILE_BUCKET")

    COGNITO_PARTICIPANT_CLIENT_ID = os.environ.get(
        "COGNITO_PARTICIPANT_CLIENT_ID"
    )
    COGNITO_PARTICIPANT_CLIENT_SECRET = os.environ.get(
        "COGNITO_PARTICIPANT_CLIENT_SECRET"
    )

    API_AUTHORIZE_REDIRECT = "http://localhost:3000"
    FITBIT_CLIENT_ID = os.environ.get("FITBIT_CLIENT_ID")
    FITBIT_CLIENT_SECRET = os.environ.get("FITBIT_CLIENT_SECRET")
    FITBIT_REDIRECT_URI = "http://localhost:5000/api/fitbit/callback"

    COGNITO_PARTICIPANT_DOMAIN = os.getenv("COGNITO_PARTICIPANT_DOMAIN")
    COGNITO_PARTICIPANT_REGION = os.getenv("COGNITO_PARTICIPANT_REGION")
    COGNITO_PARTICIPANT_REDIRECT_URI = (
        "http://localhost:5000/auth/participant/callback"
    )
    COGNITO_PARTICIPANT_LOGOUT_URI = "http://localhost:3000/login"
    COGNITO_PARTICIPANT_USER_POOL_ID = os.getenv(
        "COGNITO_PARTICIPANT_USER_POOL_ID"
    )

    COGNITO_RESEARCHER_CLIENT_ID = os.environ.get("COGNITO_RESEARCHER_CLIENT_ID")
    COGNITO_RESEARCHER_CLIENT_SECRET = os.environ.get(
        "COGNITO_RESEARCHER_CLIENT_SECRET"
    )
    COGNITO_RESEARCHER_DOMAIN = os.getenv("COGNITO_RESEARCHER_DOMAIN")
    COGNITO_RESEARCHER_REGION = os.getenv("COGNITO_RESEARCHER_REGION")
    COGNITO_RESEARCHER_USER_POOL_ID = os.getenv("COGNITO_RESEARCHER_USER_POOL_ID")
    COGNITO_RESEARCHER_REDIRECT_URI = (
        "http://localhost:5000/auth/researcher/callback"
    )
    COGNITO_RESEARCHER_LOGOUT_URI = "http://localhost:3000/coordinator/login"

    TM_FSTRING = os.getenv("TM_FSTRING")

    # AWS Lambda configuration
    LAMBDA_FUNCTION_NAME = os.environ.get("LAMBDA_FUNCTION_NAME")

    # AWS SigV4 configuration
    LAMBDA_ACCESS_KEY_ID = os.environ.get("LAMBDA_ACCESS_KEY_ID")
    LAMBDA_SECRET_ACCESS_KEY = os.environ.get("LAMBDA_SECRET_ACCESS_KEY")
    LAMBDA_AWS_REGION = os.environ.get("LAMBDA_AWS_REGION", "us-east-1")

    # Configuration for invoking a lambda function locally
    LOCAL_LAMBDA_ENDPOINT = os.environ.get("LOCAL_LAMBDA_ENDPOINT")


class Staging(Default):
    """
    Staging environment configuration.

    Configuration for the staging environment with production-like settings
    but separate from the actual production environment.
    """

    ENV = "production"
    DEBUG = False

    CORS_ALLOW_HEADERS: ClassVar[list[str]] = [
        "Content-Type",
        "X-Amz-Date",
        "Authorization",
        "X-Api-Key",
        "X-Amz-Security-Token",
        "X-CSRF-TOKEN",
    ]


class Production(Default):
    """
    Production environment configuration.

    Configuration for the live production environment with secure settings.
    """

    ENV = "production"
    DEBUG = False

    CORS_ALLOW_HEADERS: ClassVar[list[str]] = [
        "Content-Type",
        "X-Amz-Date",
        "Authorization",
        "X-Api-Key",
        "X-Amz-Security-Token",
        "X-CSRF-TOKEN",
    ]

    CORS_ORIGINS = os.getenv("AWS_CLOUDFRONT_DOMAIN_NAME")

    COGNITO_PARTICIPANT_USER_POOL_ID = os.environ.get(
        "COGNITO_PARTICIPANT_USER_POOL_ID"
    )
    COGNITO_PARTICIPANT_REDIRECT_URI = os.environ.get(
        "COGNITO_PARTICIPANT_REDIRECT_URI"
    )
    COGNITO_PARTICIPANT_LOGOUT_URI = os.environ.get(
        "COGNITO_PARTICIPANT_LOGOUT_URI"
    )
    COGNITO_PARTICIPANT_DOMAIN = os.environ.get("COGNITO_PARTICIPANT_DOMAIN")
    COGNITO_PARTICIPANT_REGION = os.environ.get("COGNITO_PARTICIPANT_REGION")

    FITBIT_REDIRECT_URI = os.environ.get("FITBIT_REDIRECT_URI")

    API_AUTHORIZE_REDIRECT = os.environ.get("API_AUTHORIZE_REDIRECT")

    TM_FSTRING = "{api_name}-tokens"

    # Researcher Cognito Production configuration
    COGNITO_RESEARCHER_USER_POOL_ID = os.environ.get(
        "COGNITO_RESEARCHER_USER_POOL_ID"
    )
    COGNITO_RESEARCHER_REDIRECT_URI = os.environ.get(
        "COGNITO_RESEARCHER_REDIRECT_URI"
    )
    COGNITO_RESEARCHER_LOGOUT_URI = os.environ.get(
        "COGNITO_RESEARCHER_LOGOUT_URI"
    )
    COGNITO_RESEARCHER_DOMAIN = os.environ.get("COGNITO_RESEARCHER_DOMAIN")
    COGNITO_RESEARCHER_REGION = os.environ.get("COGNITO_RESEARCHER_REGION")


class Testing(Default):
    """
    Testing environment configuration.

    Configuration specifically designed for running automated tests.
    """

    ENV = "testing"
    TESTING = True

    CORS_ORIGINS = "http://localhost:3000"

    TM_FSTRING = "{api_name}-tokens-testing"
