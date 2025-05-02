# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
import hashlib
import time
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask

from backend.extensions import tm  # Updated from sm to tm
from shared.fitbit import (
    create_code_challenge,
    generate_code_verifier,
    get_fitbit_oauth_session,
)


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["FITBIT_CLIENT_ID"] = "fake_fitbit_client_id"
    app.config["FITBIT_CLIENT_SECRET"] = "fake_fitbit_client_secret"  # noqa: S105
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
    with pytest.raises(
        ValueError, match="length must be between 43 and 128 characters"
    ):
        generate_code_verifier(42)
    with pytest.raises(
        ValueError, match="length must be between 43 and 128 characters"
    ):
        generate_code_verifier(129)


def test_create_code_challenge_correctness():
    code_verifier = "test_code_verifier"
    expected_challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        )
        .rstrip(b"=")
        .decode("utf-8")
    )

    code_challenge = create_code_challenge(code_verifier)
    assert code_challenge == expected_challenge


def test_get_fitbit_oauth_session_success(app):
    with app.app_context():
        # Mock tokens
        fake_tokens = {
            "access_token": "fake_access_token",
            "refresh_token": "fake_refresh_token",
            "expires_at": int(time.time()) + 3600,
        }

        # Use a single with statement with multiple contexts
        with (
            patch.object(tm, "get_api_tokens") as mock_get_api_tokens,
            patch.object(tm, "add_or_update_api_token"),
            patch("shared.fitbit.WebApplicationClient") as mock_client_class,
        ):
            mock_get_api_tokens.return_value = fake_tokens
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            session = get_fitbit_oauth_session(
                "123", config=app.config, tokens=fake_tokens, tm=tm
            )
            assert session is not None
            assert hasattr(session, "request")
            assert hasattr(session, "get")
            assert hasattr(session, "post")


def test_get_fitbit_oauth_session_token_refresh(app):
    with app.app_context():
        # Mock expired access token and valid refresh token
        expired_tokens = {
            "access_token": "expired_access_token",
            "refresh_token": "fake_refresh_token",
            "expires_at": int(time.time()) - 3600,
        }

        # Use a single with statement with multiple contexts
        with (
            patch.object(tm, "get_api_tokens") as mock_get_api_tokens,
            patch.object(
                tm, "add_or_update_api_token"
            ) as mock_add_update_api_token,
            patch("shared.fitbit.WebApplicationClient") as mock_client_class,
            patch("shared.fitbit.requests.post") as mock_post,
        ):
            mock_get_api_tokens.return_value = expired_tokens
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock token refresh response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600,
            }
            mock_post.return_value = mock_response

            # Initialize the OAuth2 session
            session = get_fitbit_oauth_session(
                "123",
                config=app.config,
                tokens=expired_tokens,
                tm=tm,
            )

            # Simulate a request that returns 401 and then 200 after refresh
            with patch("shared.fitbit.requests.request") as mock_request:
                # First call returns 401
                mock_response_401 = MagicMock()
                mock_response_401.status_code = 401
                # Second call returns 200
                mock_response_200 = MagicMock()
                mock_response_200.status_code = 200
                mock_request.side_effect = [
                    mock_response_401,
                    mock_response_200,
                ]

                response = session.get(
                    "https://api.fitbit.com/1/user/-/profile.json"
                )
                assert response.status_code == 200
                assert mock_post.called
                assert mock_add_update_api_token.called


def test_get_fitbit_oauth_session_refresh_failure(app):
    with app.app_context():
        # Mock expired access token and valid refresh token
        expired_tokens = {
            "access_token": "expired_access_token",
            "refresh_token": "fake_refresh_token",
            "expires_at": int(time.time()) - 3600,
        }

        # Use a single with statement with multiple contexts
        with (
            patch.object(tm, "get_api_tokens") as mock_get_api_tokens,
            patch.object(tm, "add_or_update_api_token"),
            patch("shared.fitbit.WebApplicationClient") as mock_client_class,
            patch("shared.fitbit.requests.post") as mock_post,
        ):
            mock_get_api_tokens.return_value = expired_tokens
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock token refresh failure
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.raise_for_status.side_effect = (
                requests.exceptions.HTTPError("Token refresh failed")
            )
            mock_post.return_value = mock_response

            # Initialize the OAuth2 session
            session = get_fitbit_oauth_session(
                "123",
                config=app.config,
                tokens=expired_tokens,
                tm=tm,
            )

            # Simulate a request that triggers token refresh failure
            with patch("shared.fitbit.requests.request") as mock_request:
                mock_response_401 = MagicMock()
                mock_response_401.status_code = 401
                mock_request.return_value = mock_response_401

                # Expect an HTTPError due to failed token refresh
                with pytest.raises(
                    requests.exceptions.HTTPError,
                    match="Token refresh failed",
                ):
                    session.get("https://api.fitbit.com/1/user/-/profile.json")


def test_get_fitbit_oauth_session_tm_get_api_tokens_failure(app):
    with (
        app.app_context(),
        patch.object(
            tm,
            "get_api_tokens",
            side_effect=Exception("TM get_api_tokens failed"),
        ),
        pytest.raises(Exception, match="TM get_api_tokens failed"),
    ):
        get_fitbit_oauth_session("123", config=app.config, tm=tm)


def test_get_fitbit_oauth_session_tm_add_or_update_api_token_failure(app):
    with app.app_context():
        # Mock expired access token and valid refresh token
        expired_tokens = {
            "access_token": "expired_access_token",
            "refresh_token": "fake_refresh_token",
            "expires_at": int(time.time()) - 3600,
        }

        # Use a single with statement with multiple contexts
        with (
            patch.object(tm, "get_api_tokens") as mock_get_api_tokens,
            patch.object(
                tm,
                "add_or_update_api_token",
                side_effect=Exception("TM add_or_update_api_token failed"),
            ),
            patch("shared.fitbit.WebApplicationClient") as mock_client_class,
            patch("shared.fitbit.requests.post") as mock_post,
        ):
            mock_get_api_tokens.return_value = expired_tokens
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock token refresh response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600,
            }
            mock_post.return_value = mock_response

            # Initialize the OAuth2 session
            session = get_fitbit_oauth_session(
                "123",
                config=app.config,
                tokens=expired_tokens,
                tm=tm,
            )

            # Simulate a request that triggers token refresh
            with patch("shared.fitbit.requests.request") as mock_request:
                mock_response_401 = MagicMock()
                mock_response_401.status_code = 401
                mock_request.return_value = mock_response_401

                # Expect an Exception due to failed token update
                with pytest.raises(
                    Exception,
                    match="TM add_or_update_api_token failed",
                ):
                    session.get("https://api.fitbit.com/1/user/-/profile.json")


def test_get_fitbit_oauth_session_tm_add_or_update_api_token_partial_update(
    app,
):
    with app.app_context():
        # Mock expired access token and existing refresh token
        expired_tokens = {
            "access_token": "expired_access_token",
            "refresh_token": "existing_refresh_token",
            "expires_at": int(time.time()) - 3600,
        }

        # Mock tm.get_api_tokens to return expired tokens
        with patch.object(tm, "get_api_tokens") as mock_get_api_tokens:
            mock_get_api_tokens.return_value = expired_tokens

            # Mock tm.add_or_update_api_token to perform partial update (e.g., missing refresh_token)
            with patch.object(
                tm, "add_or_update_api_token"
            ) as mock_add_update_api_token:
                # Define a side effect function to simulate partial update
                def add_update_side_effect(api_name, ditti_id, tokens):
                    if tokens.get("access_token"):
                        expired_tokens["access_token"] = tokens["access_token"]
                    if tokens.get("refresh_token"):
                        expired_tokens["refresh_token"] = tokens["refresh_token"]
                    if tokens.get("expires_at"):
                        expired_tokens["expires_at"] = tokens["expires_at"]

                mock_add_update_api_token.side_effect = add_update_side_effect

                # Mock WebApplicationClient
                with patch(
                    "shared.fitbit.WebApplicationClient"
                ) as mock_client_class:
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client

                    # Mock token refresh response with partial data (e.g., missing refresh_token)
                    with patch("shared.fitbit.requests.post") as mock_post:
                        mock_response = MagicMock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = {
                            "access_token": "updated_access_token",
                            # "refresh_token" is omitted to simulate partial update
                            "expires_in": 3600,
                        }
                        mock_post.return_value = mock_response

                        # Initialize the OAuth2 session
                        session = get_fitbit_oauth_session(
                            "123",
                            config=app.config,
                            tokens=expired_tokens,
                            tm=tm,
                        )

                        # Simulate a request that returns 401 and then 200 after refresh
                        with patch(
                            "shared.fitbit.requests.request"
                        ) as mock_request:
                            # First call returns 401
                            mock_response_401 = MagicMock()
                            mock_response_401.status_code = 401
                            # Second call returns 200
                            mock_response_200 = MagicMock()
                            mock_response_200.status_code = 200
                            mock_request.side_effect = [
                                mock_response_401,
                                mock_response_200,
                            ]

                            response = session.get(
                                "https://api.fitbit.com/1/user/-/profile.json"
                            )
                            assert response.status_code == 200
                            assert mock_post.called
                            assert mock_add_update_api_token.called

                            # Verify that the refresh_token remains unchanged
                            assert (
                                expired_tokens["refresh_token"]
                                == "existing_refresh_token"  # noqa: S105
                            )
