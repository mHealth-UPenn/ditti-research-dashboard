from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from aws_portal.extensions import db
from aws_portal.models import Api, JoinStudySubjectApi, StudySubject, JoinStudySubjectStudy
from tests.testing_utils import get_unwrapped_view


@pytest.fixture
def ditti_id():
    """
    Fixture to provide a consistent ditti_id for participant identification across tests.
    Must match the ID used in mock_participant_auth_required for proper test integration.
    """
    return "test-ditti-123"


@pytest.fixture
def api_name():
    """
    Fixture to provide a standard API name for testing API integration points.
    """
    return "TestAPI"


@pytest.fixture
def view_func():
    """
    Fixture providing a minimal mock view function that returns a success status.
    Useful for testing the Flask routing and middleware without actual view logic.
    """
    def mock_view_func(*args, **kwargs):
        return {"status": "success"}

    return mock_view_func


def test_view_directly(app, view_func, *args, **kwargs):
    """
    Tests a view function directly, bypassing Flask's routing middleware.

    This pattern allows testing the core logic of view functions without
    dealing with authentication decorators, request context, etc.
    """
    with app.app_context():
        response = view_func(*args, **kwargs)
        assert isinstance(response, dict)
        assert "status" in response


def test_get_participant(app, ditti_id):
    """
    Tests the get_participant endpoint by directly accessing the view function.

    This approach tests the core logic without authentication constraints.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "get_participant")

    with app.app_context():
        response = view_func(ditti_id=ditti_id)
        assert response is not None
        assert hasattr(response, "status_code")


@pytest.fixture
def study_subject():
    """
    Fixture providing a persistent StudySubject entity in the test database.

    This creates a real database record for a study subject with a consistent 
    ditti_id that can be referenced by multiple tests.
    """
    unique_ditti_id = "test-ditti-123"
    subject = StudySubject(
        created_on=datetime.now(),
        ditti_id=unique_ditti_id,
        is_archived=False
    )
    db.session.add(subject)
    db.session.commit()
    return subject


@pytest.fixture
def api_entry():
    """
    Fixture providing a persistent API entity in the test database.

    Creates an API record that tests can reference when testing API integration flows.
    """
    api = Api(name="TestAPI", is_archived=False)
    db.session.add(api)
    db.session.commit()
    return api


@pytest.fixture
def join_api(study_subject, api_entry):
    """
    Fixture providing a JoinStudySubjectApi entity linking a study subject with an API.

    This represents the many-to-many relationship between participants and APIs.
    """
    join_entry = JoinStudySubjectApi(
        study_subject_id=study_subject.id,
        api_id=api_entry.id,
        api_user_uuid="test_uuid",
        scope=["read", "write"]
    )
    db.session.add(join_entry)
    db.session.commit()
    return join_entry


def test_get_participant_success(app, study_subject, join_api, api_entry):
    """
    Tests the successful retrieval of participant data with associated APIs.

    Verifies that participant data is correctly serialized and returned with the
    proper API associations.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "get_participant")

    expected_data = {
        "dittiId": study_subject.ditti_id,
        "userId": study_subject.id,
        "apis": [
            {
                "apiName": api_entry.name,
                "scope": join_api.scope
            }
        ],
        "studies": []
    }

    with app.app_context(), \
            patch("aws_portal.utils.serialization.serialize_participant") as mock_serialize:
        mock_serialize.return_value = expected_data
        response = view_func(ditti_id=study_subject.ditti_id)

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["dittiId"] == expected_data["dittiId"]
        assert "apis" in response_data
        assert len(response_data["apis"]) == 1
        assert response_data["apis"][0]["apiName"] == api_entry.name


def test_get_participant_missing_id_token(client):
    """
    Tests the HTTP response when a request lacks authentication credentials.

    Verifies proper 401 error handling for unauthenticated requests.
    """
    response = client.get("/participant")
    assert response.status_code == 401
    assert response.get_json() == {"msg": "Authentication required"}


def test_get_participant_invalid_id_token_format(client):
    """
    Tests the HTTP response when authentication token has invalid format.

    Verifies proper error handling for malformed authorization headers.
    """
    headers = {"Authorization": "InvalidFormat"}
    response = client.get("/participant", headers=headers)
    assert response.status_code == 401
    assert "Authentication required" in response.get_json().get("msg", "")


def test_get_participant_user_not_found(app):
    """
    Tests error handling when the requested participant doesn't exist.

    Verifies proper 404 responses for non-existent users.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "get_participant")

    with app.app_context(), \
            patch("aws_portal.models.StudySubject.query") as mock_query:
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        response = view_func(ditti_id="nonexistent_ditti_id")

        assert response.status_code == 404
        assert response.get_json() == {"msg": "User not found or is archived."}


def test_get_participant_exception_handling(app):
    """
    Tests error handling when an unexpected exception occurs during participant lookup.

    Verifies that database errors are properly caught and return 500 responses.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "get_participant")

    with app.app_context(), \
            patch("aws_portal.models.StudySubject.query") as mock_query:
        mock_query.filter_by.side_effect = Exception("Database error")
        response = view_func(ditti_id="test_ditti_id")

        assert response.status_code == 500
        assert response.get_json() == {"msg": "Unexpected server error."}


def test_revoke_api_access_direct(app, study_subject, api_entry, join_api):
    """
    Tests the API access revocation process by directly calling the view function.

    Verifies that the API tokens are properly deleted and the database association
    is removed when revoking API access.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "revoke_api_access")

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("aws_portal.extensions.db.session.delete") as mock_db_delete, \
            patch("aws_portal.extensions.db.session.commit") as mock_db_commit:

        response = view_func(api_entry.name, ditti_id=study_subject.ditti_id)

        assert response.status_code == 200
        assert response.get_json() == {
            "msg": "API access revoked successfully"}
        mock_delete_tokens.assert_called_once_with(
            api_name=api_entry.name, ditti_id=study_subject.ditti_id)
        mock_db_delete.assert_called_once_with(join_api)
        mock_db_commit.assert_called_once()


def test_delete_participant_direct(app, study_subject, api_entry, join_api):
    """
    Tests participant account deletion by directly calling the view function.

    Verifies the complete deletion flow including:
    1. API token revocation
    2. Cognito user deletion
    3. Database record cleanup
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "delete_participant")

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("boto3.client") as mock_boto3_client, \
            patch("aws_portal.extensions.db.session.delete") as mock_db_delete, \
            patch("aws_portal.extensions.db.session.commit") as mock_db_commit:

        mock_cognito_client = MagicMock()
        mock_boto3_client.return_value = mock_cognito_client

        # Mock account with admin privileges
        mock_account = type("Account", (), {
            "id": "2",
            "email": "admin@example.com",
            "name": "Admin User",
            "admin": True,
            "is_admin": True
        })

        response = view_func(mock_account, study_subject.ditti_id)

        assert response.status_code == 200
        assert response.get_json() == {"msg": "Account deleted successfully."}

        mock_delete_tokens.assert_called_once_with(
            api_name=api_entry.name, ditti_id=study_subject.ditti_id)

        mock_cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=app.config.get("COGNITO_PARTICIPANT_USER_POOL_ID"),
            Username=study_subject.ditti_id
        )


@pytest.fixture
def mock_auth_header():
    """
    Fixture providing mock authentication headers for admin endpoints.
    Used for testing routes that require admin authentication.
    """
    return {"Authorization": "Bearer fake_token"}


def test_delete_participant_success(app, study_subject, api_entry, join_api):
    """
    Tests the full participant deletion flow with an authenticated admin user.

    Duplicates test_delete_participant_direct but with focus on success path integration.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "delete_participant")

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("boto3.client") as mock_boto3_client, \
            patch("aws_portal.extensions.db.session.delete") as mock_db_delete, \
            patch("aws_portal.extensions.db.session.commit") as mock_db_commit:

        mock_cognito_client = MagicMock()
        mock_boto3_client.return_value = mock_cognito_client

        # Mock admin account
        mock_account = type("Account", (), {
            "id": "2",
            "email": "admin@example.com",
            "name": "Admin User",
            "admin": True,
            "is_admin": True
        })

        response = view_func(mock_account, study_subject.ditti_id)

        assert response.status_code == 200
        assert response.get_json() == {"msg": "Account deleted successfully."}

        mock_delete_tokens.assert_called_once_with(
            api_name=api_entry.name, ditti_id=study_subject.ditti_id)

        mock_cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=app.config.get("COGNITO_PARTICIPANT_USER_POOL_ID"),
            Username=study_subject.ditti_id
        )


def test_delete_participant_missing_id_token(client):
    """
    Tests the HTTP response when trying to delete a participant without authentication.

    Verifies that unauthenticated deletion attempts are rejected with 401.
    """
    response = client.delete("/participant/test_user")
    assert response.status_code == 401


def test_delete_participant_user_not_found(app):
    """
    Tests error handling when attempting to delete a non-existent participant.

    Verifies proper 404 responses for deleting unknown users.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "delete_participant")

    with app.app_context(), \
            patch("aws_portal.models.StudySubject.query") as mock_query:
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        mock_account = type("Account", (), {
            "id": "2",
            "email": "admin@example.com",
            "name": "Admin User"
        })

        response = view_func(mock_account, "nonexistent_ditti_id")

        assert response.status_code == 404
        assert response.get_json() == {
            "msg": "User not found or already archived."}


def test_delete_participant_cognito_exception(app, study_subject):
    """
    Tests error handling when Cognito user deletion fails.

    Verifies proper error response when AWS Cognito operations fail during
    participant deletion.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, "delete_participant")

    with app.app_context(), \
            patch("aws_portal.models.JoinStudySubjectApi.query") as mock_join_query, \
            patch("boto3.client") as mock_boto3_client:

        mock_filter = MagicMock()
        mock_filter.all.return_value = []
        mock_join_query.filter_by.return_value = mock_filter

        mock_cognito_client = MagicMock()
        mock_cognito_client.admin_delete_user.side_effect = Exception(
            "Cognito error")
        mock_boto3_client.return_value = mock_cognito_client

        mock_account = type("Account", (), {
            "id": "2",
            "email": "admin@example.com",
            "name": "Admin User"
        })

        response = view_func(mock_account, study_subject.ditti_id)

        assert response.status_code == 500
        error_msg = response.get_json()["msg"]
        assert "Error deleting" in error_msg, f"Expected error message about deletion, got: {error_msg}"


@pytest.fixture
def study_id():
    """
    Fixture to provide a study ID for testing consent-related endpoints.
    """
    return 1


@pytest.fixture
def join_study(study_subject):
    """
    Fixture to create a JoinStudySubjectStudy relation for testing consent updates.
    """
    join_entry = JoinStudySubjectStudy(
        study_subject_id=study_subject.id,
        study_id=1,
        did_consent=False,
        created_on=datetime.utcnow(),
        starts_on=datetime.utcnow()
    )
    db.session.add(join_entry)
    db.session.commit()
    return join_entry


def test_update_consent_direct(app, study_subject, study_id, join_study):
    """
    Tests direct invocation of the update_consent function.

    Verifies that a participant can successfully update their consent status
    when providing valid data.
    """
    from aws_portal.views import participant
    view_func = get_unwrapped_view(participant, "update_consent")

    with app.app_context():
        with app.test_request_context(json={"didConsent": True}):
            response = view_func(study_id, study_subject.ditti_id)
        assert response.status_code == 200

        # Verify database update - keep inside app context
        updated_join = JoinStudySubjectStudy.query.filter_by(
            study_subject_id=study_subject.id,
            study_id=study_id
        ).first()
        assert updated_join.did_consent is True


def test_update_consent_missing_field(app, ditti_id, study_id):
    """
    Tests update_consent with missing didConsent field in request.

    Verifies that the endpoint returns a 400 Bad Request when the
    required field is missing.
    """
    from aws_portal.views import participant
    view_func = get_unwrapped_view(participant, "update_consent")

    with app.app_context():
        with app.test_request_context(json={}):
            response = view_func(study_id, ditti_id)
            assert response.status_code == 400
            assert "didConsent" in response.get_json()["msg"]


def test_update_consent_invalid_type(app, ditti_id, study_id):
    """
    Tests update_consent with an invalid data type for didConsent.

    Verifies that the endpoint validates the data type of the
    didConsent field and returns appropriate error.
    """
    from aws_portal.views import participant
    view_func = get_unwrapped_view(participant, "update_consent")

    with app.app_context():
        # String instead of boolean
        with app.test_request_context(json={"didConsent": "yes"}):
            response = view_func(study_id, ditti_id)
            assert response.status_code == 400
            assert "boolean" in response.get_json()["msg"].lower()


def test_update_consent_user_not_found(app, study_id):
    """
    Tests update_consent when the user does not exist.

    Verifies that the endpoint returns a 404 Not Found when
    attempting to update consent for a non-existent user.
    """
    from aws_portal.views import participant
    view_func = get_unwrapped_view(participant, "update_consent")

    with app.app_context():
        with app.test_request_context(json={"didConsent": True}):
            response = view_func(study_id, "non-existent-ditti")
            assert response.status_code == 404
            assert "not found" in response.get_json()["msg"].lower()


def test_update_consent_study_not_found(app, study_subject, study_id):
    """
    Tests update_consent when the study enrollment does not exist.

    Verifies that the endpoint returns a 404 Not Found when
    attempting to update consent for a study that the user is not enrolled in.
    """
    from aws_portal.views import participant
    view_func = get_unwrapped_view(participant, "update_consent")

    # Using a different study_id than the one in the join_study fixture
    non_existent_study_id = study_id + 100

    with app.app_context():
        with app.test_request_context(json={"didConsent": True}):
            response = view_func(non_existent_study_id, study_subject.ditti_id)
            assert response.status_code == 404
            assert "enrollment not found" in response.get_json()["msg"].lower()


@patch("aws_portal.extensions.db.session.commit")
def test_update_consent_database_error(mock_commit, app, study_subject, study_id, join_study):
    """
    Tests update_consent handling of database errors.

    Verifies that the endpoint properly handles and reports database errors.
    """
    from aws_portal.views import participant
    view_func = get_unwrapped_view(participant, "update_consent")

    # Simulate database error
    mock_commit.side_effect = Exception("Database error")

    with app.app_context():
        with app.test_request_context(json={"didConsent": True}):
            response = view_func(study_id, study_subject.ditti_id)
            assert response.status_code == 500
            assert "error" in response.get_json()["msg"].lower()


def test_flask_app_routes(app):
    """
    Tests that all expected endpoints are registered in the Flask app.

    This test verifies that the Flask blueprint registers all the routes we expect,
    providing a form of API contract testing.
    """
    with app.app_context():
        rules = [str(rule) for rule in app.url_map.iter_rules()]

        # Check that all participant endpoints are registered
        assert "/participant" in rules
        assert "/participant/study/<int:study_id>/consent" in rules
        assert "/participant/api/<string:api_name>" in rules
        assert "/participant/<string:ditti_id>" in rules
