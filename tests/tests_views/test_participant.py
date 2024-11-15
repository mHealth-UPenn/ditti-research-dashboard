import time
import uuid
from datetime import datetime
import pytest
from jwt.exceptions import InvalidTokenError
from unittest.mock import MagicMock, patch
from aws_portal.extensions import db
from aws_portal.models import Api, JoinStudySubjectApi, StudySubject


@pytest.fixture
def study_subject():
    """
    Fixture to provide a new unique study subject.
    """
    unique_email = f"user_{uuid.uuid4()}@example.com"
    subject = StudySubject(
        created_on=datetime.utcnow(),
        email=unique_email,
        is_confirmed=True,
        is_archived=False
    )
    db.session.add(subject)
    db.session.commit()
    return subject


@pytest.fixture
def api_entry():
    """
    Fixture to provide an API entry.
    """
    api = Api(name="TestAPI", is_archived=False)
    db.session.add(api)
    db.session.commit()
    return api


@pytest.fixture
def join_api(study_subject, api_entry):
    """
    Fixture to provide a JoinStudySubjectApi entry.
    """
    join_entry = JoinStudySubjectApi(
        study_subject_id=study_subject.id,
        api_id=api_entry.id,
        api_user_uuid="test_uuid",
        scope=["read", "write"],
        access_key_uuid="access_uuid",
        refresh_key_uuid="refresh_uuid"
    )
    db.session.add(join_entry)
    db.session.commit()
    return join_entry


@pytest.fixture
def authenticated_client(client, study_subject):
    """
    Fixture to provide an authenticated client.
    Sets "id_token" and "access_token" cookies and mocks "verify_token" to accept them.
    """
    # Set the authentication cookies
    client.set_cookie("id_token", "fake_id_token")
    client.set_cookie("access_token", "fake_access_token")

    # Mock "verify_token" to accept the fake tokens
    with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
        def verify_token_side_effect(participant_pool, token, token_use="id"):
            if participant_pool is not True:
                raise ValueError(
                    "Only participant pool is supported at this time.")
            if token_use == "access":
                return {"token_use": "access", "cognito:username": study_subject.email}
            elif token_use == "id":
                return {"token_use": "id", "cognito:username": study_subject.email}
            else:
                raise InvalidTokenError("Invalid token_use")

        mock_verify_token.side_effect = verify_token_side_effect

        yield client


def test_get_participant_success(authenticated_client, study_subject, join_api, api_entry):
    """
    Test successful retrieval of participant data.
    """
    # Mock serialize_participant to return expected data
    expected_data = {
        "email": study_subject.email,
        "user_id": study_subject.id,
        "apis": [
            {
                "api_name": api_entry.name,
                "scope": join_api.scope,
                "expires_at": None
            }
        ],
        "studies": []
    }

    with patch("aws_portal.views.participant.serialize_participant") as mock_serialize, \
            patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:

        # Mock jwt.decode to return a valid claims dictionary with cognito:username
        mock_jwt_decode.return_value = {
            "cognito:username": study_subject.email}

        mock_serialize.return_value = expected_data

        response = authenticated_client.get("/participant")

        assert response.status_code == 200
        assert response.get_json() == expected_data
        mock_serialize.assert_called_once_with(study_subject)


def test_get_participant_missing_id_token(client):
    """
    Test retrieval of participant data with missing ID token.
    """
    response = client.get("/participant")
    assert response.status_code == 401
    assert response.get_json() == {"msg": "Missing authentication tokens."}


def test_get_participant_missing_email(authenticated_client):
    """
    Test retrieval of participant data when email is missing in ID token.
    """
    with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {}  # No email in claims

        response = authenticated_client.get("/participant")

        assert response.status_code == 400
        assert response.get_json() == {
            "msg": "cognito:username not found in token."}


def test_get_participant_user_not_found(authenticated_client):
    """
    Test retrieval of participant data when user is not found or is archived.
    """
    with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
        # Mock jwt.decode to return a valid claims dictionary with nonexistent cognito:username
        mock_jwt_decode.return_value = {"cognito:username": "dne@email.com"}
        response = authenticated_client.get("/participant")
        assert response.status_code == 404
        assert response.get_json() == {"msg": "User not found or is archived."}


def test_get_participant_exception_handling(authenticated_client, study_subject):
    """
    Test retrieval of participant data when an exception occurs.
    """
    with patch("aws_portal.views.participant.StudySubject.query") as mock_query:
        mock_query.filter_by.side_effect = Exception("Database error")

        # Mock jwt.decode to return a valid claims dictionary with cognito:username
        with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {
                "cognito:username": study_subject.email}

            response = authenticated_client.get("/participant")

            assert response.status_code == 500
            assert response.get_json() == {
                "msg": "Unexpected server error."}


def test_revoke_api_access_success(authenticated_client, study_subject, api_entry, join_api):
    """
    Test successful revocation of API access.
    """
    response_data = {"msg": "API access revoked successfully"}

    with patch("aws_portal.views.participant.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("aws_portal.views.participant.db.session.delete") as mock_db_delete, \
            patch("aws_portal.views.participant.db.session.commit") as mock_db_commit:

        # Mock jwt.decode to return a valid claims dictionary with cognito:username
        with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {
                "cognito:username": study_subject.email}

            response = authenticated_client.delete(
                f"/participant/api/{api_entry.name}")

            assert response.status_code == 200
            assert response.get_json() == response_data
            mock_delete_tokens.assert_called_once_with(
                api_name=api_entry.name, study_subject_id=study_subject.id)
            mock_db_delete.assert_called_once_with(join_api)
            mock_db_commit.assert_called_once()


def test_revoke_api_access_missing_id_token(client):
    """
    Test revocation of API access with missing ID token.
    """
    response = client.delete("/participant/api/TestAPI")
    assert response.status_code == 401
    assert response.get_json() == {"msg": "Missing authentication tokens."}


def test_revoke_api_access_missing_email(authenticated_client):
    """
    Test revocation of API access when email is missing in ID token.
    """
    with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {}  # No email in claims

        response = authenticated_client.delete("/participant/api/TestAPI")

        assert response.status_code == 400
        assert response.get_json() == {
            "msg": "cognito:username not found in token"}


def test_revoke_api_access_user_not_found(authenticated_client):
    """
    Test revocation of API access when user is not found.
    """
    with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
        # Mock jwt.decode to return a valid claims dictionary with nonexistent cognito:username
        mock_jwt_decode.return_value = {"cognito:username": "dne@email.com"}
        response = authenticated_client.delete("/participant/api/TestAPI")
        assert response.status_code == 404
        assert response.get_json() == {"msg": "User not found"}


def test_revoke_api_access_api_not_found(authenticated_client, study_subject):
    """
    Test revocation of API access when API is not found.
    """
    # Mock jwt.decode to return a valid claims dictionary with cognito:username
    with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {
            "cognito:username": study_subject.email}

        response = authenticated_client.delete(
            "/participant/api/NonExistentAPI")
        assert response.status_code == 404
        assert response.get_json() == {"msg": "API not found"}


def test_revoke_api_access_api_access_not_found(authenticated_client, study_subject, api_entry):
    """
    Test revocation of API access when API access is not found.
    """
    # Mock jwt.decode to return a valid claims dictionary with cognito:username
    with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {
            "cognito:username": study_subject.email}

        response = authenticated_client.delete(
            f"/participant/api/{api_entry.name}")
        assert response.status_code == 404
        assert response.get_json() == {"msg": "API access not found"}


def test_revoke_api_access_delete_tokens_keyerror(authenticated_client, study_subject, api_entry, join_api):
    """
    Test revocation of API access when delete_api_tokens raises KeyError.
    """
    with patch("aws_portal.views.participant.tm.delete_api_tokens", side_effect=KeyError), \
            patch("aws_portal.views.participant.db.session.delete") as mock_db_delete, \
            patch("aws_portal.views.participant.db.session.commit") as mock_db_commit, \
            patch("aws_portal.views.participant.logger.warning") as mock_logger_warning:

        # Mock jwt.decode to return a valid claims dictionary with cognito:username
        with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {
                "cognito:username": study_subject.email}

            response = authenticated_client.delete(
                f"/participant/api/{api_entry.name}")

            assert response.status_code == 200
            assert response.get_json() == {
                "msg": "API access revoked successfully"}
            mock_db_delete.assert_called_once_with(join_api)
            mock_db_commit.assert_called_once()
            mock_logger_warning.assert_called_once_with(
                f"Tokens for API '{api_entry.name}' and StudySubject ID {
                    study_subject.id} not found."
            )


def test_revoke_api_access_exception_handling(authenticated_client, study_subject, api_entry, join_api):
    """
    Test revocation of API access when an exception occurs.
    """
    with patch("aws_portal.views.participant.db.session.commit", side_effect=Exception("Commit error")), \
            patch("aws_portal.views.participant.logger.error") as mock_logger_error:

        # Mock jwt.decode to return a valid claims dictionary with cognito:username
        with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {
                "cognito:username": study_subject.email}

            response = authenticated_client.delete(
                f"/participant/api/{api_entry.name}")

            assert response.status_code == 500
            assert response.get_json() == {"msg": "Error revoking API access"}
            mock_logger_error.assert_called_once_with(
                "Error revoking API access: Commit error")


def test_delete_participant_success(app, delete_admin, study_subject, join_api, api_entry):
    """
    Test successful deletion of participant account.
    """
    with patch("aws_portal.views.participant.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("aws_portal.views.participant.db.session.delete") as mock_db_delete, \
            patch("aws_portal.views.participant.db.session.commit") as mock_db_commit, \
            patch("aws_portal.views.participant.boto3.client") as mock_boto_client:

        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        response = delete_admin(
            f"/participant/{study_subject.email}", query_string={"app": 1})

        assert response.status_code == 200
        assert response.get_json() == {
            "msg": "Account deleted successfully."}

        # Verify tokens deletion for each API
        mock_delete_tokens.assert_called_once_with(
            api_name=api_entry.name, study_subject_id=study_subject.id)

        # Verify API access removal
        mock_db_delete.assert_called_once_with(join_api)

        # Verify StudySubject is archived
        assert study_subject.is_archived == True

        # Verify database commit
        mock_db_commit.assert_called_once()

        # Verify Cognito deletion
        mock_cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=app.config["COGNITO_PARTICIPANT_USER_POOL_ID"],
            Username=study_subject.email
        )

        # Verify cookies are cleared
        assert response.headers.get_all("Set-Cookie")


def test_delete_participant_not_admin(app, delete, study_subject):
    """
    Test deletion of participant account without admin permissions.
    """
    response = delete(
        f"/participant/{study_subject.email}", query_string={"app": 1})
    assert response.status_code == 403
    assert response.get_json() == {"msg": "Unauthorized Request"}


def test_delete_participant_missing_username(app, delete_admin, study_subject):
    """
    Test deletion of participant account when username is missing in route.
    """
    with patch("aws_portal.views.participant.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("aws_portal.views.participant.db.session.delete") as mock_db_delete, \
            patch("aws_portal.views.participant.db.session.commit") as mock_db_commit, \
            patch("aws_portal.views.participant.boto3.client") as mock_boto_client:
        response = delete_admin(
            f"/participant/", query_string={"app": 1})

        assert response.status_code == 405


def test_delete_participant_user_not_found(app, delete_admin):
    """
    Test deletion of participant account when user is not found or already archived.
    """
    with patch("aws_portal.views.participant.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("aws_portal.views.participant.db.session.delete") as mock_db_delete, \
            patch("aws_portal.views.participant.db.session.commit") as mock_db_commit, \
            patch("aws_portal.views.participant.boto3.client") as mock_boto_client:
        response = delete_admin(
            f"/participant/username_dne", query_string={"app": 1})
        assert response.status_code == 404
        assert response.get_json() == {
            "msg": "User not found or already archived."}


def test_delete_participant_exception_deleting_tokens(app, delete_admin, study_subject, join_api):
    """
    Test deletion of participant account when deleting tokens raises an exception.
    """
    with patch("aws_portal.views.participant.tm.delete_api_tokens", side_effect=Exception("Token deletion error")):
        response = delete_admin(
            f"/participant/{study_subject.email}", query_string={"app": 1})

        assert response.status_code == 500
        assert response.get_json() == {
            "msg": "Error deleting API tokens."}


def test_delete_participant_cognito_exception(app, delete_admin, study_subject):
    """
    Test deletion of participant account when Cognito deletion raises a general exception.
    """
    with patch("aws_portal.views.participant.boto3.client") as mock_boto_client:

        mock_cognito_client = MagicMock()
        mock_cognito_client.admin_delete_user.side_effect = Exception(
            "Cognito error")
        mock_boto_client.return_value = mock_cognito_client

        response = delete_admin(
            f"/participant/{study_subject.email}", query_string={"app": 1})

        assert response.status_code == 500
        assert response.get_json() == {
            "msg": "Error deleting account."}


def test_delete_participant_exception_handling(app, delete_admin, study_subject):
    """
    Test deletion of participant account when an exception occurs during the process.
    """
    with patch("aws_portal.views.participant.db.session.commit", side_effect=Exception("Commit error")):

        response = delete_admin(
            f"/participant/{study_subject.email}", query_string={"app": 1})

        assert response.status_code == 500
        assert response.get_json() == {
            "msg": "Error deleting account."}


def test_revoke_api_access_exception_deleting_tokens(authenticated_client, study_subject, api_entry, join_api):
    """
    Test revocation of API access when an exception occurs during token deletion.
    """
    with patch("aws_portal.views.participant.tm.delete_api_tokens", side_effect=Exception("Delete token error")), \
            patch("aws_portal.views.participant.logger.error") as mock_logger_error:

        # Mock jwt.decode to return a valid claims dictionary with cognito:username
        with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {
                "cognito:username": study_subject.email}

            response = authenticated_client.delete(
                f"/participant/api/{api_entry.name}")

            assert response.status_code == 500
            assert response.get_json() == {
                "msg": "Error revoking API access"}
            mock_logger_error.assert_called_once_with(
                "Error revoking API access: Delete token error")


def test_get_participant_serialization(authenticated_client, study_subject, join_api, api_entry):
    """
    Test that the get_participant endpoint correctly serializes participant data.
    """
    # Mock serialize_participant to ensure it's called correctly
    with patch("aws_portal.views.participant.serialize_participant") as mock_serialize, \
            patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:

        mock_jwt_decode.return_value = {
            "cognito:username": study_subject.email}
        mock_serialize.return_value = {
            "email": study_subject.email,
            "user_id": study_subject.id,
            "apis": [
                {
                    "api_name": api_entry.name,
                    "scope": join_api.scope,
                    "expires_at": None
                }
            ],
            "studies": []
        }

        response = authenticated_client.get("/participant")

        assert response.status_code == 200
        mock_serialize.assert_called_once_with(study_subject)
        assert response.get_json()["email"] == study_subject.email
        assert response.get_json()["user_id"] == study_subject.id
        assert len(response.get_json()["apis"]) == 1
        assert response.get_json()["apis"][0]["api_name"] == api_entry.name


def test_delete_participant_remove_api_access(app, delete_admin, study_subject, join_api, api_entry):
    """
    Test that the delete_participant endpoint removes API access entries.
    """
    with patch("aws_portal.views.participant.tm.delete_api_tokens") as mock_delete_tokens, \
            patch("aws_portal.views.participant.db.session.delete") as mock_db_delete, \
            patch("aws_portal.views.participant.db.session.commit") as mock_db_commit, \
            patch("aws_portal.views.participant.boto3.client") as mock_boto_client:

        mock_cognito_client = MagicMock()
        # Configure the delete_user method to return a successful response
        mock_cognito_client.delete_user.return_value = {}
        mock_boto_client.return_value = mock_cognito_client

        response = delete_admin(
            f"/participant/{study_subject.email}", query_string={"app": 1})

        assert response.status_code == 200
        assert response.get_json() == {
            "msg": "Account deleted successfully."}

        # Verify tokens deletion for each API
        mock_delete_tokens.assert_called_once_with(
            api_name=api_entry.name, study_subject_id=study_subject.id)

        # Verify API access removal
        mock_db_delete.assert_called_once_with(join_api)

        # Verify StudySubject is archived
        assert study_subject.is_archived == True

        # Verify database commit
        mock_db_commit.assert_called_once()

        # Verify Cognito deletion
        mock_cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=app.config["COGNITO_PARTICIPANT_USER_POOL_ID"],
            Username=study_subject.email
        )

        # Verify cookies are cleared
        set_cookie_headers = response.headers.get_all("Set-Cookie")
        assert any(
            "id_token=; " in header for header in set_cookie_headers)
        assert any(
            "access_token=; " in header for header in set_cookie_headers)
        assert any(
            "refresh_token=; " in header for header in set_cookie_headers)


def test_revoke_api_access_concurrent_requests(authenticated_client, study_subject, api_entry, join_api):
    """
    Test handling of concurrent API access revocation requests.
    """
    # Set the cognito:username in the token for authenticated client
    with patch("aws_portal.views.participant.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {
            "cognito:username": study_subject.email}

        # Send the first DELETE request
        response1 = authenticated_client.delete(
            f"/participant/api/{api_entry.name}")

        # Introduce a short delay to allow database to fully commit the deletion
        time.sleep(0.1)

        # Send the second DELETE request
        response2 = authenticated_client.delete(
            f"/participant/api/{api_entry.name}")

        # Assert that the first request was successful
        assert response1.status_code == 200
        assert response1.get_json() == {
            "msg": "API access revoked successfully"}

        # Assert that the second request fails as the API access no longer exists
        assert response2.status_code == 404
        assert response2.get_json() == {"msg": "API access not found"}
