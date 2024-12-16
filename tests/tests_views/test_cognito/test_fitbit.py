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
    unique_ditti_id = f"ditti_{uuid.uuid4()}"
    subject = StudySubject(
        created_on=datetime.utcnow(),
        ditti_id=unique_ditti_id,
        is_archived=False
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
    # If it doesn't exist, create one
    if not fitbit_api:
        fitbit_api = Api(name="Fitbit", is_archived=False)
        db.session.add(fitbit_api)
        db.session.commit()
    return fitbit_api


@pytest.fixture
def auth_client(client, study_subject):
    """
    Fixture to provide an authenticated client.
    Sets "id_token" and "access_token" cookies and mocks "verify_token" to return a valid ditti_id.
    """
    # Set authentication cookies
    client.set_cookie("id_token", "fake_id_token")
    client.set_cookie("access_token", "fake_access_token")

    # Mock "verify_token" to return claims with cognito:username = study_subject.ditti_id
    with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
        def verify_token_side_effect(participant_pool, token, token_use="id"):
            if participant_pool is not True:
                raise ValueError(
                    "Only participant pool is supported at this time.")
            if token_use == "access":
                return {"token_use": "access", "client_id": "test_client_id"}
            elif token_use == "id":
                return {
                    "token_use": "id",
                    "cognito:username": study_subject.ditti_id,
                    "client_id": "test_client_id"
                }
            else:
                raise InvalidTokenError("Invalid token_use")

        mock_verify_token.side_effect = verify_token_side_effect
        yield client


def test_fitbit_authorize_success(app, auth_client, study_subject, fitbit_api):
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

            response = auth_client.get("/cognito/fitbit/authorize")

            # Check that the response is a redirect (302)
            assert response.status_code == 302
            assert response.headers["Location"] == "https://www.fitbit.com/oauth2/authorize?params"

            # Check that code_verifier and state are stored in session
            with auth_client.session_transaction() as sess:
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


def test_fitbit_callback_success_new_association(app, auth_client, study_subject, fitbit_api):
    # Set session variables for OAuth
    with auth_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"

    # Prepare query parameters
    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        # Mock token endpoint response
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

            # Mock tm.add_or_update_api_token
            with patch.object(tm, "add_or_update_api_token") as mock_add_update_api_token:
                response = auth_client.get(
                    "/cognito/fitbit/callback", query_string=query_params)

                # Check redirection to success page
                assert response.status_code == 302
                expected_redirect_url = app.config.get(
                    "API_AUTHORIZE_REDIRECT", "/dashboard")
                assert response.headers["Location"] == expected_redirect_url

                # Verify that tokens are stored
                mock_add_update_api_token.assert_called_once()
                args, kwargs = mock_add_update_api_token.call_args
                assert kwargs["api_name"] == "Fitbit", f"Expected api_name 'Fitbit', got {
                    kwargs['api_name']}"
                assert kwargs["ditti_id"] == study_subject.ditti_id, \
                    f"Expected ditti_id {study_subject.ditti_id}, got {
                        kwargs['ditti_id']}"
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


def test_fitbit_callback_state_mismatch(app, auth_client, study_subject):
    with auth_client.session_transaction() as sess:
        sess["oauth_state"] = "correct_state"
        sess["oauth_code_verifier"] = "test_code_verifier"

    query_params = {
        "state": "incorrect_state",
        "code": "test_code"
    }

    response = auth_client.get(
        "/cognito/fitbit/callback", query_string=query_params)
    # Expect a 400 Bad Request due to state mismatch
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Invalid authorization state."}


def test_fitbit_callback_missing_code(app, auth_client, study_subject):
    with auth_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"

    # No "code" in query params
    query_params = {
        "state": "test_state"
    }

    response = auth_client.get(
        "/cognito/fitbit/callback", query_string=query_params)
    # Expect a 400 Bad Request due to missing authorization code
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Authorization code missing."}


def test_fitbit_callback_token_exchange_failure(app, auth_client, study_subject):
    with auth_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"

    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        with patch("aws_portal.views.cognito.fitbit.requests.post") as mock_post:
            mock_post.side_effect = Exception("Network error")

            response = auth_client.get(
                "/cognito/fitbit/callback", query_string=query_params)
            # Expect a 400 due to token exchange failure
            assert response.status_code == 400
            # The updated code logs a generic error; check for "Failed to retrieve Fitbit tokens."
            assert response.get_json() == {
                "msg": "Failed to retrieve Fitbit tokens."}


def test_fitbit_callback_missing_fitbit_api_entry(app, auth_client, study_subject):
    with auth_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"

    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

        # Mock a successful token response
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

            # Mock Api.query to return None for Fitbit
            with patch("aws_portal.models.Api.query") as mock_api_query:
                mock_api_query.filter_by.return_value.first.return_value = None

                response = auth_client.get(
                    "/cognito/fitbit/callback", query_string=query_params)
                # Expect 500 since Fitbit API not configured
                assert response.status_code == 500
                assert response.get_json() == {
                    "msg": "Fitbit integration not available."}


def test_fitbit_callback_error_storing_tokens(app, auth_client, study_subject, fitbit_api):
    with auth_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"

    query_params = {
        "state": "test_state",
        "code": "test_code"
    }

    with patch.object(WebApplicationClient, "prepare_token_request") as mock_prepare_token_request:
        mock_prepare_token_request.return_value = (
            "https://api.fitbit.com/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=authorization_code&code=test_code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&code_verifier=test_code_verifier"
        )

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

            # Mock add_or_update_api_token to raise an exception
            with patch.object(tm, "add_or_update_api_token", side_effect=Exception("AWS Secrets Manager error")):
                response = auth_client.get(
                    "/cognito/fitbit/callback", query_string=query_params)
                # Expect 500 due to error storing tokens
                assert response.status_code == 500
                assert response.get_json() == {
                    "msg": "Failed to store Fitbit tokens."}


def test_fitbit_authorize_unauthenticated(client):
    # No authentication cookies set
    response = client.get("/cognito/fitbit/authorize")
    # Expect unauthorized response since decorator requires auth tokens
    assert response.status_code == 401
    assert response.get_json() == {"msg": "Missing authentication tokens."}


def test_fitbit_authorize_concurrent_requests(app, auth_client):
    with patch("aws_portal.views.cognito.fitbit.generate_code_verifier") as mock_gen_verifier, \
            patch("aws_portal.views.cognito.fitbit.create_code_challenge") as mock_code_challenge, \
            patch("aws_portal.views.cognito.fitbit.os.urandom") as mock_urandom:

        mock_gen_verifier.return_value = "test_code_verifier"
        mock_code_challenge.return_value = "test_code_challenge"
        mock_urandom.return_value = b"\x00" * 32

        # Simulate two concurrent requests
        response1 = auth_client.get("/cognito/fitbit/authorize")
        response2 = auth_client.get("/cognito/fitbit/authorize")

        assert response1.status_code == 302
        assert response2.status_code == 302

        with auth_client.session_transaction() as sess:
            # The last request's session data should prevail
            assert sess["oauth_code_verifier"] == "test_code_verifier"
            assert sess["oauth_state"] == base64.urlsafe_b64encode(
                b"\x00" * 32).rstrip(b"=").decode("utf-8")


def test_fitbit_callback_token_scope_validation(app, auth_client, study_subject, fitbit_api):
    with auth_client.session_transaction() as sess:
        sess["oauth_state"] = "test_state"
        sess["oauth_code_verifier"] = "test_code_verifier"

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
            def add_update_side_effect(api_name, ditti_id, tokens):
                tokens["expires_at"] = pytest.approx(
                    tokens["expires_at"], rel=1e-2)

            mock_add_update_api_token.side_effect = add_update_side_effect

            response = auth_client.get(
                "/cognito/fitbit/callback", query_string=query_params)

            assert response.status_code == 302
            join_entry = JoinStudySubjectApi.query.filter_by(
                study_subject_id=study_subject.id,
                api_id=fitbit_api.id
            ).first()
            assert join_entry.scope == ["sleep"]


def test_fitbit_sleep_list(app, auth_client, study_subject, fitbit_api):
    # Link the participant to the Fitbit API if not already linked
    join_entry = JoinStudySubjectApi.query.filter_by(
        study_subject_id=study_subject.id,
        api_id=fitbit_api.id
    ).first()
    if not join_entry:
        join_entry = JoinStudySubjectApi(
            study_subject_id=study_subject.id,
            api_id=fitbit_api.id,
            api_user_uuid="fitbit_user_id",
            scope=["sleep"]
        )
        db.session.add(join_entry)
        db.session.commit()

    with patch("aws_portal.views.cognito.fitbit.get_fitbit_oauth_session") as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.get.return_value.json.return_value = {"sleep": []}

        response = auth_client.get("/cognito/fitbit/sleep_list")
        assert response.status_code == 200
        data = response.get_json()
        assert "sleep" in data
        assert data["sleep"] == []


def test_fitbit_sleep_list_not_linked(app, auth_client, study_subject, fitbit_api):
    # Ensure no JoinStudySubjectApi entry
    JoinStudySubjectApi.query.filter_by(
        study_subject_id=study_subject.id,
        api_id=fitbit_api.id
    ).delete()
    db.session.commit()

    response = auth_client.get("/cognito/fitbit/sleep_list")
    assert response.status_code == 401
    assert response.get_json() == {
        "msg": "Fitbit API not linked to your account."}
