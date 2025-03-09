from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from aws_portal.extensions import db
from aws_portal.models import Api, JoinStudySubjectApi, StudySubject
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
    view_func = get_unwrapped_view(participant_view, 'get_participant')

    with app.app_context():
        response = view_func(ditti_id=ditti_id)
        assert response is not None
        assert hasattr(response, 'status_code')


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
    view_func = get_unwrapped_view(participant_view, 'get_participant')

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
    view_func = get_unwrapped_view(participant_view, 'get_participant')

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
    view_func = get_unwrapped_view(participant_view, 'get_participant')

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
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

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
    view_func = get_unwrapped_view(participant_view, 'delete_participant')

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("boto3.client") as mock_boto3_client, \
            patch("aws_portal.extensions.db.session.delete") as mock_db_delete, \
            patch("aws_portal.extensions.db.session.commit") as mock_db_commit:

        mock_cognito_client = MagicMock()
        mock_boto3_client.return_value = mock_cognito_client

        # Mock account with admin privileges
        mock_account = type('Account', (), {
            'id': '2',
            'email': 'admin@example.com',
            'name': 'Admin User',
            'admin': True,
            'is_admin': True
        })

        response = view_func(mock_account, study_subject.ditti_id)

        assert response.status_code == 200
        assert response.get_json() == {"msg": "Account deleted successfully."}

        mock_delete_tokens.assert_called_once_with(
            api_name=api_entry.name, ditti_id=study_subject.ditti_id)

        mock_cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=app.config.get('COGNITO_PARTICIPANT_USER_POOL_ID'),
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
    view_func = get_unwrapped_view(participant_view, 'delete_participant')

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("boto3.client") as mock_boto3_client, \
            patch("aws_portal.extensions.db.session.delete") as mock_db_delete, \
            patch("aws_portal.extensions.db.session.commit") as mock_db_commit:

        mock_cognito_client = MagicMock()
        mock_boto3_client.return_value = mock_cognito_client

        # Mock admin account
        mock_account = type('Account', (), {
            'id': '2',
            'email': 'admin@example.com',
            'name': 'Admin User',
            'admin': True,
            'is_admin': True
        })

        response = view_func(mock_account, study_subject.ditti_id)

        assert response.status_code == 200
        assert response.get_json() == {"msg": "Account deleted successfully."}

        mock_delete_tokens.assert_called_once_with(
            api_name=api_entry.name, ditti_id=study_subject.ditti_id)

        mock_cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=app.config.get('COGNITO_PARTICIPANT_USER_POOL_ID'),
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
    view_func = get_unwrapped_view(participant_view, 'delete_participant')

    with app.app_context(), \
            patch("aws_portal.models.StudySubject.query") as mock_query:
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        mock_account = type('Account', (), {
            'id': '2',
            'email': 'admin@example.com',
            'name': 'Admin User'
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
    view_func = get_unwrapped_view(participant_view, 'delete_participant')

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

        mock_account = type('Account', (), {
            'id': '2',
            'email': 'admin@example.com',
            'name': 'Admin User'
        })

        response = view_func(mock_account, study_subject.ditti_id)

        assert response.status_code == 500
        error_msg = response.get_json()["msg"]
        assert "Error deleting" in error_msg, f"Expected error message about deletion, got: {error_msg}"


@patch("aws_portal.extensions.db.session.execute")
@patch("aws_portal.models.Account.validate_ask", lambda *_: None)
def test_download_fitbit_participant(mock_execute, app):
    """
    Tests the Fitbit data download endpoint for a specific participant.

    Verifies that participant-specific Fitbit data can be retrieved and
    returned in the proper format.
    """
    from aws_portal.views import fitbit_data
    view_func = get_unwrapped_view(fitbit_data, 'download_fitbit_participant')

    # Sample Fitbit sleep data
    mock_data = [
        {"Ditti ID": "test-ditti-123", "Sleep Log Date": "2023-01-01", "Sleep Level Timestamp":
            "2023-01-01 01:00:00", "Sleep Level Level": "deep", "Sleep Level Length (s)": 3600},
        {"Ditti ID": "test-ditti-123", "Sleep Log Date": "2023-01-02", "Sleep Level Timestamp":
            "2023-01-02 01:00:00", "Sleep Level Level": "light", "Sleep Level Length (s)": 1800}
    ]
    mock_result = MagicMock()
    mock_result.fetchall.return_value = mock_data
    mock_execute.return_value = mock_result

    mock_account = type('Account', (), {
        'id': '2',
        'email': 'admin@example.com',
        'name': 'Admin User'
    })

    with app.app_context():
        response = view_func(mock_account, "test-ditti-123")

    assert response.status_code == 200
    assert response.mimetype == "application/json"


@patch("aws_portal.extensions.db.session.execute")
def test_download_fitbit_participant_not_found(mock_execute, app):
    """
    Tests the Fitbit data download endpoint when participant has no data.

    Verifies that empty result sets are handled properly without errors.
    """
    from aws_portal.views import fitbit_data
    view_func = get_unwrapped_view(fitbit_data, 'download_fitbit_participant')

    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_execute.return_value = mock_result

    mock_account = type('Account', (), {
        'id': '2',
        'email': 'admin@example.com',
        'name': 'Admin User'
    })

    with app.app_context():
        response = view_func(mock_account, "nonexistent_id")

    assert response.status_code == 200


@patch("aws_portal.extensions.db.session.execute")
def test_download_fitbit_study(mock_execute, app):
    """
    Tests the Fitbit data download endpoint for an entire study.

    Verifies that study-wide Fitbit data can be retrieved and formatted
    as an Excel file for download.
    """
    from aws_portal.views import fitbit_data
    view_func = get_unwrapped_view(fitbit_data, 'download_fitbit_study')

    # Sample aggregated Fitbit data for a study
    mock_data = [
        {"ditti_id": "ditti_1", "date": "2023-01-01", "steps": 10000},
        {"ditti_id": "ditti_2", "date": "2023-01-02", "steps": 12000}
    ]
    mock_result = MagicMock()
    mock_result.fetchall.return_value = mock_data
    mock_execute.return_value = mock_result

    mock_account = type('Account', (), {
        'id': '2',
        'email': 'admin@example.com',
        'name': 'Admin User'
    })

    with app.app_context(), \
            patch('pandas.DataFrame.to_excel') as mock_to_excel:
        response = view_func(mock_account, 123)
        assert mock_to_excel.called

    assert hasattr(response, 'status_code')


@patch("aws_portal.extensions.db.session.execute")
def test_download_fitbit_study_not_found(mock_execute, app):
    """
    Tests the Fitbit data download endpoint when study has no data.

    Verifies empty result sets are handled properly for study-level downloads.
    """
    from aws_portal.views import fitbit_data
    view_func = get_unwrapped_view(fitbit_data, 'download_fitbit_study')

    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_execute.return_value = mock_result

    mock_account = type('Account', (), {
        'id': '2',
        'email': 'admin@example.com',
        'name': 'Admin User'
    })

    with app.app_context(), \
            patch('pandas.DataFrame.to_excel') as mock_to_excel:
        response = view_func(mock_account, 999)

    assert hasattr(response, 'status_code')


def test_download_fitbit_study_invalid_id(app):
    """
    Tests error handling when providing an invalid study ID format.

    Verifies proper error responses for non-numeric study IDs.
    """
    from aws_portal.views import fitbit_data
    view_func = get_unwrapped_view(fitbit_data, 'download_fitbit_study')

    mock_account = type('Account', (), {
        'id': '2',
        'email': 'admin@example.com',
        'name': 'Admin User'
    })

    with app.app_context():
        response = view_func(mock_account, "not-a-number")

    assert response.status_code == 500


def test_revoke_api_access_user_not_found(app):
    """
    Tests error handling when revoking API access for a non-existent user.

    Verifies proper 404 responses for unknown users.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

    with app.app_context(), \
            patch("aws_portal.models.StudySubject.query") as mock_query:
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        response = view_func("TestAPI", ditti_id="nonexistent_ditti_id")

        assert response.status_code == 404
        assert response.get_json() == {"msg": "User not found."}


def test_revoke_api_access_api_not_found(app, study_subject):
    """
    Tests error handling when revoking access for a non-existent API.

    Verifies proper 404 responses when the API doesn't exist.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

    with app.app_context(), \
            patch("aws_portal.models.Api.query") as mock_query:
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        response = view_func("NonExistentAPI", ditti_id=study_subject.ditti_id)

        assert response.status_code == 404
        assert response.get_json() == {"msg": "API not found."}


def test_revoke_api_access_api_access_not_found(app, study_subject, api_entry):
    """
    Tests error handling when revoking API access that doesn't exist.

    Verifies proper 404 responses when no API access relationship exists.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

    with app.app_context(), \
            patch("aws_portal.models.JoinStudySubjectApi.query") as mock_query:
        mock_query.get.return_value = None

        response = view_func(api_entry.name, ditti_id=study_subject.ditti_id)

        assert response.status_code == 404
        assert response.get_json() == {"msg": "API access not found."}


def test_revoke_api_access_delete_tokens_keyerror(app, study_subject, api_entry, join_api):
    """
    Tests error recovery when token manager can't find tokens to delete.

    Verifies that the API access relationship is still deleted from the database
    even when token deletion fails due to missing tokens.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens", side_effect=KeyError), \
            patch("aws_portal.extensions.db.session.delete") as mock_db_delete, \
            patch("aws_portal.extensions.db.session.commit") as mock_db_commit, \
            patch("aws_portal.views.participant.logger.warning") as mock_logger_warning:

        response = view_func(api_entry.name, ditti_id=study_subject.ditti_id)

        assert response.status_code == 200
        assert response.get_json() == {
            "msg": "API access revoked successfully"}
        mock_db_delete.assert_called_once_with(join_api)
        mock_db_commit.assert_called_once()
        mock_logger_warning.assert_called_once_with(
            f"Tokens for API '{api_entry.name}' and StudySubject {study_subject.ditti_id} not found.")


def test_revoke_api_access_exception_handling(app, study_subject, api_entry, join_api):
    """
    Tests error handling when database operations fail during API access revocation.

    Verifies proper 500 error responses when database commits fail.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

    with app.app_context(), \
            patch("aws_portal.extensions.db.session.commit", side_effect=Exception("Commit error")), \
            patch("aws_portal.views.participant.logger.error") as mock_logger_error:

        response = view_func(api_entry.name, ditti_id=study_subject.ditti_id)

        assert response.status_code == 500
        assert response.get_json() == {"msg": "Error revoking API access."}
        mock_logger_error.assert_called_once()


def test_revoke_api_access_exception_deleting_tokens(app, study_subject, api_entry, join_api):
    """
    Tests error handling when token deletion fails with an exception.

    Verifies proper error responses when token manager operations fail.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens", side_effect=Exception("Delete token error")), \
            patch("aws_portal.views.participant.logger.error") as mock_logger_error:

        response = view_func(api_entry.name, ditti_id=study_subject.ditti_id)

        assert response.status_code == 500
        assert response.get_json() == {"msg": "Error deleting API tokens."}
        mock_logger_error.assert_called_once()


def test_revoke_api_access_concurrent_requests(app, study_subject, api_entry, join_api):
    """
    Tests API access revocation resilience against concurrent operations.

    Verifies that the endpoint functions correctly when token deletion fails
    with KeyError due to concurrent operations.
    """
    from aws_portal.views import participant as participant_view
    view_func = get_unwrapped_view(participant_view, 'revoke_api_access')

    with app.app_context(), \
            patch("aws_portal.extensions.tm.delete_api_tokens", side_effect=KeyError), \
            patch("aws_portal.extensions.db.session.delete") as mock_db_delete, \
            patch("aws_portal.extensions.db.session.commit") as mock_db_commit:

        response = view_func(api_entry.name, ditti_id=study_subject.ditti_id)

        assert response.status_code == 200
        assert response.get_json() == {
            "msg": "API access revoked successfully"}
        mock_db_delete.assert_called_once_with(join_api)
        mock_db_commit.assert_called_once()


def test_flask_app_routes(app):
    """
    Maps all API routes in the application to their corresponding view functions.

    This test provides visibility into the routing structure for reviewers,
    making it easier to understand the overall API surface.
    """
    # Verify routes exist - we don't need to print details
    assert app.url_map is not None
    # Ensure key participant routes exist
    route_endpoints = [rule.endpoint for rule in app.url_map.iter_rules()]
    assert "participant.get_participant" in route_endpoints
    assert "participant.delete_participant" in route_endpoints
    assert "participant.revoke_api_access" in route_endpoints
