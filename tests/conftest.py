import os

from dotenv import load_dotenv
from moto import mock_aws

load_dotenv("flask.env")

# Environment variables
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"  # noqa: S105
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["APP_SYNC_HOST"] = "https://testing"
os.environ["AWS_TABLENAME_USER"] = "testing_table_user"
os.environ["AWS_TABLENAME_TAP"] = "testing_table_tap"
os.environ["APPSYNC_ACCESS_KEY"] = "testing"
os.environ["APPSYNC_SECRET_KEY"] = "testing"  # noqa: S105

import json
from unittest.mock import MagicMock, patch

import boto3
import pytest
from flask import Blueprint

from backend.app import create_app
from backend.extensions import db
from backend.models import (
    init_admin_account,
    init_admin_app,
    init_admin_group,
    init_api,
    init_db,
)
from tests.testing_utils import (
    create_joins,
    create_tables,
    mock_researcher_auth_for_testing,
)

# Test blueprint and routes
blueprint = Blueprint("test", __name__, url_prefix="/test")


# Infrastructure fixtures
@pytest.fixture
def with_mocked_tables():
    """
    Set up mocked DynamoDB tables for testing.

    Creates test tables and populates sample data, yielding the boto3 client.
    """
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
            BillingMode="PAY_PER_REQUEST",
        )

        client.put_item(
            TableName="testing_table_user",
            Item={
                "id": {"S": "1"},
                "user_permission_id": {"S": "abc123"},
                "information": {"S": ""},
            },
        )

        yield client


# App and client fixtures
@pytest.fixture
def app(with_mocked_tables):
    """
    Create a test Flask application with initialized database.

    Sets up a complete test environment with admin accounts and required tables.
    """
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
    """Create a Flask test client for the test application."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context(app):
    """
    Provide app context for tests that need it.

    This avoids the "Working outside of application context" error.
    """
    with app.app_context():
        yield


@pytest.fixture
def get_admin(client):
    """
    Create a test GET request function with admin authentication.

    Returns a partially applied function for making admin GET requests.
    """
    headers = mock_researcher_auth_for_testing(client, is_admin=True)

    def _get(url, query_string=None, **kwargs):
        return client.get(
            url, query_string=query_string, headers=headers, **kwargs
        )

    return _get


@pytest.fixture
def post_admin(client):
    """
    Create a test POST request function with admin authentication.

    Returns a partially applied function for making admin POST requests.
    """
    headers = mock_researcher_auth_for_testing(client, is_admin=True)

    def _post(url, data=None, **kwargs):
        return client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            headers=headers,
            **kwargs,
        )

    return _post


@pytest.fixture
def delete_admin(client):
    """
    Create a test DELETE request function with admin authentication.

    Returns a partially applied function for making admin DELETE requests.
    """
    headers = mock_researcher_auth_for_testing(client, is_admin=True)

    def _delete(url, data=None, **kwargs):
        return client.delete(
            url,
            data=json.dumps(data) if data else None,
            content_type="application/json",
            headers=headers,
            **kwargs,
        )

    return _delete


# Auth-related fixtures
@pytest.fixture
def base_cognito_auth():
    """
    Return a base cognito auth test implementation.

    Creates a minimal implementation of CognitoAuthBase for testing purposes
    without requiring any actual AWS configuration.
    """
    from backend.auth.providers.cognito.base import CognitoAuthBase

    class TestCognitoAuth(CognitoAuthBase):
        """Test implementation of CognitoAuthBase for testing."""

        def __init__(self):
            super().__init__(user_type="test")

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
    from backend.auth.providers.cognito.participant import ParticipantAuth

    return ParticipantAuth()


@pytest.fixture
def researcher_auth_fixture():
    """
    Return a researcher auth instance.

    Creates an actual ResearcherAuth instance for testing.
    """
    from backend.auth.providers.cognito.researcher import ResearcherAuth

    return ResearcherAuth()


# Test data fixtures
@pytest.fixture
def mock_auth_test_data():
    """
    Provide test data for mocking authentication.

    Returns both user objects for mock decorators and claims/tokens for auth controllers.
    """
    return {
        "researcher_claims": {
            "sub": "test-user-id",
            "email": "researcher@example.com",
            "cognito:username": "researcher@example.com",
            "name": "Test Researcher",
            "token_use": "id",
        },
        "participant_claims": {
            "sub": "test-user-id",
            "email": "test@example.com",
            "cognito:username": "ditti_12345",
            "name": "Test User",
            "token_use": "id",
        },
        "access_token_claims": {
            "sub": "test-user-id",
            "email": "test@example.com",
            "token_use": "access",
            "exp": 1700000000,  # Future time
        },
        "fake_tokens": {
            "id_token": "fake-id-token",
            "access_token": "fake-access-token",
            "refresh_token": "fake-refresh-token",
        },
    }


# Auth app fixtures
@pytest.fixture
def auth_app():
    """
    Create a test Flask application with initialized database and mock auth decorators.

    This fixture provides all the necessary configuration for
    authentication testing, including mocked OAuth clients.
    """
    # Create a Flask test application
    app = create_app(testing=True)
    app.register_blueprint(blueprint)

    # Mock the auth
    with app.app_context():
        init_db()
        init_admin_app()
        init_admin_group()
        init_admin_account()
        init_api()
        create_tables()
        create_joins()
        db.session.commit()

        # Mock the OAuth clients
        with (
            patch(
                "backend.auth.controllers.base.AuthControllerBase.init_oauth_client"
            ),
            patch(
                "backend.auth.controllers.participant.ParticipantAuthController.init_oauth_client"
            ),
            patch(
                "backend.auth.controllers.researcher.ResearcherAuthController.init_oauth_client"
            ),
        ):
            yield app


@pytest.fixture
def mock_auth_oauth():
    """
    Mock the OAuth client initialization for auth controllers.

    This fixture prevents real OAuth connections during tests.
    """
    # Mock the OAuth client initialization
    with (
        patch(
            "backend.auth.controllers.base.AuthControllerBase.init_oauth_client"
        ),
        patch(
            "backend.auth.controllers.participant.ParticipantAuthController.init_oauth_client"
        ),
        patch(
            "backend.auth.controllers.researcher.ResearcherAuthController.init_oauth_client"
        ),
    ):
        yield


@pytest.fixture
def mock_model_not_found():
    """
    Mock a model query that returns no results.

    Example usage:
        def test_user_not_found(mock_model_not_found):
            query_mock = mock_model_not_found(User)
            # Test logic here...

    Args:
        model_class: The SQLAlchemy model class to mock

    Returns
    -------
        A function that takes a model class and returns a mock query that will
        return None for first() and empty list for all()
    """
    patchers = []

    def _mock_model_not_found(model_class):
        """Inner function to create the mock for a specific model class."""
        patcher = patch.object(model_class, "query")
        mock_query = patcher.start()
        patchers.append(patcher)

        # Create mock filter methods
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_filter.all.return_value = []

        # Setup common query methods to return the filter mock
        mock_query.filter_by.return_value = mock_filter
        mock_query.filter.return_value = mock_filter

        return mock_query

    yield _mock_model_not_found

    # Clean up patchers
    for patcher in patchers:
        patcher.stop()
