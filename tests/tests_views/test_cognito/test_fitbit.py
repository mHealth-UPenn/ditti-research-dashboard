import pytest
from unittest.mock import patch, MagicMock
from aws_portal.models import Api, JoinStudySubjectApi, StudySubject
from aws_portal.extensions import db, tm
from oauthlib.oauth2 import WebApplicationClient
import base64
import uuid
import json
from datetime import datetime
from jwt.exceptions import InvalidTokenError


@pytest.fixture
def study_subject():
    """
    Fixture to provide a new unique study subject.
    """
    unique_username = f"username_{uuid.uuid4()}"
    subject = StudySubject(
        created_on=datetime.utcnow(),
        email=unique_username,
        is_confirmed=True
    )
    db.session.add(subject)
    db.session.commit()
    return subject


@pytest.fixture
def fitbit_api():
    """
    Fixture to provide the Fitbit API.
    """
    fitbit_api = Api.query.filter_by(name="Fitbit").first()
    return fitbit_api


@pytest.fixture
def authenticated_client(client):
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
                return {"token_use": "access", "client_id": "test_client_id"}
            elif token_use == "id":
                return {"token_use": "id", "client_id": "test_client_id"}
            else:
                raise InvalidTokenError("Invalid token_use")

        mock_verify_token.side_effect = verify_token_side_effect

        yield client


def test_fitbit_authorize_success(app, authenticated_client, study_subject, fitbit_api):
    # Set session variables via authenticated_client.session_transaction()
    with authenticated_client.session_transaction() as sess:
        sess["study_subject_id"] = study_subject.id

    # Mock generate_code_verifier and create_code_challenge
    with patch("aws_portal.views.cognito.fitbit.generate_code_verifier") as mock_gen_verifier, \
            patch("aws_portal.views.cognito.fitbit.create_code_challenge") as mock_code_challenge, \
            patch("aws_portal.views.cognito.fitbit.os.urandom") as mock_urandom:

        mock_gen_verifier.return_value = "test_code_verifier"
        mock_code_challenge.return_value = "test_code_challenge"
        mock_urandom.return_value = b"\x00" * 32  # Mock 32 bytes of zeros for state

        expected_state = base64.urlsafe_b64encode(
            b"\x00" * 32).rstrip(b"=").decode("utf-8")

        # Mock WebApplicationClient.prepare_request_uri
        with patch.object(WebApplicationClient, "prepare_request_uri") as mock_prepare_uri:
            mock_prepare_uri.return_value = "https://www.fitbit.com/oauth2/authorize?params"

            response = authenticated_client.get("/cognito/fitbit/authorize")

            # Check that the response is a redirect (302)
            assert response.status_code == 302
            assert response.headers["Location"] == "https://www.fitbit.com/oauth2/authorize?params"

            # Check that code_verifier and state are stored in session
            with authenticated_client.session_transaction() as sess:
                assert sess["oauth_code_verifier"] == "test_code_verifier"
                assert sess["oauth_state"] == expected_state

            # Verify that prepare_request_uri was called with correct parameters
            mock_prepare_uri.assert_called_once()
            args, kwargs = mock_prepare_uri.call_args
            assert args[0] == "https://www.fitbit.com/oauth2/authorize"
            assert kwargs["redirect_uri"] == app.config["FITBIT_REDIRECT_URI"]
            assert kwargs["scope"] == ["sleep"]
            assert kwargs["state"] == expected_state
            assert kwargs["code_challenge"] == "test_code_challenge"
            assert kwargs["code_challenge_method"] == "S256"


def test_fitbit_authorize_missing_study_subject_id(app, authenticated_client):
    # Do not set study_subject_id in session
    with authenticated_client.session_transaction() as sess:
        pass  # No study_subject_id

    response = authenticated_client.get("/cognito/fitbit/authorize")

    # Expect a redirect (302) to Fitbit's authorization URL
    assert response.status_code == 302
    assert "https://www.fitbit.com/oauth2/authorize" in response.headers["Location"]


def test_fitbit_callback_success_new_association(app, authenticated_client, study_subject, fitbit_api):
    # Set session variables
    with authenticated_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"
        sess["study_subject_id"] = study_subject.id

    # Prepare query parameters
    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    # Mock WebApplicationClient.prepare_token_request
    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        # Mock requests.post to token endpoint
        with patch("aws_portal.views.cognito.fitbit.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.text = json.dumps({
                "access_token": "access_token_value",
                "refresh_token": "refresh_token_value",
                "expires_in": 28800,
                "user_id": "fitbit_user_id",
                "scope": "sleep"
            })
            mock_post.return_value = mock_response

            # Mock sm.store_secret
            with patch.object(tm, "add_or_update_api_token") as mock_add_update_api_token:
                response = authenticated_client.get(
                    "/cognito/fitbit/callback", query_string=query_params)

                # Check redirection to success page
                assert response.status_code == 302
                expected_redirect_url = f"{app.config.get(
                    'CORS_ORIGINS', 'http://localhost:3000')}/participant"
                assert response.headers["Location"] == expected_redirect_url

                # Verify that tokens are stored using TokensManager
                mock_add_update_api_token.assert_called_once()
                args, kwargs = mock_add_update_api_token.call_args
                assert kwargs["api_name"] == "Fitbit", f"Expected api_name 'Fitbit', got {
                    kwargs['api_name']}"
                assert kwargs["study_subject_id"] == study_subject.id, \
                    f"Expected study_subject_id {study_subject.id}, got {
                        kwargs['study_subject_id']}"
                assert kwargs["tokens"]["access_token"] == "access_token_value", \
                    f"Expected access_token 'access_token_value', got {
                        kwargs['tokens']['access_token']}"
                assert kwargs["tokens"]["refresh_token"] == "refresh_token_value", \
                    f"Expected refresh_token 'refresh_token_value', got {
                        kwargs['tokens']['refresh_token']}"

                # Verify that JoinStudySubjectApi entry is created
                join_entry = JoinStudySubjectApi.query.filter_by(
                    study_subject_id=study_subject.id,
                    api_id=fitbit_api.id
                ).first()
                assert join_entry is not None
                assert join_entry.api_user_uuid == "fitbit_user_id"
                assert join_entry.scope == ["sleep"]


def test_fitbit_callback_state_mismatch(app, authenticated_client):
    # Set session state
    with authenticated_client.session_transaction() as sess:
        sess["oauth_state"] = "correct_state"
        sess["oauth_code_verifier"] = "test_code_verifier"
        sess["study_subject_id"] = 1

    # Prepare query parameters with mismatched state
    query_params = {
        "state": "incorrect_state",
        "code": "test_code"
    }

    response = authenticated_client.get(
        "/cognito/fitbit/callback", query_string=query_params)

    # Expect a 400 Bad Request due to state mismatch
    assert response.status_code == 400
    assert response.get_json() == {"msg": "State mismatch"}


def test_fitbit_callback_missing_code(app, authenticated_client):
    # Set session variables
    with authenticated_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"
        sess["study_subject_id"] = 1

    # Prepare query parameters without "code"
    query_params = {
        "state": "test_state",
        # "code" is omitted or set to None
    }

    response = authenticated_client.get(
        "/cognito/fitbit/callback", query_string=query_params)

    # Expect a 400 Bad Request due to missing authorization code
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Authorization code not found"}


def test_fitbit_callback_token_exchange_failure(app, authenticated_client):
    # Set session variables
    with authenticated_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"
        sess["study_subject_id"] = 1

    # Prepare query parameters
    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    # Mock WebApplicationClient.prepare_token_request
    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        # Mock requests.post to raise an exception
        with patch("aws_portal.views.cognito.fitbit.requests.post") as mock_post:
            mock_post.side_effect = Exception("Network error")

            response = authenticated_client.get(
                "/cognito/fitbit/callback", query_string=query_params)

            # Expect a 400 Bad Request due to token exchange failure
            assert response.status_code == 400
            assert response.get_json() == {
                "msg": "Failed to fetch token: Network error"}


def test_fitbit_callback_missing_fitbit_api_entry(app, authenticated_client):
    # Set session variables
    with authenticated_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"
        sess["study_subject_id"] = 1

    # Prepare query parameters
    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    # Mock WebApplicationClient.prepare_token_request
    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        # Mock requests.post to token endpoint
        with patch("aws_portal.views.cognito.fitbit.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.text = json.dumps({
                "access_token": "access_token_value",
                "refresh_token": "refresh_token_value",
                "expires_in": 28800,
                "user_id": "fitbit_user_id",
                "scope": "sleep"
            })
            mock_post.return_value = mock_response

            # Mock Api.query.filter_by(name="Fitbit").first() to return None
            with patch("aws_portal.models.Api.query") as mock_api_query:
                mock_api_query.filter_by.return_value.first.return_value = None

                response = authenticated_client.get(
                    "/cognito/fitbit/callback", query_string=query_params)

                # Expect a 500 Internal Server Error due to missing Fitbit API configuration
                assert response.status_code == 500
                assert response.get_json() == {
                    "msg": "Fitbit API not configured."}


def test_fitbit_callback_error_storing_tokens(app, authenticated_client, study_subject, fitbit_api):
    # Set session variables
    with authenticated_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"
        sess["study_subject_id"] = study_subject.id

    # Prepare query parameters
    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    # Mock WebApplicationClient.prepare_token_request
    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        # Mock requests.post to token endpoint
        with patch("aws_portal.views.cognito.fitbit.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.text = json.dumps({
                "access_token": "access_token_value",
                "refresh_token": "refresh_token_value",
                "expires_in": 28800,
                "user_id": "fitbit_user_id",
                "scope": "sleep"
            })
            mock_post.return_value = mock_response

            # Mock tm.add_or_update_api_token to raise an exception
            with patch.object(tm, "add_or_update_api_token", side_effect=Exception("AWS Secrets Manager error")) as mock_add_update_api_token:
                response = authenticated_client.get(
                    "/cognito/fitbit/callback", query_string=query_params)

                # Expect a 500 Internal Server Error due to error storing tokens
                assert response.status_code == 500
                assert response.get_json() == {
                    "msg": "Error storing tokens: AWS Secrets Manager error"}


# Test: Decorator behavior for unauthenticated requests
def test_fitbit_authorize_unauthenticated(client):
    # Do not set authentication cookies
    response = client.get("/cognito/fitbit/authorize")

    # Expect a redirect to the login page or an unauthorized response
    assert response.status_code in [302, 401]


# Test: Concurrent Requests
def test_fitbit_authorize_concurrent_requests(app, authenticated_client, study_subject):
    with patch("aws_portal.views.cognito.fitbit.generate_code_verifier") as mock_gen_verifier, \
            patch("aws_portal.views.cognito.fitbit.create_code_challenge") as mock_code_challenge, \
            patch("aws_portal.views.cognito.fitbit.os.urandom") as mock_urandom:

        mock_gen_verifier.return_value = "test_code_verifier"
        mock_code_challenge.return_value = "test_code_challenge"
        mock_urandom.return_value = b"\x00" * 32

        # Simulate two concurrent requests
        response1 = authenticated_client.get("/cognito/fitbit/authorize")
        response2 = authenticated_client.get("/cognito/fitbit/authorize")

        assert response1.status_code == 302
        assert response2.status_code == 302

        with authenticated_client.session_transaction() as sess:
            # The last request's session data should prevail
            assert sess["oauth_code_verifier"] == "test_code_verifier"
            assert sess["oauth_state"] == base64.urlsafe_b64encode(
                b"\x00" * 32).rstrip(b"=").decode("utf-8")


# Test: Token Scope Validation
def test_fitbit_callback_token_scope_validation(app, authenticated_client, study_subject, fitbit_api):
    with authenticated_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"
        sess["study_subject_id"] = study_subject.id

    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request, \
            patch("aws_portal.views.cognito.fitbit.requests.post") as mock_post:

        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = json.dumps({
            "access_token": "access_token_value",
            "refresh_token": "refresh_token_value",
            "expires_in": 28800,
            "user_id": "fitbit_user_id",
            "scope": "sleep"
        })
        mock_post.return_value = mock_response

        with patch.object(tm, "add_or_update_api_token") as mock_add_update_api_token:
            def add_update_side_effect(api_name, study_subject_id, tokens):
                tokens["expires_at"] = pytest.approx(
                    tokens["expires_at"], rel=1e-2)

            mock_add_update_api_token.side_effect = add_update_side_effect

            response = authenticated_client.get(
                "/cognito/fitbit/callback", query_string=query_params)

            assert response.status_code == 302
            join_entry = JoinStudySubjectApi.query.filter_by(
                study_subject_id=study_subject.id,
                api_id=fitbit_api.id
            ).first()
            assert join_entry.scope == ["sleep"]
