import pytest
from unittest.mock import patch, MagicMock
from flask import url_for
from aws_portal.views.cognito.cognito import build_cognito_url
from aws_portal.models import StudySubject
from aws_portal.extensions import db
import requests
from datetime import datetime, timezone
import jwt
from urllib.parse import urlencode
from http.cookies import SimpleCookie


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


def test_build_cognito_url(app, client_with_cognito):
    with app.app_context():
        path = "/test-path"
        params = {"key1": "value1", "key2": "value2"}
        expected_url = f"https://{app.config['COGNITO_DOMAIN']
                                  }/test-path?key1=value1&key2=value2"
        constructed_url = build_cognito_url(path, params)
        assert constructed_url == expected_url


def test_login_success(app, client_with_cognito):
    with app.app_context():
        # Expected Cognito auth URL
        params = {
            "client_id": app.config["COGNITO_CLIENT_ID"],
            "response_type": "code",
            "scope": "openid email",
            "redirect_uri": app.config["COGNITO_REDIRECT_URI"],
        }
        redirect_uri_encoded = urlencode(
            {"redirect_uri": app.config["COGNITO_REDIRECT_URI"]})
        cognito_auth_url = f"https://{app.config['COGNITO_DOMAIN']}/login?" + \
            f"client_id={app.config['COGNITO_CLIENT_ID']
                         }&response_type=code&scope=openid+email&redirect_uri={redirect_uri_encoded}"

        with patch("aws_portal.views.cognito.cognito.build_cognito_url", return_value=cognito_auth_url) as mock_build_url:
            response = client_with_cognito.get("/cognito/login")
            assert response.status_code == 302
            assert response.headers["Location"] == cognito_auth_url
            mock_build_url.assert_called_once_with("/login", params)


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
                "access_token": "valid_access_token"
            }
            mock_post.return_value = mock_response

            # Mock verify_token to return valid claims
            with patch("aws_portal.views.cognito.cognito.verify_token") as mock_verify_token:
                mock_verify_token.return_value = {
                    "email": "user@example.com",
                    "sub": "user123",
                    "iss": f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}",
                    "aud": app.config["COGNITO_CLIENT_ID"],
                    "token_use": "id",
                }

                # Ensure the user exists in the database
                study_subject = StudySubject(
                    created_on=datetime.now(timezone.utc),
                    email="user@example.com",
                    is_confirmed=True
                )
                db.session.add(study_subject)
                db.session.commit()

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}")
                assert response.status_code == 302
                expected_redirect_url = f"{app.config.get(
                    'CORS_ORIGINS', 'http://localhost:3000')}/participant"
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
                "access_token": "valid_access_token"
            }
            mock_post.return_value = mock_response

            # Mock verify_token to return valid claims
            with patch("aws_portal.views.cognito.cognito.verify_token") as mock_verify_token:
                mock_verify_token.return_value = {
                    "email": "newuser@example.com",
                    "sub": "newuser123",
                    "iss": f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}",
                    "aud": app.config["COGNITO_CLIENT_ID"],
                    "token_use": "id",
                }

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}")
                assert response.status_code == 302
                expected_redirect_url = f"{app.config.get(
                    'CORS_ORIGINS', 'http://localhost:3000')}/participant"
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
                    assert study_subject.email == "newuser@example.com"
                    assert study_subject.is_confirmed == True


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
                f"/cognito/callback?code={auth_code}")
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
                "access_token": "valid_access_token"
            }
            mock_post.return_value = mock_response

            # Mock verify_token to raise InvalidTokenError
            with patch("aws_portal.views.cognito.cognito.verify_token") as mock_verify_token:
                mock_verify_token.side_effect = jwt.InvalidTokenError(
                    "Invalid token")

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}")
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
                "access_token": "valid_access_token"
            }
            mock_post.return_value = mock_response

            # Mock verify_token to raise ExpiredSignatureError
            with patch("aws_portal.views.cognito.cognito.verify_token") as mock_verify_token:
                mock_verify_token.side_effect = jwt.ExpiredSignatureError(
                    "Token has expired.")

                response = client_with_cognito.get(
                    f"/cognito/callback?code={auth_code}")
                assert response.status_code == 400
                assert response.get_json() == {"msg": "Token has expired."}


def test_logout_success(app, client_with_cognito):
    with app.app_context():
        # Assume user is logged in with session and cookies
        with client_with_cognito.session_transaction() as sess:
            sess["study_subject_id"] = 1

        # Mock build_cognito_url to return a known logout URL
        with patch("aws_portal.views.cognito.cognito.build_cognito_url") as mock_build_url:
            params = {
                "client_id": app.config['COGNITO_CLIENT_ID'],
                "redirect_uri": app.config['COGNITO_REDIRECT_URI'],
                "response_type": "code",
                "scope": "openid email"
            }
            redirect_uri_encoded = urlencode(
                {"redirect_uri": app.config['COGNITO_REDIRECT_URI']})
            cognito_logout_url = f"https://{app.config['COGNITO_DOMAIN']}/logout?" + \
                f"client_id={app.config['COGNITO_CLIENT_ID']}&redirect_uri={
                    redirect_uri_encoded}&response_type=code&scope=openid+email"
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

            with pytest.raises(requests.exceptions.RequestException):
                client_with_cognito.get(f"/cognito/callback?code={auth_code}")


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
                "access_token": "valid_access_token"
            }
            mock_post.return_value = mock_response

            # Mock verify_token to return valid claims
            with patch("aws_portal.views.cognito.cognito.verify_token") as mock_verify_token:
                mock_verify_token.return_value = {
                    "email": "user@example.com",
                    "sub": "user123",
                    "iss": f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}",
                    "aud": app.config["COGNITO_CLIENT_ID"],
                    "token_use": "id",
                }

                # Mock StudySubject.query.filter_by().first() to raise Exception
                with patch("aws_portal.views.cognito.cognito.StudySubject.query") as mock_query:
                    mock_query.filter_by.return_value.first.side_effect = Exception(
                        "Database error")

                    with patch("aws_portal.views.cognito.cognito.db.session.commit", side_effect=Exception("Database commit failed")):
                        with pytest.raises(Exception):
                            client_with_cognito.get(
                                f"/cognito/callback?code={auth_code}")


def test_cognito_logout_without_cookies(app, client_with_cognito):
    with app.app_context():
        # Ensure no session or cookies are set
        with client_with_cognito.session_transaction() as sess:
            assert "study_subject_id" not in sess

        # Mock build_cognito_url to return a known logout URL
        with patch("aws_portal.views.cognito.cognito.build_cognito_url") as mock_build_url:
            params = {
                "client_id": app.config['COGNITO_CLIENT_ID'],
                "redirect_uri": app.config['COGNITO_REDIRECT_URI'],
                "response_type": "code",
                "scope": "openid email"
            }
            redirect_uri_encoded = urlencode(
                {"redirect_uri": app.config['COGNITO_REDIRECT_URI']})
            cognito_logout_url = f"https://{app.config['COGNITO_DOMAIN']}/logout?" + \
                f"client_id={app.config['COGNITO_CLIENT_ID']}&redirect_uri={
                    redirect_uri_encoded}&response_type=code&scope=openid+email"
            mock_build_url.return_value = cognito_logout_url

            response = client_with_cognito.get("/cognito/logout")
            assert response.status_code == 302
            assert response.headers["Location"] == cognito_logout_url

            # Check that cookies are cleared even if they were not set
            set_cookies = response.headers.getlist("Set-Cookie")
            cookies = parse_set_cookies(set_cookies)
            assert cookies.get("id_token") == ""
            assert cookies.get("access_token") == ""
