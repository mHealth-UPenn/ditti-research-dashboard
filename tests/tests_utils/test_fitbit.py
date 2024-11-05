import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from aws_portal.utils.fitbit import (
    generate_code_verifier,
    create_code_challenge,
    get_fitbit_oauth_session,
)
from aws_portal.extensions import sm
import base64
import hashlib
import time
import requests


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["FITBIT_CLIENT_ID"] = "fake_fitbit_client_id"
    app.config["FITBIT_CLIENT_SECRET"] = "fake_fitbit_client_secret"
    return app


def test_generate_code_verifier_valid_length():
    # Test for minimum length
    code_verifier = generate_code_verifier(43)
    assert len(code_verifier) == 43

    # Test for maximum length
    code_verifier = generate_code_verifier(128)
    assert len(code_verifier) == 128

    # Test for default length (128)
    code_verifier = generate_code_verifier()
    assert len(code_verifier) == 128


def test_generate_code_verifier_invalid_length():
    with pytest.raises(ValueError, match="length must be between 43 and 128 characters"):
        generate_code_verifier(42)
    with pytest.raises(ValueError, match="length must be between 43 and 128 characters"):
        generate_code_verifier(129)


def test_create_code_challenge_correctness():
    code_verifier = "test_code_verifier"
    expected_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).rstrip(b'=').decode('utf-8')

    code_challenge = create_code_challenge(code_verifier)
    assert code_challenge == expected_challenge


def test_get_fitbit_oauth_session_success(app):
    with app.app_context():
        # Mock join_entry with access_key_uuid and refresh_key_uuid
        join_entry = MagicMock()
        join_entry.access_key_uuid = "access_key_uuid"
        join_entry.refresh_key_uuid = "refresh_key_uuid"

        # Mock tokens
        fake_access_token_data = {
            "access_token": "fake_access_token",
            "expires_at": int(time.time()) + 3600,
        }
        fake_refresh_token_data = {
            "refresh_token": "fake_refresh_token",
        }

        # Mock sm.get_secret to return fake tokens
        with patch.object(sm, 'get_secret') as mock_get_secret:
            def get_secret_side_effect(key_uuid):
                if key_uuid == "access_key_uuid":
                    return fake_access_token_data
                elif key_uuid == "refresh_key_uuid":
                    return fake_refresh_token_data
            mock_get_secret.side_effect = get_secret_side_effect

            # Mock WebApplicationClient
            with patch("aws_portal.utils.fitbit.WebApplicationClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                session = get_fitbit_oauth_session(join_entry)
                assert session is not None
                assert hasattr(session, 'request')
                assert hasattr(session, 'get')
                assert hasattr(session, 'post')


def test_get_fitbit_oauth_session_token_refresh(app):
    with app.app_context():
        # Mock join_entry
        join_entry = MagicMock()
        join_entry.access_key_uuid = "access_key_uuid"
        join_entry.refresh_key_uuid = "refresh_key_uuid"

        # Mock expired access token and valid refresh token
        expired_access_token_data = {
            "access_token": "expired_access_token",
            "expires_at": int(time.time()) - 3600,
        }
        fake_refresh_token_data = {
            "refresh_token": "fake_refresh_token",
        }

        # Mock sm.get_secret
        with patch.object(sm, 'get_secret') as mock_get_secret:
            def get_secret_side_effect(key_uuid):
                if key_uuid == "access_key_uuid":
                    return expired_access_token_data
                elif key_uuid == "refresh_key_uuid":
                    return fake_refresh_token_data
            mock_get_secret.side_effect = get_secret_side_effect

            # Mock WebApplicationClient
            with patch("aws_portal.utils.fitbit.WebApplicationClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                # Mock token refresh response
                with patch("aws_portal.utils.fitbit.requests.post") as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "access_token": "new_access_token",
                        "refresh_token": "new_refresh_token",
                        "expires_in": 3600,
                    }
                    mock_post.return_value = mock_response

                    # Mock sm.store_secret
                    with patch.object(sm, 'store_secret') as mock_store_secret:

                        session = get_fitbit_oauth_session(join_entry)

                        # Simulate a request that returns 401 and then 200 after refresh
                        with patch("aws_portal.utils.fitbit.requests.request") as mock_request:
                            # First call returns 401
                            mock_response_401 = MagicMock()
                            mock_response_401.status_code = 401
                            # Second call returns 200
                            mock_response_200 = MagicMock()
                            mock_response_200.status_code = 200
                            mock_request.side_effect = [
                                mock_response_401, mock_response_200]

                            response = session.get(
                                "https://api.fitbit.com/1/user/-/profile.json")
                            assert response.status_code == 200
                            assert mock_post.called
                            assert mock_store_secret.called


def test_get_fitbit_oauth_session_refresh_failure(app):
    with app.app_context():
        # Mock join_entry
        join_entry = MagicMock()
        join_entry.access_key_uuid = "access_key_uuid"
        join_entry.refresh_key_uuid = "refresh_key_uuid"

        # Mock expired access token and valid refresh token
        expired_access_token_data = {
            "access_token": "expired_access_token",
            "expires_at": int(time.time()) - 3600,
        }
        fake_refresh_token_data = {
            "refresh_token": "fake_refresh_token",
        }

        # Mock sm.get_secret
        with patch.object(sm, 'get_secret') as mock_get_secret:
            def get_secret_side_effect(key_uuid):
                if key_uuid == "access_key_uuid":
                    return expired_access_token_data
                elif key_uuid == "refresh_key_uuid":
                    return fake_refresh_token_data
            mock_get_secret.side_effect = get_secret_side_effect

            # Mock WebApplicationClient
            with patch("aws_portal.utils.fitbit.WebApplicationClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                # Mock token refresh failure
                with patch("aws_portal.utils.fitbit.requests.post") as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 400
                    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                        "Token refresh failed")
                    mock_post.return_value = mock_response

                    session = get_fitbit_oauth_session(join_entry)

                    # Simulate a request that triggers token refresh failure
                    with patch("aws_portal.utils.fitbit.requests.request") as mock_request:
                        mock_response_401 = MagicMock()
                        mock_response_401.status_code = 401
                        mock_request.return_value = mock_response_401

                        # Update the expected match to the actual exception message
                        with pytest.raises(requests.exceptions.HTTPError, match="Token refresh failed"):
                            session.get(
                                "https://api.fitbit.com/1/user/-/profile.json")


def test_get_fitbit_oauth_session_sm_get_secret_failure(app):
    with app.app_context():
        # Mock join_entry
        join_entry = MagicMock()
        join_entry.access_key_uuid = "access_key_uuid"

        # Mock sm.get_secret to raise exception
        with patch.object(sm, 'get_secret', side_effect=Exception("SM get_secret failed")):
            with pytest.raises(Exception, match="SM get_secret failed"):
                get_fitbit_oauth_session(join_entry)


def test_get_fitbit_oauth_session_sm_store_secret_failure(app):
    with app.app_context():
        # Mock join_entry
        join_entry = MagicMock()
        join_entry.access_key_uuid = "access_key_uuid"
        join_entry.refresh_key_uuid = "refresh_key_uuid"

        # Mock tokens
        expired_access_token_data = {
            "access_token": "expired_access_token",
            "expires_at": int(time.time()) - 3600,
        }
        fake_refresh_token_data = {
            "refresh_token": "fake_refresh_token",
        }

        # Mock sm.get_secret
        with patch.object(sm, 'get_secret') as mock_get_secret:
            def get_secret_side_effect(key_uuid):
                if key_uuid == "access_key_uuid":
                    return expired_access_token_data
                elif key_uuid == "refresh_key_uuid":
                    return fake_refresh_token_data
            mock_get_secret.side_effect = get_secret_side_effect

            # Mock WebApplicationClient
            with patch("aws_portal.utils.fitbit.WebApplicationClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                # Mock token refresh response
                with patch("aws_portal.utils.fitbit.requests.post") as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "access_token": "new_access_token",
                        "refresh_token": "new_refresh_token",
                        "expires_in": 3600,
                    }
                    mock_post.return_value = mock_response

                    # Mock sm.store_secret to raise exception
                    with patch.object(sm, 'store_secret', side_effect=Exception("SM store_secret failed")):

                        session = get_fitbit_oauth_session(join_entry)

                        # Simulate a request that triggers token refresh
                        with patch("aws_portal.utils.fitbit.requests.request") as mock_request:
                            mock_response_401 = MagicMock()
                            mock_response_401.status_code = 401
                            mock_request.return_value = mock_response_401

                            # Update the expected match to the actual exception message
                            with pytest.raises(Exception, match="SM store_secret failed"):
                                session.get(
                                    "https://api.fitbit.com/1/user/-/profile.json")
