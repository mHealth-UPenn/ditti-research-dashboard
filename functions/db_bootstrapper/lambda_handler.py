import json
import logging
import os
import socket
import time
from functools import partial

import boto3
import cfnresponse
from flask import Flask
from flask_migrate import upgrade
from load_data import load_data
from sqlalchemy import create_engine, text

from backend.extensions import db, migrate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# It is safe to use /tmp because the lambda function is ephemeral
DATA_FILE = "/tmp/data.json"  # noqa: S108


def retry_with_backoff(func, max_retries=5, initial_delay=1):
    """Retry a function with exponential backoff."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds..."
            )
            time.sleep(delay)
            delay *= 2


def create_app(db_uri: str) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)
    return app


def get_secret(secret_arn: str) -> dict:
    logger.info(f"Getting secret from {secret_arn}")
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])


def save_datafile(data_arn: str) -> str:
    logger.info(f"Saving data to file from {data_arn}")
    client = boto3.client("s3")
    bucket, key = data_arn.split(":")[-1].split("/")
    client.download_file(
        Bucket=bucket,
        Key=key,
        Filename=DATA_FILE,
    )
    return DATA_FILE


def setup_iam_database_user(db_uri: str, username: str) -> None:
    """
    Set up a database user for IAM authentication.

    Args
    ----
        db_uri: The database connection string
        username: The username to create for IAM authentication
    """
    logger.info(f"Setting up IAM database user: {username}")

    try:
        engine = create_engine(db_uri)
        with engine.connect() as connection:
            # Check if user already exists
            result = connection.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :username"),
                {"username": username},
            )

            if result.fetchone():
                logger.info(
                    f"User {username} already exists, updating IAM permissions"
                )
                # Grant IAM role to existing user
                connection.execute(text(f"GRANT rds_iam TO {username}"))
            else:
                logger.info(
                    f"Creating new user {username} with IAM authentication"
                )
                # Create new user with IAM authentication
                connection.execute(text(f"CREATE USER {username} WITH LOGIN"))
                connection.execute(text(f"GRANT rds_iam TO {username}"))

            # Grant necessary permissions (adjust as needed for your application)
            connection.execute(
                text(f"GRANT CONNECT ON DATABASE postgres TO {username}")
            )
            connection.execute(
                text(f"GRANT USAGE ON SCHEMA public TO {username}")
            )
            connection.execute(
                text(
                    f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username}"
                )
            )
            connection.execute(
                text(
                    f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {username}"
                )
            )
            connection.execute(
                text(
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {username}"
                )
            )
            connection.execute(
                text(
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {username}"
                )
            )

            connection.commit()
            logger.info(f"Successfully setup IAM database user {username}")

    except Exception as e:
        logger.error(f"Error setting up IAM database user {username}: {e}")
        raise


def handler(event, context) -> None:
    response = {}
    send_success = partial(cfnresponse.send, event, context, cfnresponse.SUCCESS)
    send_failed = partial(cfnresponse.send, event, context, cfnresponse.FAILED)

    if event["RequestType"] == "Delete":
        response["Data"] = "Skipping bootstrap on delete."
        return send_success(response)

    secret_arn = os.getenv("DB_SECRET_ARN")

    if not secret_arn:
        logger.error("DB_SECRET_ARN is not set")
        response["Data"] = "DB_SECRET_ARN is not set"
        return send_failed(response)

    username = os.getenv("DB_USER")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    if not (username and host and port and database):
        logger.error("DB credentials are not set")
        response["Data"] = "DB credentials are not set"
        return send_failed(response)

    secret = get_secret(secret_arn)

    if not secret or "password" not in secret:
        logger.error("DB secret is not set")
        response["Data"] = "DB secret is not set"
        return send_failed(response)

    password = secret["password"]
    db_uri = f"postgresql://{username}:{password}@{host}:{port}/{database}"

    # Debug connection details
    logger.info(
        f"Database connection details:"
        f"\n  Host: {host}"
        f"\n  Port: {port}"
        f"\n  Database: {database}"
        f"\n  Username: {username}"
        f"\n  Connection URI: postgresql://{username}:***@{host}:{port}/{database}"
    )

    # Debug DNS resolution
    try:
        logger.info(f"Attempting to resolve hostname: {host}")
        resolved_ip = socket.gethostbyname(host)
        logger.info(f"Successfully resolved {host} to {resolved_ip}")
    except socket.gaierror as e:
        logger.error(f"Failed to resolve hostname {host}: {e}")
        response["Data"] = f"DNS resolution failed for {host}: {e}"
        return send_failed(response)

    # Test TCP connection
    try:
        logger.info(f"Testing TCP connection to {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        if result == 0:
            logger.info(f"TCP connection to {host}:{port} successful")
        else:
            logger.warning(
                f"TCP connection to {host}:{port} failed with error code {result}"
            )
    except Exception as e:
        logger.warning(f"TCP connection test failed: {e}")

    try:
        app = create_app(db_uri)
        logger.info("Upgrading database")

        def upgrade_database():
            with app.app_context():
                upgrade()

        retry_with_backoff(upgrade_database)
        logger.info("Database upgraded")

    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        response["Data"] = f"Error upgrading database: {e}"
        return send_failed(response)

    if event["RequestType"] == "Create":
        try:
            # Setup IAM database user after successful upgrade
            logger.info("Setting up IAM database authentication")
            setup_iam_database_user(db_uri, username)
            logger.info("IAM database authentication setup")
        except Exception as e:
            logger.error(f"Error setting up IAM database authentication: {e}")
            response["Data"] = (
                f"Error setting up IAM database authentication: {e}"
            )
            return send_failed(response)

    if event["RequestType"] == "Create" and (
        data_arn := os.getenv("DB_BOOTSTRAP_DATA_ARN")
    ):
        logger.debug(f"DB_BOOTSTRAP_DATA_ARN: {data_arn}")
        try:
            filename = save_datafile(data_arn)
        except Exception as e:
            logger.error(f"Error saving data file: {e}")
            response["Data"] = f"Error saving data file: {e}"
            return send_failed(response)
        try:
            load_data(db_uri, filename)
        except Exception as e:
            logger.error(f"Error loading data from file: {e}")
            response["Data"] = f"Error loading data from file: {e}"
            return send_failed(response)

    response["Data"] = "Database upgraded"
    return send_success(response)
