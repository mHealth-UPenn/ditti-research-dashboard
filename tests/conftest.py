from datetime import timedelta
import os

from dotenv import load_dotenv
from moto import mock_aws
import pytest

from aws_portal.extensions import db
from aws_portal.app import create_app
from tests.testing_utils import create_unit_testing_db

load_dotenv("flask.env")

os.environ["FLASK_CONFIG"] = "Testing"
os.environ["APP_SYNC_HOST"] = "https://testing"
os.environ["AWS_TABLENAME_USER"] = "testing_table_user"
os.environ["AWS_TABLENAME_TAP"] = "testing_table_tap"
os.environ["APPSYNC_ACCESS_KEY"] = "testing"
os.environ["APPSYNC_SECRET_KEY"] = "testing"


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def client():
    app = create_app(testing=True)
    with app.app_context():
        create_unit_testing_db()
        with app.test_client() as client:
            yield client
        db.drop_all()


@pytest.fixture(scope="session")
def timeout_client(app):
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=1)
    with app.test_client() as client:
        yield client
