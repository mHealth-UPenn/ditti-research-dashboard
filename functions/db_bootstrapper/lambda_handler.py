import json
import logging
import os
from functools import partial

import boto3
import cfnresponse
from flask import Flask
from flask_migrate import upgrade
from load_data import load_data

from backend.extensions import db, migrate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# It is safe to use /tmp because the lambda function is ephemeral
DATA_FILE = "/tmp/data.json"  # noqa: S108


def create_app(db_uri: str):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)
    return app


def get_secret(secret_arn: str):
    logger.info(f"Getting secret from {secret_arn}")
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])


def get_data(data_arn: str):
    logger.info(f"Loading data from {data_arn}")
    client = boto3.client("s3")
    response = client.get_object(
        Bucket=data_arn.split("/")[2], Key=data_arn.split("/")[3]
    )
    data = response["Body"].read()
    return data


def save_datafile(data_arn: str):
    logger.info(f"Saving data to file from {data_arn}")
    client = boto3.client("s3")
    client.download_file(
        Bucket=data_arn.split("/")[2],
        Key=data_arn.split("/")[3],
        Filename=DATA_FILE,
    )
    return DATA_FILE


def handler(event, context):
    response = {}
    send_success = partial(cfnresponse.send, event, context, cfnresponse.SUCCESS)
    send_failed = partial(cfnresponse.send, event, context, cfnresponse.FAILED)

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

    try:
        app = create_app(db_uri)
        logger.info("Creating database")
        with app.app_context():
            upgrade()
        logger.info("Database created")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        response["Data"] = f"Error creating database: {e}"
        return send_failed(response)

    if data_arn := os.getenv("DB_BOOTSTRAP_DATA_ARN"):
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

    response["Data"] = "Database created"
    return send_success(response)
