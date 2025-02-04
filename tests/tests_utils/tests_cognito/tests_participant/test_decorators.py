import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from aws_portal.utils.cognito.participant.decorators import participant_auth_required


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["COGNITO_PARTICIPANT_REGION"] = "us-east-1"
    app.config["COGNITO_PARTICIPANT_USER_POOL_ID"] = "us-east-1_example"
    app.config["COGNITO_PARTICIPANT_CLIENT_ID"] = "example_client_id"
    app.config["COGNITO_PARTICIPANT_DOMAIN"] = "example.auth.us-east-1.amazoncognito.com"
    app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"] = "secret"
    app.config["COGNITO_PARTICIPANT_REDIRECT_URI"] = "http://localhost/callback"
    app.config["COGNITO_PARTICIPANT_LOGOUT_URI"] = "http://localhost/logout"
    return app


def test_participant_auth_decorator_success(app):
    with app.app_context():
        @app.route("/protected")
        @participant_auth_required
        def protected(ditti_id):
            return {"ditti_id": ditti_id}, 200

        test_client = app.test_client()

        with patch("aws_portal.utils.cognito.participant.decorators.get_participant_service") as mock_service, \
                patch("aws_portal.extensions.db.session.execute") as mock_execute:

            service = MagicMock()
            service.verify_token.side_effect = lambda t, u: {
                "sub": "123"} if u == "access" else {"cognito:username": "user123"}
            service.get_jwks.return_value = {"keys": [
                {"kid": "example_kid", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "modulus", "e": "AQAB"}]}
            mock_service.return_value = service

            mock_execute.return_value.scalar.return_value = "user123"

            test_client.set_cookie('id_token', 'valid_id')
            test_client.set_cookie('access_token', 'valid_access')

            response = test_client.get("/protected")
            assert response.status_code == 200
            assert response.json["ditti_id"] == "user123"


def test_participant_auth_missing_tokens(app):
    with app.app_context():
        @app.route("/protected")
        @participant_auth_required
        def protected(ditti_id):
            return {}, 200

        test_client = app.test_client()
        response = test_client.get("/protected")
        assert response.status_code == 401
        assert "Missing authentication tokens" in response.json["msg"]


def test_participant_auth_expired_access_token(app):
    with app.app_context():
        @app.route("/protected")
        @participant_auth_required
        def protected(ditti_id):
            return {}, 200

        test_client = app.test_client()

        with patch("aws_portal.utils.cognito.participant.decorators.get_participant_service") as mock_service, \
                patch("aws_portal.extensions.db.session.execute") as mock_execute:

            service = MagicMock()
            service.verify_token.side_effect = [
                ExpiredSignatureError("Expired"),
                {"sub": "user123", "token_use": "access"},
                {"cognito:username": "user123", "token_use": "id"}
            ]
            service.refresh_access_token.return_value = "new_token"
            service.get_jwks.return_value = {"keys": [
                {"kid": "example_kid", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "modulus", "e": "AQAB"}]}
            mock_service.return_value = service

            mock_execute.return_value.scalar.return_value = "user123"

            test_client.set_cookie('id_token', 'valid_id')
            test_client.set_cookie('access_token', 'expired')
            test_client.set_cookie('refresh_token', 'refresh')

            response = test_client.get("/protected")
            assert response.status_code == 200


def test_participant_auth_invalid_id_token(app):
    with app.app_context():
        @app.route("/protected")
        @participant_auth_required
        def protected(ditti_id):
            return {}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.participant.decorators.get_participant_service") as mock_service:
            service = MagicMock()
            service.verify_token.side_effect = InvalidTokenError(
                "Invalid ID token")
            service.get_jwks.return_value = {"keys": [
                {"kid": "example_kid", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "modulus", "e": "AQAB"}]}
            mock_service.return_value = service

            test_client.set_cookie('id_token', 'invalid')
            test_client.set_cookie('access_token', 'valid')

            response = test_client.get("/protected")
            assert response.status_code == 401
            assert "Invalid token" in response.json["msg"]


def test_participant_auth_database_lookup_failure(app):
    with app.app_context():
        @app.route("/protected")
        @participant_auth_required
        def protected(ditti_id):
            return {}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.participant.decorators.get_participant_service") as mock_service, \
                patch("aws_portal.extensions.db.session.execute") as mock_execute:

            service = MagicMock()
            service.verify_token.return_value = {"cognito:username": "user123"}
            service.get_jwks.return_value = {"keys": [
                {"kid": "example_kid", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "modulus", "e": "AQAB"}]}
            mock_service.return_value = service

            mock_execute.return_value.scalar.return_value = None

            test_client.set_cookie('id_token', 'valid')
            test_client.set_cookie('access_token', 'valid')

            response = test_client.get("/protected")
            assert response.status_code == 400
            assert "Participant not found" in response.json["msg"]


def test_participant_auth_database_exception(app):
    with app.app_context():
        @app.route("/protected")
        @participant_auth_required
        def protected(ditti_id):
            return {}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.participant.decorators.get_participant_service") as mock_service, \
                patch("aws_portal.extensions.db.session.execute") as mock_execute:

            service = MagicMock()
            service.verify_token.return_value = {"cognito:username": "user123"}
            service.get_jwks.return_value = {"keys": [
                {"kid": "example_kid", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "modulus", "e": "AQAB"}]}
            mock_service.return_value = service

            mock_execute.side_effect = Exception("Database error")

            test_client.set_cookie('id_token', 'valid')
            test_client.set_cookie('access_token', 'valid')

            response = test_client.get("/protected")
            assert response.status_code == 500
            assert "Database error" in response.json["msg"]


def test_participant_auth_missing_refresh_token(app):
    with app.app_context():
        @app.route("/protected")
        @participant_auth_required
        def protected(ditti_id):
            return {}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.participant.decorators.get_participant_service") as mock_service:
            service = MagicMock()
            service.verify_token.side_effect = ExpiredSignatureError("Expired")
            service.get_jwks.return_value = {"keys": [
                {"kid": "example_kid", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "modulus", "e": "AQAB"}]}
            mock_service.return_value = service

            test_client.set_cookie('id_token', 'valid')
            test_client.set_cookie('access_token', 'expired')

            response = test_client.get("/protected")
            assert response.status_code == 401
            assert "Missing refresh token" in response.json["msg"]
