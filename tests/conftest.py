from datetime import timedelta
import os
from unittest.mock import patch

from flask import Flask
from moto import mock_aws
import pytest

from aws_portal.extensions import db

os.environ["APP_SYNC_HOST"] = "https://testing"
os.environ["AWS_TABLENAME_USER"] = "testing_table_user"
os.environ["AWS_TABLENAME_TAP"] = "testing_table_tap"
os.environ["APPSYNC_ACCESS_KEY"] = "testing"
os.environ["APPSYNC_SECRET_KEY"] = "testing"


@pytest.fixture(scope="function")
def with_mocked_tables():
    with mock_aws():
        import boto3
        client = boto3.client("dynamodb")
        client.create_table(
            TableName="testing_table_user",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        client.put_item(
            TableName="testing_table_user",
            Item={
                "id": {"S": "1"},
                "user_permission_id": {"S": "abc123"},
                "information": {"S": ""}
            }
        )

        yield client


@pytest.fixture()
def client(with_mocked_tables):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def client_with_mocked_user(client):
    with patch("aws_portal.rbac.api.current_user", type("User", (object,), {"id": 1})):
        yield client


@pytest.fixture
def timeout_client(app):
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=1)
    with app.test_client() as client:
        yield client
