# Disable linter warnings for print statements (quick fix for logging issues with alembic)
# ruff: noqa: T201

import json
import os
from functools import partial

import boto3
import cfnresponse
from db_uri import DbUri
from flask import Flask
from flask_migrate import upgrade
from load_data import load_data
from sqlalchemy import text

from backend.extensions import db, migrate

# It is safe to use /tmp because the lambda function is ephemeral
DATA_FILE = "/tmp/data.json"  # noqa: S108

LOCAL_DB = os.getenv("LOCAL_DB", "false").lower() == "true"
if LOCAL_DB:
    print("Using local database! IAM authentication is disabled.")


def create_app(db_uri: DbUri, use_iam: bool = False) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri.uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app, use_iam=use_iam)
    migrate.init_app(app, db)

    return app


def get_secret(secret_arn: str) -> dict:
    try:
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_arn)
        return json.loads(response["SecretString"])
    except Exception as e:
        print(f"Error getting secret: {e}")
        raise


def save_datafile(data_arn: str) -> str:
    try:
        client = boto3.client("s3")
        bucket, key = data_arn.split(":")[-1].split("/")
        client.download_file(
            Bucket=bucket,
            Key=key,
            Filename=DATA_FILE,
        )
    except Exception as e:
        print(f"Error saving data file: {e}")
        raise

    return DATA_FILE


def setup_iam_database_user(app: Flask, iam_username: str) -> None:
    """
    Set up a database user for IAM authentication using master credentials.

    Args
    ----
        app: The Flask application with configured database
        iam_username: The username to create for IAM authentication
    """
    try:
        with app.app_context():
            # Use Flask-SQLAlchemy db instance to get the connection
            connection = db.engine.connect()

            try:
                # Check if user already exists
                result = connection.execute(
                    text("SELECT 1 FROM pg_roles WHERE rolname = :username"),
                    {"username": iam_username},
                )

                if result.fetchone():
                    print(
                        f"User {iam_username} already exists, updating IAM permissions"
                    )
                    # Grant IAM role to existing user
                    connection.execute(text(f"GRANT rds_iam TO {iam_username}"))
                else:
                    print(
                        f"Creating new user {iam_username} with IAM authentication"
                    )
                    # Create new user with IAM authentication
                    connection.execute(
                        text(f"CREATE USER {iam_username} WITH LOGIN")
                    )
                    connection.execute(text(f"GRANT rds_iam TO {iam_username}"))

                # Get the current database name from the connection
                db_result = connection.execute(text("SELECT current_database()"))
                current_db = db_result.fetchone()[0]
                print(f"Setting up permissions for database: {current_db}")

                # Grant necessary permissions on the current database (not postgres)
                connection.execute(
                    text(
                        f"GRANT CONNECT ON DATABASE {current_db} TO {iam_username}"
                    )
                )
                connection.execute(
                    text(f"GRANT USAGE ON SCHEMA public TO {iam_username}")
                )
                connection.execute(
                    text(
                        f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {iam_username}"
                    )
                )
                connection.execute(
                    text(
                        f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {iam_username}"
                    )
                )
                connection.execute(
                    text(
                        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {iam_username}"
                    )
                )
                connection.execute(
                    text(
                        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {iam_username}"
                    )
                )

                connection.commit()

            finally:
                connection.close()

    except Exception as e:
        print(f"Error setting up IAM database user {iam_username}: {e}")
        raise


def test_iam_database_connection(app: Flask) -> None:
    """Test the IAM database connection."""
    with app.app_context():
        connection = db.engine.connect()
        try:
            result = connection.execute(
                text(
                    "SELECT 1 as test, current_user as user, current_database()"
                    " as db"
                )
            )
            result.fetchone()
        except Exception as e:
            print(f"Error testing IAM database connection: {e}")
            raise
        finally:
            connection.close()


def lambda_handler(event, context) -> None:
    response = {}
    send_success = partial(cfnresponse.send, event, context, cfnresponse.SUCCESS)
    send_failed = partial(cfnresponse.send, event, context, cfnresponse.FAILED)

    if event["RequestType"] == "Delete":
        response["Data"] = "Skipping bootstrap on delete."
        return send_success(response)

    secret_arn = os.getenv("DB_SECRET_ARN")

    if not secret_arn:
        print("DB_SECRET_ARN is not set")
        response["Data"] = "DB_SECRET_ARN is not set"
        return send_failed(response)

    username = os.getenv("DB_USER")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    if not (username and host and port and database):
        print("DB credentials are not set")
        response["Data"] = "DB credentials are not set"
        return send_failed(response)

    iam_username = os.getenv("DB_IAM_USER")

    if not iam_username:
        print("DB_IAM_USER is not set")
        response["Data"] = "DB_IAM_USER is not set"
        return send_failed(response)

    # Get the secret which contains the master password for initial setup
    secret = get_secret(secret_arn)
    print("Retrieved database secret")

    if not secret or "password" not in secret:
        print("DB secret does not contain password")
        response["Data"] = "DB secret does not contain password"
        return send_failed(response)

    db_uri = DbUri(
        hostname=host,
        port=port,
        database=database,
        username=username,
        password=secret["password"],
    )
    app = create_app(db_uri, use_iam=False)

    # 1. Upgrade database on Create and Update requests
    try:
        print("Upgrading database")
        with app.app_context():
            upgrade()
        print("Database upgraded successfully")
    except Exception as e:
        print(f"Error upgrading database: {e}")
        response["Data"] = f"Error upgrading database: {e}"
        return send_failed(response)

    # 2. Setup IAM database user on Create requests
    if event["RequestType"] == "Create":
        try:
            print("Setting up IAM database authentication")
            setup_iam_database_user(app, iam_username)
            print("IAM database authentication setup")
        except Exception as e:
            print(f"Error setting up IAM database authentication: {e}")
            response["Data"] = (
                f"Error setting up IAM database authentication: {e}"
            )
            return send_failed(response)

    # Create new app with auth token generation
    iam_db_uri = DbUri(
        hostname=db_uri.hostname,
        port=db_uri.port,
        database=db_uri.database,
        username=iam_username,
    )

    if LOCAL_DB:
        app = create_app(db_uri, use_iam=False)
    else:
        app = create_app(iam_db_uri, use_iam=True)

    # 3. Test the IAM database connection
    try:
        print("Testing IAM database connection")
        test_iam_database_connection(app)
        print("IAM database connection test successful")
    except Exception as e:
        print(f"Error testing IAM database connection: {e}")
        response["Data"] = f"Error testing IAM database connection: {e}"
        return send_failed(response)

    # 4. Load data on Create requests when data is provided
    if event["RequestType"] == "Create" and (
        data_arn := os.getenv("DB_BOOTSTRAP_DATA_ARN")
    ):
        print(f"DB_BOOTSTRAP_DATA_ARN: {data_arn}")
        try:
            print(f"Saving data file from {data_arn}")
            filename = save_datafile(data_arn)
            print(f"Data file saved to {filename}")
        except Exception as e:
            print(f"Error saving data file: {e}")
            response["Data"] = f"Error saving data file: {e}"
            return send_failed(response)

        try:
            print(f"Loading data from file: {filename}")
            load_data(app, filename)
            print("Data loaded successfully")
        except Exception as e:
            print(f"Error loading data from file: {e}")
            response["Data"] = f"Error loading data from file: {e}"
            return send_failed(response)
    else:
        print("No data to load")

    response["Data"] = "Database upgraded"
    return send_success(response)
