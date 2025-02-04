import json
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from flask import Flask
from sqlalchemy.inspection import inspect
from sqlalchemy.types import ARRAY
import requests


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # Add required Cognito configuration
    app.config.update({
        "COGNITO_PARTICIPANT_REGION": "us-east-1",
        "COGNITO_PARTICIPANT_USER_POOL_ID": "us-east-1_example",
        "COGNITO_PARTICIPANT_CLIENT_ID": "example_client_id",
        "COGNITO_PARTICIPANT_CLIENT_SECRET": "example_secret",
        "COGNITO_PARTICIPANT_DOMAIN": "example.auth.us-east-1.amazoncognito.com",
        "COGNITO_PARTICIPANT_REDIRECT_URI": "http://localhost/callback",
        "COGNITO_PARTICIPANT_LOGOUT_URI": "http://localhost/logout",
        "CORS_ORIGINS": "http://localhost:3000"
    })

    # Add blueprint registration
    from aws_portal.views.cognito.participant import auth as participant_auth
    app.register_blueprint(participant_auth.blueprint)

    db.init_app(app)
    with app.app_context():
        # Only create tables that don't use unsupported SQLite types
        inspector = inspect(db.engine)
        tables_to_create = []
        for table in db.Model.metadata.tables.values():
            if not any(
                # Exclude tables with ARRAY columns
                isinstance(col.type, ARRAY)
                for col in table.columns.values()
            ):
                tables_to_create.append(table)

        db.metadata.create_all(
            bind=db.engine,
            tables=tables_to_create,
            checkfirst=False
        )
    yield app
    with app.app_context():
        db.drop_all()


def parse_set_cookies(set_cookie_headers):
    """Helper to parse Set-Cookie headers"""
    cookies = {}
    for sc in set_cookie_headers:
        cookie = SimpleCookie()
        cookie.load(sc)
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
    return cookies


def test_login_success(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.build_cognito_url") as mock_build:
            expected_params = {
                "client_id": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                "response_type": "code",
                "scope": "openid",
                "redirect_uri": app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
            }

            mock_build.return_value = "https://mock_auth_url"

            response = client.get("/cognito/login")
            assert response.status_code == 302
            assert response.headers["Location"] == "https://mock_auth_url"
            mock_build.assert_called_once_with("/login", expected_params)


def test_cognito_callback_success_existing_user(app, client):
    with app.app_context():
        auth_code = "valid_code"

        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post, \
                patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:

            mock_post.return_value.json.return_value = {
                "id_token": "test_id",
                "access_token": "test_access"
            }

            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.return_value = {
                "cognito:username": "existing_ditti_id",
                "sub": "user123",
                "iss": f"https://cognito-idp.{app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}",
                "aud": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                "token_use": "id",
            }

            study_subject = StudySubject(
                created_on=datetime.now(timezone.utc),
                ditti_id="existing_ditti_id",
                is_archived=False,
            )
            db.session.add(study_subject)
            db.session.commit()

            response = client.get(
                f"/cognito/callback?code={auth_code}")
            assert response.status_code == 302
            assert response.headers["Location"] == app.config.get(
                "CORS_ORIGINS", "http://localhost:3000")

            cookies = parse_set_cookies(response.headers.getlist("Set-Cookie"))
            assert cookies["id_token"] == "test_id"
            assert cookies["access_token"] == "test_access"

            with client.session_transaction() as sess:
                assert sess["study_subject_id"] == study_subject.id


def test_cognito_callback_success_new_user(app, client):
    with app.app_context():
        auth_code = "valid_code"

        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post, \
                patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:

            mock_post.return_value.json.return_value = {
                "id_token": "test_id",
                "access_token": "test_access"
            }

            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.return_value = {
                "cognito:username": "new_ditti_id",
                "sub": "newuser123",
                "iss": f"https://cognito-idp.{app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}",
                "aud": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                "token_use": "id",
            }

            response = client.get(
                f"/cognito/callback?code={auth_code}")
            assert response.status_code == 302

            with client.session_transaction() as sess:
                study_subject = StudySubject.query.get(
                    sess["study_subject_id"])
                assert study_subject.ditti_id == "new_ditti_id"


def test_cognito_callback_missing_tokens(app, client):
    with app.app_context():
        auth_code = "valid_code"

        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post:
            mock_post.return_value.json.return_value = {
                "access_token": "only_access"}

            response = client.get(
                f"/cognito/callback?code={auth_code}")
            assert response.status_code == 400
            assert json.loads(response.data) == {
                "msg": "Authentication error."}


def test_cognito_callback_invalid_token(app, client):
    with app.app_context():
        auth_code = "valid_code"

        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post, \
                patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:

            mock_post.return_value.json.return_value = {
                "id_token": "invalid",
                "access_token": "valid"
            }

            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.side_effect = InvalidTokenError(
                "Invalid token")

            response = client.get(
                f"/cognito/callback?code={auth_code}")
            assert response.status_code == 400
            assert json.loads(response.data) == {
                "msg": "Authentication error."}


def test_cognito_callback_database_error(app, client):
    with app.app_context():
        auth_code = "valid_code"

        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post, \
                patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service, \
                patch("aws_portal.views.cognito.participant.auth.db.session.commit") as mock_commit:

            mock_post.return_value.json.return_value = {
                "id_token": "test_id",
                "access_token": "test_access"
            }

            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.return_value = {
                "cognito:username": "new_ditti_id",
                "sub": "newuser123",
                "iss": f"https://cognito-idp.{app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}",
                "aud": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                "token_use": "id",
            }

            mock_commit.side_effect = Exception("DB error")

            response = client.get(
                f"/cognito/callback?code={auth_code}")
            assert response.status_code == 400
            assert json.loads(response.data) == {
                "msg": "Authentication error."}


def test_logout_success(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.build_cognito_url") as mock_build:
            expected_params = {
                "client_id": app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                "logout_uri": app.config["COGNITO_PARTICIPANT_LOGOUT_URI"],
                "response_type": "code"
            }

            mock_build.return_value = "https://mock_logout_url"

            with client.session_transaction() as sess:
                sess["study_subject_id"] = 1

            response = client.get("/cognito/logout")
            assert response.status_code == 302
            assert response.headers["Location"] == "https://mock_logout_url"
            mock_build.assert_called_once_with("/logout", expected_params)


def test_check_login_authenticated(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:
            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.return_value = {
                "cognito:username": "testuser",
                "sub": "user123"
            }

            study_subject = StudySubject(
                created_on=datetime.now(timezone.utc),
                ditti_id="TestUser",
                is_archived=False,
            )
            db.session.add(study_subject)
            db.session.commit()

            client.set_cookie(
                "id_token",
                "valid_token",
                domain="localhost"
            )
            response = client.get("/cognito/check-login")
            assert response.status_code == 200
            assert json.loads(response.data) == {
                "msg": "Login successful",
                "dittiId": "TestUser"
            }


def test_check_login_unauthenticated(app, client):
    response = client.get("/cognito/check-login")
    assert response.status_code == 401
    assert json.loads(response.data) == {"msg": "Not authenticated"}


def test_cognito_callback_missing_code(app, client):
    with app.app_context():
        response = client.get("/cognito/callback")
        assert response.status_code == 400
        assert json.loads(response.data) == {
            "msg": "Authorization code not provided."}


def test_cognito_callback_token_fetch_error(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post, \
                patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:

            # Configure service mock
            service_mock = MagicMock()
            service_mock.config = MagicMock(
                client_id="dummy_client",
                client_secret="dummy_secret",
                redirect_uri="http://dummy",
                domain="example.auth.us-east-1.amazoncognito.com"
            )
            mock_service.return_value = service_mock

            # Raise a requests exception instead of generic Exception
            mock_post.side_effect = requests.exceptions.ConnectionError(
                "Connection error")

            response = client.get("/cognito/callback?code=invalid")
            assert response.status_code == 400
            assert json.loads(response.data) == {
                "msg": "Error fetching tokens."
            }


def test_cognito_callback_invalid_token_use(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post, \
                patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:

            mock_post.return_value.json.return_value = {
                "id_token": "invalid",
                "access_token": "valid"
            }

            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.side_effect = InvalidTokenError(
                "Invalid token use")

            response = client.get("/cognito/callback?code=invalid")
            assert response.status_code == 400


def test_cognito_callback_archived_user(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.requests.post") as mock_post, \
                patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:

            mock_post.return_value.json.return_value = {
                "id_token": "test_id",
                "access_token": "test_access"
            }

            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.return_value = {
                "cognito:username": "archived_user",
                "sub": "user123"
            }

            study_subject = StudySubject(
                created_on=datetime.now(timezone.utc),
                ditti_id="archived_user",
                is_archived=True,
            )
            db.session.add(study_subject)
            db.session.commit()

            response = client.get("/cognito/callback?code=valid")
            assert response.status_code == 400
            assert json.loads(response.data) == {"msg": "Account is archived."}


def test_logout_without_cookies(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.build_cognito_url") as mock_build:
            mock_build.return_value = "https://mock_logout_url"

            response = client.get("/cognito/logout")
            assert response.status_code == 302

            cookies = parse_set_cookies(response.headers.getlist("Set-Cookie"))
            assert cookies.get("id_token") == ""
            assert cookies.get("access_token") == ""


def test_check_login_expired_token(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:
            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.side_effect = ExpiredSignatureError(
                "Expired")

            client.set_cookie("id_token", "expired_token", domain="localhost")
            response = client.get("/cognito/check-login")
            assert response.status_code == 401


def test_check_login_invalid_token(app, client):
    with app.app_context():
        with patch("aws_portal.views.cognito.participant.auth.get_participant_service") as mock_service:
            service_mock = MagicMock()
            mock_service.return_value = service_mock
            service_mock.verify_token.side_effect = InvalidTokenError(
                "Invalid")

            client.set_cookie("id_token", "invalid", domain="localhost")
            response = client.get("/cognito/check-login")
            assert response.status_code == 401
