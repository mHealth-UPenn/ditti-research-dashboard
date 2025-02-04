import pytest
from unittest.mock import patch
from aws_portal.utils.cognito.service import get_participant_service
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import requests


@pytest.fixture
def mock_service(app):
    with app.app_context():
        service = get_participant_service()
        with patch.object(service, 'get_jwks') as mock_jwks, \
                patch.object(service, 'get_public_key') as mock_pubkey, \
                patch.object(service, 'verify_token') as mock_verify, \
                patch.object(service, 'refresh_access_token') as mock_refresh:
            yield service, mock_jwks, mock_pubkey, mock_verify, mock_refresh


def test_get_jwks_success(app):
    with app.app_context():
        fake_jwks = {"keys": [{"kid": "example_kid", "kty": "RSA",
                               "alg": "RS256", "use": "sig", "n": "modulus", "e": "AQAB"}]}
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = fake_jwks
            service = get_participant_service()
            result = service.get_jwks()
            assert result == fake_jwks


def test_verify_token_success_access_token(mock_service):
    service, _, _, mock_verify, _ = mock_service
    token = "test_token"
    expected_claims = {"sub": "user123", "token_use": "access"}
    mock_verify.return_value = expected_claims
    claims = service.verify_token(token, "access")
    assert claims == expected_claims


def test_refresh_access_token_success(mock_service):
    service, _, _, _, mock_refresh = mock_service
    refresh_token = "refresh_token"
    new_token = "new_access_token"
    mock_refresh.return_value = new_token
    result = service.refresh_access_token(refresh_token)
    assert result == new_token


def test_get_public_key_success(mock_service):
    service, _, mock_pubkey, _, _ = mock_service
    token = "test_token"
    expected_key = {"kty": "RSA", "n": "modulus", "e": "AQAB"}
    mock_pubkey.return_value = expected_key

    key = service.get_public_key(token)

    assert key == expected_key
    mock_pubkey.assert_called_once_with(token)


def test_get_public_key_no_kid(app):
    with app.app_context():
        service = get_participant_service()
        token = "test_token"

        with patch("jwt.get_unverified_header", return_value={}):
            with pytest.raises(InvalidTokenError, match="No 'kid' found"):
                service.get_public_key(token)


def test_get_public_key_key_not_found(app):
    with app.app_context():
        service = get_participant_service()
        token = "test_token"

        with patch.object(service, 'get_jwks') as mock_jwks:
            mock_jwks.return_value = {"keys": [{
                "kid": "other_kid",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "modulus",
                "e": "AQAB"
            }]}

            with patch("jwt.get_unverified_header", return_value={"kid": "missing_kid", "alg": "RS256"}):
                with pytest.raises(InvalidTokenError, match="Public key not found in JWKS"):
                    service.get_public_key(token)


def test_verify_token_invalid_token_use(mock_service):
    service, _, _, mock_verify, _ = mock_service
    token = "test_token"
    mock_verify.side_effect = InvalidTokenError("Invalid type")
    with pytest.raises(InvalidTokenError):
        service.verify_token(token, "invalid_use")


def test_verify_token_expired_signature(mock_service):
    service, _, _, mock_verify, _ = mock_service
    token = "test_token"
    mock_verify.side_effect = ExpiredSignatureError("Expired")
    with pytest.raises(ExpiredSignatureError):
        service.verify_token(token, "access")


def test_refresh_access_token_failure(mock_service):
    service, _, _, _, mock_refresh = mock_service
    mock_refresh.side_effect = Exception("Refresh failed")
    with pytest.raises(Exception):
        service.refresh_access_token("bad_token")


def test_verify_token_expired_id_token(mock_service):
    service, _, _, mock_verify, _ = mock_service
    token = "expired_id_token"
    mock_verify.side_effect = ExpiredSignatureError("ID token expired")
    with pytest.raises(ExpiredSignatureError):
        service.verify_token(token, "id")


def test_verify_token_invalid_signature(mock_service):
    service, _, _, mock_verify, _ = mock_service
    token = "invalid_sig_token"
    mock_verify.side_effect = InvalidTokenError("Invalid signature")
    with pytest.raises(InvalidTokenError):
        service.verify_token(token, "access")


def test_get_jwks_request_exception(app):
    with app.app_context():
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Connection failed")
            service = get_participant_service()

            with pytest.raises(requests.exceptions.RequestException):
                service.get_jwks()


def test_verify_token_general_error(mock_service):
    service, _, _, mock_verify, _ = mock_service
    token = "bad_token"
    mock_verify.side_effect = InvalidTokenError("Malformed token")

    with pytest.raises(InvalidTokenError):
        service.verify_token(token, "access")
