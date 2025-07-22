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
from flask import Flask
from flask_jwt_extended import JWTManager

from backend.auth.utils.cookies import clear_auth_cookies, set_auth_cookies


@pytest.fixture
def mock_app():
    """Create a minimal Flask app for testing with JWT configurations."""
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="super-secret",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_SESSION_COOKIE=True,
        JWT_CSRF_IN_COOKIES=True,
        JWT_COOKIE_SECURE=False,
        JWT_COOKIE_SAMESITE="Lax",
        JWT_COOKIE_DOMAIN=None,
        JWT_COOKIE_PATH="/",
        JWT_ACCESS_COOKIE_NAME="access_token_cookie",
        JWT_ACCESS_COOKIE_PATH="/",
        JWT_REFRESH_COOKIE_NAME="refresh_token_cookie",
        JWT_REFRESH_COOKIE_PATH="/",
        JWT_ACCESS_CSRF_COOKIE_NAME="XSRF-TOKEN",
        JWT_ACCESS_CSRF_HEADER_NAME="X-XSRF-TOKEN",
    )
    JWTManager(app)
    return app


def test_set_auth_cookies(mock_app):
    """
    Test setting standard authentication cookies.

    Verifies that id_token, access_token, refresh_token, and CSRF cookies
    are set with proper security flags (HttpOnly, Secure, SameSite) as per
    the test configuration.
    """
    with mock_app.app_context():
        response = mock_app.response_class("Test")
        tokens = {
            "access_token": "test-access-token",
            "id_token": "test-id-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
        }

        result = set_auth_cookies(response, tokens)
        all_set_cookie_strings = result.headers.getlist("Set-Cookie")

        expected_cookies_http_only_status = {
            "id_token": True,
            "access_token": True,
            "refresh_token": True,
            mock_app.config["JWT_ACCESS_COOKIE_NAME"]: True,
            mock_app.config["JWT_ACCESS_CSRF_COOKIE_NAME"]: False,
        }

        set_cookie_names = [s.split("=", 1)[0] for s in all_set_cookie_strings]

        for cookie_name in expected_cookies_http_only_status:
            assert cookie_name in set_cookie_names, (
                f"Cookie {cookie_name} not set. Found: {set_cookie_names}"
            )

        for header_value_str in all_set_cookie_strings:
            cookie_name_from_header = header_value_str.split("=", 1)[0]
            if cookie_name_from_header in expected_cookies_http_only_status:
                if expected_cookies_http_only_status[cookie_name_from_header]:
                    assert "HttpOnly" in header_value_str, (
                        f"HttpOnly missing in {cookie_name_from_header}: {header_value_str}"
                    )
                else:
                    assert "HttpOnly" not in header_value_str, (
                        f"HttpOnly unexpectedly in {cookie_name_from_header}: {header_value_str}"
                    )
                if mock_app.config["JWT_COOKIE_SECURE"]:
                    assert "Secure" in header_value_str, (
                        f"Secure missing in {cookie_name_from_header}: {header_value_str}"
                    )
                else:
                    assert "Secure" not in header_value_str, (
                        f"Secure unexpectedly in {cookie_name_from_header}: {header_value_str}"
                    )
                assert (
                    f"SameSite={mock_app.config['JWT_COOKIE_SAMESITE']}"
                    in header_value_str
                ), (
                    f"SameSite={mock_app.config['JWT_COOKIE_SAMESITE']} missing in {cookie_name_from_header}: {header_value_str}"
                )


def test_set_auth_cookies_without_refresh(mock_app):
    """
    Test setting auth cookies when no refresh token is provided.

    Verifies the function correctly handles tokens without a refresh_token,
    which occurs during certain authentication flows.
    """
    with mock_app.app_context():
        response = mock_app.response_class("Test")
        tokens = {
            "access_token": "test-access-token",
            "id_token": "test-id-token",
            "expires_in": 3600,
        }

        result = set_auth_cookies(response, tokens)
        all_set_cookie_strings = result.headers.getlist("Set-Cookie")
        set_cookie_names = [s.split("=", 1)[0] for s in all_set_cookie_strings]

        assert "id_token" in set_cookie_names
        assert "access_token" in set_cookie_names
        assert "refresh_token" not in set_cookie_names

        assert (
            mock_app.config["JWT_ACCESS_CSRF_COOKIE_NAME"] in set_cookie_names
        ), (
            f"CSRF cookie {mock_app.config['JWT_ACCESS_CSRF_COOKIE_NAME']} not found. Found: {set_cookie_names}"
        )
        assert mock_app.config["JWT_ACCESS_COOKIE_NAME"] in set_cookie_names, (
            f"Access cookie {mock_app.config['JWT_ACCESS_COOKIE_NAME']} not found. Found: {set_cookie_names}"
        )


def test_clear_auth_cookies(mock_app):
    """
    Test clearing authentication cookies.

    Verifies that all relevant authentication cookies are properly expired.
    """
    with mock_app.app_context():
        response = mock_app.response_class("Test")

        access_cookie_name = mock_app.config["JWT_ACCESS_COOKIE_NAME"]
        refresh_cookie_name = mock_app.config["JWT_REFRESH_COOKIE_NAME"]
        csrf_access_cookie_name = mock_app.config["JWT_ACCESS_CSRF_COOKIE_NAME"]

        custom_cookie_names = ["id_token", "access_token", "refresh_token"]

        all_cookies_expected_to_be_cleared = [
            access_cookie_name,
            refresh_cookie_name,
            csrf_access_cookie_name,
            *custom_cookie_names,
        ]

        for cookie_name in all_cookies_expected_to_be_cleared:
            response.set_cookie(cookie_name, "test-value")

        result = clear_auth_cookies(response)
        cookies_headers = [h for h in result.headers if h[0] == "Set-Cookie"]

        for cookie_name_to_check in all_cookies_expected_to_be_cleared:
            found_and_cleared = False
            for _, header_val in cookies_headers:
                if (
                    cookie_name_to_check in header_val
                    and "Expires=" in header_val
                ):
                    if mock_app.config["JWT_COOKIE_DOMAIN"]:
                        assert (
                            f"Domain={mock_app.config['JWT_COOKIE_DOMAIN']}"
                            in header_val
                        )
                    assert (
                        f"Path={mock_app.config['JWT_COOKIE_PATH']}" in header_val
                    )
                    if mock_app.config["JWT_COOKIE_SECURE"]:
                        assert "Secure" in header_val
                    else:
                        assert "Secure" not in header_val
                    assert (
                        f"SameSite={mock_app.config['JWT_COOKIE_SAMESITE']}"
                        in header_val
                    )

                    found_and_cleared = True
                    break
            assert found_and_cleared, (
                f"Cookie {cookie_name_to_check} not properly cleared with all attributes"
            )
