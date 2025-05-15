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

import pytest
from flask import Flask, Response

from backend.auth.utils.cookies import clear_auth_cookies, set_auth_cookies


@pytest.fixture
def mock_app():
    """Create a minimal Flask app for testing without database dependencies."""
    app = Flask(__name__)
    return app


def test_set_auth_cookies(mock_app):
    """
    Test setting standard authentication cookies.

    Verifies that id_token, access_token, and refresh_token cookies are set with
    proper security flags (HttpOnly, Secure, SameSite).
    """
    with mock_app.app_context():
        # Setup a test response and token dictionary
        response = Response("Test")
        tokens = {
            "access_token": "test-access-token",
            "id_token": "test-id-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
        }

        result = set_auth_cookies(response, tokens)

        # Extract all Set-Cookie headers
        cookies = [h for h in result.headers if h[0] == "Set-Cookie"]

        # Verify all expected cookies are present
        assert any("id_token" in h[1] for h in cookies)
        assert any("access_token" in h[1] for h in cookies)
        assert any("refresh_token" in h[1] for h in cookies)

        # Verify security flags for each auth cookie
        for cookie in cookies:
            if any(
                token_name in cookie[1]
                for token_name in ["id_token", "access_token", "refresh_token"]
            ):
                assert "HttpOnly" in cookie[1]
                assert "Secure" in cookie[1]
                assert "SameSite" in cookie[1]


def test_set_auth_cookies_without_refresh(mock_app):
    """
    Test setting auth cookies when no refresh token is provided.

    Verifies the function correctly handles tokens without a refresh_token,
    which occurs during certain authentication flows.
    """
    with mock_app.app_context():
        response = Response("Test")
        tokens = {
            "access_token": "test-access-token",
            "id_token": "test-id-token",
            "expires_in": 3600,
        }

        result = set_auth_cookies(response, tokens)

        cookies = [h for h in result.headers if h[0] == "Set-Cookie"]

        # Verify id_token and access_token are set but refresh_token is not
        assert any("id_token" in h[1] for h in cookies)
        assert any("access_token" in h[1] for h in cookies)
        assert not any("refresh_token" in h[1] for h in cookies)


def test_clear_auth_cookies(mock_app):
    """
    Test clearing authentication cookies.

    Verifies that all authentication cookies are properly expired by setting
    their expiration date to the past.
    """
    with mock_app.app_context():
        response = Response("Test")

        # Set test cookies first to ensure they exist
        for cookie_name in ["id_token", "access_token", "refresh_token"]:
            response.set_cookie(cookie_name, "test-value")

        result = clear_auth_cookies(response)

        cookies = [h for h in result.headers if h[0] == "Set-Cookie"]

        # Verify all cookies have been expired by checking for Expires attribute
        for cookie_name in ["id_token", "access_token", "refresh_token"]:
            assert any(cookie_name in h[1] and "Expires" in h[1] for h in cookies)
