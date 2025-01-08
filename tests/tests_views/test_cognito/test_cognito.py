import json

import jwt
import pytest
import requests
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from urllib.parse import urlencode
from unittest.mock import MagicMock, patch
from aws_portal.extensions import db
from aws_portal.models import StudySubject


@pytest.fixture
def app(app):
    app.config["TESTING"] = True
    app.config["COGNITO_PARTICIPANT_REGION"] = "us-east-1"
    app.config["COGNITO_PARTICIPANT_USER_POOL_ID"] = "us-east-1_example"
    app.config["COGNITO_PARTICIPANT_CLIENT_ID"] = "example_client_id"
    app.config["COGNITO_PARTICIPANT_DOMAIN"] = "example.auth.us-east-1.amazoncognito.com"
    app.config["COGNITO_PARTICIPANT_REDIRECT_URI"] = "http://localhost:5000/cognito/callback"
    app.config["COGNITO_PARTICIPANT_LOGOUT_URI"] = "http://localhost:3000/login"
    return app


def parse_set_cookies(set_cookie_headers):
    """
    Parses a list of Set-Cookie headers and returns a dictionary of cookie names and values.
    """
    cookies = {}
    for sc in set_cookie_headers:
        cookie = SimpleCookie()
        cookie.load(sc)
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
    return cookies


@pytest.fixture
def client_with_cognito(client):
    return client


def test_login_success(app, client_with_cognito):
    with app.app_context():
        # Expected Cognito auth URL
        params = {
            "client_id": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
        }
        redirect_uri_encoded = urlencode(
            {"redirect_uri": app.config["COGNITO_PARTICIPANT_REDIRECT_URI"]}
        )
        cognito_auth_url = (
            f"https://{app.config['COGNITO_PARTICIPANT_DOMAIN']}/login?"
            f"client_id={app.config['COGNITO_PARTICIPANT_CLIENT_ID']}"
            f"&response_type=code&scope=openid&redirect_uri={
                redirect_uri_encoded}"
        )

        with patch(
            "aws_portal.views.cognito.cognito.build_cognito_url",
            return_value=cognito_auth_url,
        ) as mock_build_url:
            response = client_with_cognito.get("/cognito/login")
            assert response.status_code == 302
            assert response.headers["Location"] == cognito_auth_url
            mock_build_url.assert_called_once_with(True, "/login", params)


def test_cognito_callback_success_existing_user(app, client_with_cognito):
    with app.app_context():
        # Mock authorization code
        auth_code = "valid_auth_code"

        # Mock requests.post to token endpoint to return valid tokens
        with patch("aws_portal.views.cognito.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "id_token": "valid_id_token",
                "access_token": "valid_access_token",
            }
            mock_post.return_value = mock_response

            # Mock verify_token to return valid claims
            with patch(
                "aws_portal.views.cognito.cognito.verify_token"
            ) as mock_verify_token:
                mock_verify_token.return_value = {
                    "cognito:username": "existing_ditti_id",
                    "sub": "user123",
                    "iss": f"https://cognito-idp.{app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}",
                    "aud": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                    "token_use": "id",
                }

                # Ensure the user exists in the database
                study_subject = StudySubject(
                    created_on=datetime.now(timezone.utc),
                    ditti_id="existing_ditti_id",
                    is_archived=False,
                )
                db.session.add(study_subject)
                db.session.commit()

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}"
                )
                assert response.status_code == 302
                expected_redirect_url = app.config.get(
                    "CORS_ORIGINS", "http://localhost:3000"
                )
                assert response.headers["Location"] == expected_redirect_url

                # Check that cookies are set
                set_cookies = response.headers.getlist("Set-Cookie")
                cookies = parse_set_cookies(set_cookies)
                assert cookies.get("id_token") == "valid_id_token"
                assert cookies.get("access_token") == "valid_access_token"

                # Check that session is set
                with client_with_cognito.session_transaction() as sess:
                    assert sess["study_subject_id"] == study_subject.id


def test_cognito_callback_success_new_user(app, client_with_cognito):
    with app.app_context():
        # Mock authorization code
        auth_code = "valid_auth_code"

        # Mock requests.post to token endpoint to return valid tokens
        with patch("aws_portal.views.cognito.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "id_token": "valid_id_token",
                "access_token": "valid_access_token",
            }
            mock_post.return_value = mock_response

            # Mock verify_token to return valid claims
            with patch(
                "aws_portal.views.cognito.cognito.verify_token"
            ) as mock_verify_token:
                mock_verify_token.return_value = {
                    "cognito:username": "new_ditti_id",
                    "sub": "newuser123",
                    "iss": f"https://cognito-idp.{app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}",
                    "aud": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                    "token_use": "id",
                }

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}"
                )
                assert response.status_code == 302
                expected_redirect_url = app.config.get(
                    "CORS_ORIGINS", "http://localhost:3000"
                )
                assert response.headers["Location"] == expected_redirect_url

                # Check that cookies are set
                set_cookies = response.headers.getlist("Set-Cookie")
                cookies = parse_set_cookies(set_cookies)
                assert cookies.get("id_token") == "valid_id_token"
                assert cookies.get("access_token") == "valid_access_token"

                # Check that session is set and user is created
                with client_with_cognito.session_transaction() as sess:
                    assert "study_subject_id" in sess
                    study_subject_id = sess["study_subject_id"]
                    study_subject = StudySubject.query.get(study_subject_id)
                    assert study_subject is not None
                    assert study_subject.ditti_id == "new_ditti_id"
                    assert not study_subject.is_archived


def test_cognito_callback_missing_tokens(app, client_with_cognito):
    with app.app_context():
        # Mock authorization code
        auth_code = "valid_auth_code"

        # Mock requests.post to token endpoint to return incomplete tokens
        with patch("aws_portal.views.cognito.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "access_token": "valid_access_token"  # Missing id_token
            }
            mock_post.return_value = mock_response

            response = client_with_cognito.get(
                f"/cognito/callback?code={auth_code}"
            )
            assert response.status_code == 400
            assert response.get_json() == {"msg": "Error fetching tokens."}


def test_cognito_callback_invalid_token(app, client_with_cognito):
    with app.app_context():
        # Mock authorization code
        auth_code = "valid_auth_code"

        # Mock requests.post to token endpoint to return tokens
        with patch("aws_portal.views.cognito.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "id_token": "invalid_id_token",
                "access_token": "valid_access_token",
            }
            mock_post.return_value = mock_response

            # Mock verify_token to raise InvalidTokenError
            with patch(
                "aws_portal.views.cognito.cognito.verify_token"
            ) as mock_verify_token:
                mock_verify_token.side_effect = jwt.InvalidTokenError(
                    "Invalid token")

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}"
                )
                assert response.status_code == 400
                assert response.get_json() == {
                    "msg": "Invalid token: Invalid token"}


def test_cognito_callback_expired_token(app, client_with_cognito):
    with app.app_context():
        # Mock authorization code
        auth_code = "valid_auth_code"

        # Mock requests.post to token endpoint to return tokens
        with patch("aws_portal.views.cognito.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "id_token": "expired_id_token",
                "access_token": "valid_access_token",
            }
            mock_post.return_value = mock_response

            # Mock verify_token to raise ExpiredSignatureError
            with patch(
                "aws_portal.views.cognito.cognito.verify_token"
            ) as mock_verify_token:
                mock_verify_token.side_effect = jwt.ExpiredSignatureError(
                    "Token has expired."
                )

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}"
                )
                assert response.status_code == 400
                assert response.get_json() == {"msg": "Token has expired."}


def test_logout_success(app, client_with_cognito):
    with app.app_context():
        # Assume user is logged in with session and cookies
        with client_with_cognito.session_transaction() as sess:
            sess["study_subject_id"] = 1

        # Mock build_cognito_url to return a known logout URL
        with patch(
            "aws_portal.views.cognito.cognito.build_cognito_url"
        ) as mock_build_url:
            params = {
                "client_id": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                "redirect_uri": app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
                "response_type": "code",
                "scope": "openid",
            }
            redirect_uri_encoded = urlencode(
                {"redirect_uri": app.config["COGNITO_PARTICIPANT_REDIRECT_URI"]}
            )
            cognito_logout_url = (
                f"https://{app.config['COGNITO_PARTICIPANT_DOMAIN']}/logout?"
                + f"client_id={app.config['COGNITO_PARTICIPANT_CLIENT_ID']}"
                f"&redirect_uri={redirect_uri_encoded}"
                f"&response_type=code&scope=openid"
            )
            mock_build_url.return_value = cognito_logout_url

            response = client_with_cognito.get("/cognito/logout")
            assert response.status_code == 302
            assert response.headers["Location"] == cognito_logout_url

            # Check that cookies are cleared
            set_cookies = response.headers.getlist("Set-Cookie")
            cookies = parse_set_cookies(set_cookies)
            assert cookies.get("id_token") == ""
            assert cookies.get("access_token") == ""

            # Check that session is cleared
            with client_with_cognito.session_transaction() as sess:
                assert "study_subject_id" not in sess


def test_cognito_callback_requests_post_exception(app, client_with_cognito):
    with app.app_context():
        # Mock authorization code
        auth_code = "valid_auth_code"

        # Mock requests.post to token endpoint to raise RequestException
        with patch("aws_portal.views.cognito.cognito.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException(
                "Network error")

            # Send GET request to /cognito/callback with auth_code
            response = client_with_cognito.get(
                f"/cognito/callback?code={auth_code}")

            # Assert response status and message
            assert response.status_code == 400
            assert response.get_json() == {"msg": "Error fetching tokens."}


def test_cognito_callback_database_exception(app, client_with_cognito):
    with app.app_context():
        # Mock authorization code
        auth_code = "valid_auth_code"

        # Mock requests.post to token endpoint to return valid tokens
        with patch("aws_portal.views.cognito.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "id_token": "valid_id_token",
                "access_token": "valid_access_token",
            }
            mock_post.return_value = mock_response

            # Mock verify_token to return valid claims
            with patch("aws_portal.views.cognito.cognito.verify_token") as mock_verify_token:
                mock_verify_token.return_value = {
                    "cognito:username": "my_ditti_id",
                    "sub": "user123",
                    "iss": f"https://cognito-idp.{app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}",
                    "aud": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                    "token_use": "id",
                }

                # Mock StudySubject.query.filter_by().first() to raise Exception
                with patch("aws_portal.views.cognito.cognito.StudySubject.query") as mock_query:
                    # Ensure that any call to filter_by().first() raises an exception
                    mock_filter = MagicMock()
                    mock_filter.first.side_effect = Exception("Database error")
                    mock_query.filter_by.return_value = mock_filter

                    # Send GET request to /cognito/callback with auth_code
                    response = client_with_cognito.get(
                        f"/cognito/callback?code={auth_code}")

                    # Assert response status and message
                    assert response.status_code == 500
                    assert response.get_json() == {"msg": "Database error."}


def test_cognito_logout_without_cookies(app, client_with_cognito):
    with app.app_context():
        # Ensure no session or cookies are set
        with client_with_cognito.session_transaction() as sess:
            assert "study_subject_id" not in sess

        # Mock build_cognito_url to return a known logout URL
        with patch(
            "aws_portal.views.cognito.cognito.build_cognito_url"
        ) as mock_build_url:
            redirect_uri_encoded = urlencode(
                {"redirect_uri": app.config["COGNITO_PARTICIPANT_REDIRECT_URI"]}
            )
            cognito_logout_url = (
                f"https://{app.config['COGNITO_PARTICIPANT_DOMAIN']}/logout?"
                + f"client_id={app.config['COGNITO_PARTICIPANT_CLIENT_ID']}"
                f"&redirect_uri={redirect_uri_encoded}"
                f"&response_type=code&scope=openid"
            )
            mock_build_url.return_value = cognito_logout_url

            response = client_with_cognito.get("/cognito/logout")
            assert response.status_code == 302
            assert response.headers["Location"] == cognito_logout_url

            # Check that cookies are cleared even if they were not set
            set_cookies = response.headers.getlist("Set-Cookie")
            cookies = parse_set_cookies(set_cookies)
            assert cookies.get("id_token") == ""
            assert cookies.get("access_token") == ""


@patch("aws_portal.views.cognito.cognito.boto3.client")
@patch("aws_portal.models.Account.validate_ask", lambda *_: None)
def test_register_participant_success(mock_boto3_client, post_admin):
    # Mock Cognito client
    mock_cognito = MagicMock()
    mock_boto3_client.return_value = mock_cognito

    # Define request data
    data = {
        "data": {
            "cognitoUsername": "testuser",
            "temporaryPassword": "TempPass123!"
        }
    }

    # Send POST request
    response = post_admin(
        "/cognito/register/participant",
        data=json.dumps(data)
    )

    # Assertions
    assert response.status_code == 201
    assert response.json == {"msg": "Participant registered with AWS Cognito successfully."}
    mock_cognito.admin_create_user.assert_called_once_with(
        UserPoolId="us-east-1_example",
        Username="testuser",
        TemporaryPassword="TempPass123!",
        MessageAction="SUPPRESS"
    )


@patch("aws_portal.views.cognito.cognito.boto3.client")
@patch("aws_portal.models.Account.validate_ask", lambda *_: None)
def test_register_participant_missing_fields(mock_boto3_client, post_admin):
    # Define incomplete request data
    data = {
        "data": {
            "cognitoUsername": "testuser"
        }
    }

    # Send POST request
    response = post_admin(
        "/cognito/register/participant",
        data=json.dumps(data)
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {"error": "Cognito username and temporary password are required."}


@patch("aws_portal.views.cognito.cognito.boto3.client")
@patch("aws_portal.models.Account.validate_ask", lambda *_: None)
def test_register_participant_cognito_error(mock_boto3_client, post_admin):
    # Mock Cognito client to raise a ClientError
    mock_cognito = MagicMock()
    mock_cognito.admin_create_user.side_effect = Exception("AWS Cognito error")
    mock_boto3_client.return_value = mock_cognito

    # Define request data
    data = {
        "data": {
            "cognitoUsername": "testuser",
            "temporaryPassword": "TempPass123!"
        }
    }

    # Send POST request
    response = post_admin(
        "/cognito/register/participant",
        data=json.dumps(data)
    )

    # Assertions
    assert response.status_code == 500
    assert response.json == {"msg": "An unexpected error occurred."}


@patch("aws_portal.views.cognito.cognito.boto3.client")
@patch("aws_portal.models.Account.validate_ask", lambda *_: None)
def test_register_participant_aws_client_error(mock_boto3_client, post_admin):
    from botocore.exceptions import ClientError

    # Mock Cognito client to raise a ClientError
    mock_cognito = MagicMock()
    mock_cognito.admin_create_user.side_effect = ClientError(
        {"Error": {"Code": "UsernameExistsException"}}, "AdminCreateUser"
    )
    mock_boto3_client.return_value = mock_cognito

    # Define request data
    data = {
        "data": {
            "cognitoUsername": "testuser",
            "temporaryPassword": "TempPass123!"
        }
    }

    # Send POST request
    response = post_admin(
        "/cognito/register/participant",
        data=json.dumps(data)
    )

    # Assertions
    assert response.status_code == 500
    assert response.json == {"msg": "AWS Cognito error: UsernameExistsException"}
