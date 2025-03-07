from datetime import timedelta
from functools import partial
import os
import boto3
from flask import Blueprint, jsonify
from moto import mock_aws
import pytest
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    init_admin_account, init_admin_app, init_admin_group, init_db, init_api
)
from aws_portal.auth.decorators import researcher_auth_required
from tests.testing_utils import (
    create_joins, create_tables, get_auth_headers, login_admin_account,
    login_test_account
)
from aws_portal.auth.decorators import participant_auth_required

os.environ["APP_SYNC_HOST"] = "https://testing"
os.environ["AWS_TABLENAME_USER"] = "testing_table_user"
os.environ["AWS_TABLENAME_TAP"] = "testing_table_tap"
os.environ["APPSYNC_ACCESS_KEY"] = "testing"
os.environ["APPSYNC_SECRET_KEY"] = "testing"

blueprint = Blueprint("test", __name__, url_prefix="/test")


@blueprint.route("/participant-get")
@participant_auth_required
def participant_get(account):
    return jsonify({"msg": "OK"})


@blueprint.route("/researcher-get")
@researcher_auth_required
def researcher_get(account):
    return jsonify({"msg": "OK"})


@blueprint.route("/researcher-get-with-permission")
@researcher_auth_required("Create", "Accounts")
def researcher_get_with_permission(account):
    return jsonify({"msg": "OK"})


@blueprint.route("/get")
@researcher_auth_required
def get(account):
    return jsonify({"msg": "OK"})


@blueprint.route("/get-auth-required-action")
@researcher_auth_required("foo", "bar")
def get_auth_required_action(account):
    return jsonify({"msg": "OK"})


@blueprint.route("/get-auth-required-resource")
@researcher_auth_required("bar", "baz")
def get_auth_required_resource(account):
    return jsonify({"msg": "OK"})


@blueprint.route("/post-auth-required-action", methods=["POST"])
@researcher_auth_required("foo", "bar")
def post_auth_required_action(account):
    return jsonify({"msg": "OK"})


@blueprint.route("/post-auth-required-resource", methods=["POST"])
@researcher_auth_required("bar", "baz")
def post_auth_required_resource(account):
    return jsonify({"msg": "OK"})


@pytest.fixture(scope="function")
def with_mocked_tables():
    with mock_aws():
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


@pytest.fixture
def app(with_mocked_tables):
    app = create_app(testing=True)
    app.register_blueprint(blueprint)
    with app.app_context():
        init_db()
        init_admin_app()
        init_admin_group()
        init_admin_account()
        init_api()
        create_tables()
        create_joins()
        db.session.commit()
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def get(client):
    res = login_test_account("foo", client)
    headers = get_auth_headers(res)
    get = partial(client.get, headers=headers)
    yield get


@pytest.fixture
def get_admin(client):
    res = login_admin_account(client)
    headers = get_auth_headers(res)
    get = partial(client.get, headers=headers)
    yield get


@pytest.fixture
def delete(client):
    res = login_test_account("foo", client)
    headers = get_auth_headers(res)
    delete = partial(
        client.delete,
        content_type="application/json",
        headers=headers
    )

    yield delete


@pytest.fixture
def delete_admin(client):
    res = login_admin_account(client)
    headers = get_auth_headers(res)
    delete = partial(
        client.delete,
        content_type="application/json",
        headers=headers
    )

    yield delete


@pytest.fixture
def post(client):
    res = login_test_account("foo", client)
    headers = get_auth_headers(res)
    post = partial(
        client.post,
        content_type="application/json",
        headers=headers
    )

    yield post


@pytest.fixture
def post_admin(client):
    res = login_admin_account(client)
    headers = get_auth_headers(res)
    post = partial(
        client.post,
        content_type="application/json",
        headers=headers
    )

    yield post


@pytest.fixture
def timeout_client(app):
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=1)
    with app.test_client() as client:
        yield client


# Auth provider common fixtures for tests
@pytest.fixture
def base_cognito_auth():
    """
    Return a base cognito auth test implementation.

    Creates a minimal implementation of CognitoAuthBase for testing purposes
    without requiring any actual AWS configuration.
    """
    from aws_portal.auth.providers.cognito.base import CognitoAuthBase

    class TestCognitoAuth(CognitoAuthBase):
        """Test implementation of CognitoAuthBase."""

        def __init__(self):
            super().__init__(user_type="test")

        def get_user_from_claims(self, claims):
            """Extract user info from claims."""
            return {"user_id": claims.get("sub"), "email": claims.get("email")}

        def get_config_prefix(self):
            """Return the config prefix for test implementation."""
            return "TEST_COGNITO"

    return TestCognitoAuth()


@pytest.fixture
def participant_auth_fixture():
    """
    Return a participant auth instance.

    Creates an actual ParticipantAuth instance for testing.
    """
    from aws_portal.auth.providers.cognito.participant import ParticipantAuth
    return ParticipantAuth()


@pytest.fixture
def researcher_auth_fixture():
    """
    Return a researcher auth instance.

    Creates an actual ResearcherAuth instance for testing.
    """
    from aws_portal.auth.providers.cognito.researcher import ResearcherAuth
    return ResearcherAuth()


# Common test data for auth tests
@pytest.fixture
def mock_auth_test_data():
    """
    Common test data for auth tests.

    Provides standardized test data used across different auth test files,
    ensuring consistency in testing claims and tokens.
    """
    return {
        "researcher_claims": {
            "sub": "test-user-id",
            "email": "researcher@example.com",
            "cognito:username": "researcher@example.com",
            "name": "Test Researcher",
            "token_use": "id"
        },
        "participant_claims": {
            "sub": "test-user-id",
            "email": "test@example.com",
            "cognito:username": "ditti_12345",
            "name": "Test User",
            "token_use": "id"
        },
        "access_token_claims": {
            "sub": "test-user-id",
            "email": "test@example.com",
            "token_use": "access",
            "exp": 1700000000  # Future time
        },
        "fake_tokens": {
            "id_token": "fake-id-token",
            "access_token": "fake-access-token",
            "refresh_token": "fake-refresh-token"
        }
    }
