import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from aws_portal.utils.cognito import (
    get_cognito_jwks,
    get_public_key,
    refresh_access_token,
    verify_token,
    cognito_auth_required,
)
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, PyJWTError
import requests


@pytest.fixture(autouse=True)
def clear_cognito_jwks_cache():
    get_cognito_jwks.cache_clear()


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["COGNITO_REGION"] = "us-east-1"
    app.config["COGNITO_USER_POOL_ID"] = "us-east-1_example"
    app.config["COGNITO_CLIENT_ID"] = "example_client_id"
    app.config["COGNITO_DOMAIN"] = "example.auth.us-east-1.amazoncognito.com"
    return app


def test_get_cognito_jwks_success(app):
    with app.app_context():
        fake_jwks = {
            "keys": [
                {
                    "kid": "example_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "modulus",
                    "e": "AQAB",
                }
            ]
        }
        with patch("aws_portal.utils.cognito.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = fake_jwks
            mock_get.return_value = mock_response

            jwks = get_cognito_jwks()
            assert jwks == fake_jwks
            mock_get.assert_called_once()


def test_get_cognito_jwks_request_exception(app):
    with app.app_context():
        # Clear the cache to ensure the function makes a new request
        get_cognito_jwks.cache_clear()

        with patch("aws_portal.utils.cognito.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Network error")
            with pytest.raises(requests.exceptions.RequestException):
                get_cognito_jwks()


def test_get_public_key_success(app):
    with app.app_context():
        fake_jwks = {
            "keys": [
                {
                    "kid": "example_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "modulus",
                    "e": "AQAB",
                }
            ]
        }
        with patch("aws_portal.utils.cognito.get_cognito_jwks", return_value=fake_jwks):
            with patch("aws_portal.utils.cognito.jwt.get_unverified_header", return_value={"kid": "example_kid"}):
                fake_public_key = MagicMock()
                with patch(
                    "aws_portal.utils.cognito.jwt.algorithms.RSAAlgorithm.from_jwk", return_value=fake_public_key
                ):
                    token = "fake_token"
                    public_key = get_public_key(token)
                    assert public_key == fake_public_key


def test_get_public_key_no_kid(app):
    with app.app_context():
        with patch("aws_portal.utils.cognito.jwt.get_unverified_header", return_value={}):
            with patch("aws_portal.utils.cognito.get_cognito_jwks", return_value={"keys": []}):
                token = "fake_token"
                with pytest.raises(
                    InvalidTokenError, match="No 'kid' found in token header."
                ):
                    get_public_key(token)


def test_get_public_key_key_not_found(app):
    with app.app_context():
        fake_jwks = {
            "keys": [
                {
                    "kid": "other_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "modulus",
                    "e": "AQAB",
                }
            ]
        }
        with patch("aws_portal.utils.cognito.get_cognito_jwks", return_value=fake_jwks):
            with patch("aws_portal.utils.cognito.jwt.get_unverified_header", return_value={"kid": "example_kid"}):
                token = "fake_token"
                with pytest.raises(
                    InvalidTokenError, match="Public key not found in JWKS."
                ):
                    get_public_key(token)


def test_get_public_key_jwks_request_exception(app):
    with app.app_context():
        with patch("aws_portal.utils.cognito.get_cognito_jwks") as mock_get_jwks:
            mock_get_jwks.side_effect = requests.exceptions.RequestException(
                "Network error")
            token = "fake_token"
            with pytest.raises(requests.exceptions.RequestException):
                get_public_key(token)


def test_refresh_access_token_success(app):
    with app.app_context():
        refresh_token = "fake_refresh_token"
        new_access_token = "new_fake_access_token"
        with patch("aws_portal.utils.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": new_access_token}
            mock_post.return_value = mock_response

            result = refresh_access_token(refresh_token)
            assert result == new_access_token
            mock_post.assert_called_once()


def test_refresh_access_token_no_access_token(app):
    with app.app_context():
        refresh_token = "fake_refresh_token"
        with patch("aws_portal.utils.cognito.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_post.return_value = mock_response

            with pytest.raises(
                Exception, match="No 'access_token' found in refresh response."
            ):
                refresh_access_token(refresh_token)


def test_refresh_access_token_request_exception(app):
    with app.app_context():
        refresh_token = "fake_refresh_token"
        with patch("aws_portal.utils.cognito.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException(
                "Network error")

            with pytest.raises(requests.exceptions.RequestException):
                refresh_access_token(refresh_token)


def test_verify_token_success_id_token(app):
    with app.app_context():
        token = "fake_id_token"
        public_key = MagicMock()
        payload = {
            "sub": "user123",
            "iss": f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}",
            "aud": app.config["COGNITO_CLIENT_ID"],
            "token_use": "id",
        }
        with patch("aws_portal.utils.cognito.get_public_key", return_value=public_key):
            with patch("aws_portal.utils.cognito.jwt.decode", return_value=payload) as mock_decode:
                claims = verify_token(token, token_use="id")
                assert claims == payload
                mock_decode.assert_called_once_with(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    audience=app.config["COGNITO_CLIENT_ID"],
                    issuer=payload["iss"],
                    options=None,
                )


def test_verify_token_success_access_token(app):
    with app.app_context():
        token = "fake_access_token"
        public_key = MagicMock()
        payload = {
            "sub": "user123",
            "iss": f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}",
            "token_use": "access",
            "client_id": app.config["COGNITO_CLIENT_ID"],
        }
        with patch("aws_portal.utils.cognito.get_public_key", return_value=public_key):
            with patch("aws_portal.utils.cognito.jwt.decode", return_value=payload) as mock_decode:
                claims = verify_token(token, token_use="access")
                assert claims == payload
                mock_decode.assert_called_once_with(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    audience=None,
                    issuer=payload["iss"],
                    options={"verify_aud": False},
                )


def test_verify_token_invalid_token_use(app):
    with app.app_context():
        token = "fake_token"
        fake_jwks = {
            "keys": [
                {
                    "kid": "example_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "modulus",
                    "e": "AQAB",
                }
            ]
        }
        with patch("aws_portal.utils.cognito.get_cognito_jwks", return_value=fake_jwks):
            with patch("aws_portal.utils.cognito.jwt.get_unverified_header", return_value={"kid": "example_kid"}):
                fake_public_key = MagicMock()
                with patch("aws_portal.utils.cognito.jwt.algorithms.RSAAlgorithm.from_jwk", return_value=fake_public_key):
                    with patch("aws_portal.utils.cognito.jwt.decode") as mock_jwt_decode:
                        # Simulate decode returning invalid 'token_use'
                        mock_jwt_decode.return_value = {
                            "sub": "user123",
                            "iss": f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}",
                            "aud": app.config["COGNITO_CLIENT_ID"],
                            "token_use": "invalid",  # Invalid token_use
                        }

                        with pytest.raises(InvalidTokenError, match="Invalid token type specified."):
                            verify_token(token, token_use="invalid")


def test_verify_token_invalid_claims(app):
    with app.app_context():
        token = "fake_token"
        public_key = MagicMock()
        with patch("aws_portal.utils.cognito.get_public_key", return_value=public_key):
            with patch("aws_portal.utils.cognito.jwt.decode", side_effect=InvalidTokenError("Invalid token")):
                with pytest.raises(InvalidTokenError, match="Invalid token"):
                    verify_token(token, token_use="id")


def test_verify_token_expired_signature(app):
    with app.app_context():
        token = "expired_token"
        public_key = MagicMock()
        with patch("aws_portal.utils.cognito.get_public_key", return_value=public_key):
            with patch("aws_portal.utils.cognito.jwt.decode", side_effect=ExpiredSignatureError("Token expired")):
                with pytest.raises(ExpiredSignatureError, match="Token expired"):
                    verify_token(token, token_use="id")


def test_verify_token_jwt_decode_exception(app):
    with app.app_context():
        token = "invalid_token"
        public_key = MagicMock()
        with patch("aws_portal.utils.cognito.get_public_key", return_value=public_key):
            with patch("aws_portal.utils.cognito.jwt.decode", side_effect=PyJWTError("Decode error")):
                with pytest.raises(PyJWTError, match="Decode error"):
                    verify_token(token, token_use="id")


def test_cognito_auth_required_success(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()

        with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
            # Mock verify_token to return valid claims for both tokens
            mock_verify_token.side_effect = lambda token, token_use: {
                "sub": "user123"}

            # Set cookies without 'server_name' for Flask 1.x
            test_client.set_cookie('id_token', 'valid_id_token')
            test_client.set_cookie('access_token', 'valid_access_token')

            response = test_client.get("/protected")
            assert response.status_code == 200
            assert response.get_json() == {"msg": "Success"}
            mock_verify_token.assert_any_call(
                "valid_access_token", token_use="access")
            mock_verify_token.assert_any_call("valid_id_token", token_use="id")


def test_cognito_auth_required_missing_tokens(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()
        response = test_client.get("/protected")
        assert response.status_code == 401
        assert response.get_json() == {"msg": "Missing authentication tokens."}


def test_cognito_auth_required_expired_access_token_with_refresh(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
            # Define side effects for verify_token
            def verify_token_side_effect(token, token_use):
                if token_use == "access":
                    if token == "expired_access_token":
                        raise ExpiredSignatureError("Token has expired.")
                    elif token == "new_access_token":
                        return {"sub": "user123"}
                elif token_use == "id":
                    return {"sub": "user123"}

            mock_verify_token.side_effect = verify_token_side_effect

            with patch("aws_portal.utils.cognito.refresh_access_token") as mock_refresh_access_token:
                # Simulate successful token refresh
                mock_refresh_access_token.return_value = "new_access_token"

                # Set cookies without 'server_name' for Flask 1.x
                test_client.set_cookie('id_token', 'valid_id_token')
                test_client.set_cookie('access_token', 'expired_access_token')
                test_client.set_cookie('refresh_token', 'valid_refresh_token')

                response = test_client.get("/protected")
                assert response.status_code == 200
                assert response.get_json() == {"msg": "Success"}
                mock_refresh_access_token.assert_called_once_with(
                    "valid_refresh_token")


def test_cognito_auth_required_expired_access_token_no_refresh(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
            # Define side effects for verify_token
            def verify_token_side_effect(token, token_use):
                if token_use == "access":
                    raise ExpiredSignatureError("Token has expired.")
                elif token_use == "id":
                    return {"sub": "user123"}

            mock_verify_token.side_effect = verify_token_side_effect

            # Set cookies without refresh_token for Flask 1.x
            test_client.set_cookie('id_token', 'valid_id_token')
            test_client.set_cookie('access_token', 'expired_access_token')

            response = test_client.get("/protected")
            assert response.status_code == 401
            assert response.get_json() == {"msg": "Missing refresh token."}


def test_cognito_auth_required_refresh_fails(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
            # Define side effects for verify_token
            def verify_token_side_effect(token, token_use):
                if token_use == "access":
                    raise ExpiredSignatureError("Token has expired.")
                elif token_use == "id":
                    return {"sub": "user123"}

            mock_verify_token.side_effect = verify_token_side_effect

            with patch("aws_portal.utils.cognito.refresh_access_token", side_effect=Exception("Refresh failed")) as mock_refresh_access_token:
                test_client.set_cookie('id_token', 'valid_id_token')
                test_client.set_cookie('access_token', 'expired_access_token')
                test_client.set_cookie('refresh_token', 'valid_refresh_token')

                response = test_client.get("/protected")
                assert response.status_code == 401
                assert response.get_json() == {
                    "msg": "Failed to refresh access token: Refresh failed"
                }
                mock_refresh_access_token.assert_called_once_with(
                    "valid_refresh_token")


def test_cognito_auth_required_invalid_access_token(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
            # Define side effects for verify_token
            def verify_token_side_effect(token, token_use):
                if token_use == "access":
                    raise InvalidTokenError("Invalid token")
                elif token_use == "id":
                    return {"sub": "user123"}

            mock_verify_token.side_effect = verify_token_side_effect

            # Set cookies without 'server_name' for Flask 1.x
            test_client.set_cookie('id_token', 'valid_id_token')
            test_client.set_cookie('access_token', 'invalid_access_token')

            response = test_client.get("/protected")
            assert response.status_code == 401
            assert response.get_json() == {
                "msg": "Invalid access token: Invalid token"}


def test_cognito_auth_required_invalid_id_token(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
            # Define side effects for verify_token
            def verify_token_side_effect(token, token_use):
                if token_use == "access":
                    return {"sub": "user123"}
                elif token_use == "id":
                    raise InvalidTokenError("Invalid ID token")

            mock_verify_token.side_effect = verify_token_side_effect

            # Set cookies without 'server_name' for Flask 1.x
            test_client.set_cookie('id_token', 'invalid_id_token')
            test_client.set_cookie('access_token', 'valid_access_token')

            response = test_client.get("/protected")
            assert response.status_code == 401
            assert response.get_json() == {
                "msg": "Invalid ID token: Invalid ID token"}


def test_cognito_auth_required_expired_id_token(app):
    with app.app_context():

        @app.route("/protected")
        @cognito_auth_required
        def protected():
            return {"msg": "Success"}, 200

        test_client = app.test_client()
        with patch("aws_portal.utils.cognito.verify_token") as mock_verify_token:
            # Define side effects for verify_token
            def verify_token_side_effect(token, token_use):
                if token_use == "access":
                    return {"sub": "user123"}
                elif token_use == "id":
                    raise ExpiredSignatureError("ID token expired")

            mock_verify_token.side_effect = verify_token_side_effect

            # Set cookies without 'server_name' for Flask 1.x
            test_client.set_cookie('id_token', 'expired_id_token')
            test_client.set_cookie('access_token', 'valid_access_token')

            response = test_client.get("/protected")
            assert response.status_code == 401
            assert response.get_json() == {"msg": "ID token has expired."}
