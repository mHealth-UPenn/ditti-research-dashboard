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

import logging
from datetime import timedelta

from flask import current_app
from flask_jwt_extended import (
    create_access_token,
    get_csrf_token,
    set_access_cookies,
    unset_access_cookies,
    unset_refresh_cookies,
)

logger = logging.getLogger(__name__)


def clear_auth_cookies(response):
    """
    Clear authentication cookies from a response.

    This function uses flask-jwt-extended utilities to clear JWT-managed
    cookies (access token, refresh token, and the associated XSRF-TOKEN),
    ensuring that app configuration for domain, path, secure, and samesite
    are respected. It also manually clears any other custom auth cookies
    like 'id_token'.

    Parameters
    ----------
        response: Flask response object to clear cookies from

    Returns
    -------
        The response object with cleared cookies
    """
    # Clear JWT specific cookies using flask-jwt-extended helpers
    # These helpers use the app's JWT_COOKIE_* configurations
    unset_access_cookies(response)  # Clears access_token and XSRF-TOKEN
    unset_refresh_cookies(response)  # Clears refresh_token

    # Manually clear other custom application-specific auth cookies.
    # These cookies are set in set_auth_cookies.
    custom_cookie_names = ["id_token", "access_token", "refresh_token"]

    # Determine cookie attributes from app config
    secure_cookie = not (current_app.debug or current_app.testing)
    if "JWT_COOKIE_SECURE" in current_app.config:
        secure_cookie = current_app.config["JWT_COOKIE_SECURE"]

    samesite_cookie = "Lax"
    if "JWT_COOKIE_SAMESITE" in current_app.config:
        samesite_cookie = current_app.config["JWT_COOKIE_SAMESITE"]

    domain_cookie = current_app.config.get("JWT_COOKIE_DOMAIN", None)
    path_cookie = current_app.config.get("JWT_COOKIE_PATH", "/")

    for cookie_name in custom_cookie_names:
        response.set_cookie(
            cookie_name,
            "",
            expires=0,
            httponly=True,
            secure=secure_cookie,
            samesite=samesite_cookie,
            domain=domain_cookie,
            path=path_cookie,
        )

    return response


def set_auth_cookies(response, token):
    """
    Set authentication cookies on a response.

    Parameters
    ----------
        response: Flask response object to set cookies on
        token: Dict containing tokens (id_token, access_token,
            and optionally refresh_token)

    Returns
    -------
        The response object with set cookies
    """
    # Determine cookie attributes consistently
    # Secure attribute
    if "JWT_COOKIE_SECURE" in current_app.config:
        secure_cookie = current_app.config["JWT_COOKIE_SECURE"]
    else:
        secure_cookie = not (current_app.debug or current_app.testing)

    # SameSite attribute
    if "JWT_COOKIE_SAMESITE" in current_app.config:
        auth_samesite = current_app.config["JWT_COOKIE_SAMESITE"]
    else:
        # Infer based on debug/testing status only if not explicitly set in config
        auth_samesite = (
            "Lax" if (current_app.debug or current_app.testing) else "None"
        )

    cookie_path = current_app.config.get("JWT_COOKIE_PATH", "/")
    cookie_domain = current_app.config.get("JWT_COOKIE_DOMAIN", None)

    # Flask pre-3.0 used 'None' for cross-site cookies; browsers now require these to be 'Secure'.
    # Auth cookies (like id_token, access_token) are typically set with samesite='None' (and secure=True)
    # to support OIDC redirects across different sites.
    # For the XSRF-TOKEN cookie, samesite='Lax' is generally recommended.

    # Set ID token cookie
    response.set_cookie(
        "id_token",
        token["id_token"],
        httponly=True,
        secure=secure_cookie,
        samesite=auth_samesite,
        max_age=3600,
        domain=cookie_domain,
        path=cookie_path,
    )

    # Set access token cookie
    response.set_cookie(
        "access_token",
        token["access_token"],
        httponly=True,
        secure=secure_cookie,
        samesite=auth_samesite,
        max_age=3600,
        domain=cookie_domain,
        path=cookie_path,
    )

    # Set refresh token cookie if present
    if "refresh_token" in token:
        response.set_cookie(
            "refresh_token",
            token["refresh_token"],
            httponly=True,
            secure=secure_cookie,
            samesite=auth_samesite,
            max_age=86400,
            domain=cookie_domain,
            path=cookie_path,
        )

    # Create a short-lived JWT whose sole purpose is to transport the CSRF
    # double-submit value. The identity is irrelevant for our use-case.
    csrf_jwt = create_access_token(
        identity="csrf", expires_delta=timedelta(hours=1)
    )

    # This helper sets BOTH the HttpOnly JWT cookie and the non-HttpOnly
    # CSRF cookie (named according to our JWT_* config options).
    set_access_cookies(response, csrf_jwt)

    # Expose the CSRF token via header so the SPA can refresh its cached copy
    response.headers["X-XSRF-TOKEN"] = get_csrf_token(csrf_jwt)

    return response
