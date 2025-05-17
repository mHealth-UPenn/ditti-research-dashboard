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

import jwt
from flask import Blueprint, current_app, jsonify, make_response, request

from backend.auth.providers.cognito.base import CognitoAuthBase
from backend.auth.utils import create_error_response, set_auth_cookies

# Create API auth blueprint
blueprint = Blueprint("api_auth", __name__, url_prefix="/api/auth")
logger = logging.getLogger(__name__)


@blueprint.route("/refresh-token", methods=["POST"])
def refresh_token():
    """
    Refresh the authentication tokens using the refresh token from cookies.

    This endpoint detects whether the request is from a participant or researcher
    based on the ID token claims, and refreshes the token accordingly.

    Returns
    -------
        Response: JSON response indicating success or error
            200 OK with new tokens set in cookies if successful
            401 Unauthorized if refresh token is invalid or expired
    """
    try:
        # Extract refresh token from cookies
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            logger.warning("Refresh token missing from request")
            return create_error_response(
                message_key="no_refresh_token", status_code=401
            )

        # Use existing ID token to determine user type
        id_token = request.cookies.get("id_token")
        if not id_token:
            logger.warning("ID token missing from request")
            return create_error_response(
                message_key="no_id_token", status_code=401
            )

        # Decode the token without verification to get the cognito:groups claim
        # This will tell us if this is a participant or researcher
        try:
            claims = jwt.decode(id_token, options={"verify_signature": False})

            issuer: str = claims.get("iss", "")
            participant_pool = current_app.config.get(
                "COGNITO_PARTICIPANT_USER_POOL_ID", ""
            )
            researcher_pool = current_app.config.get(
                "COGNITO_RESEARCHER_USER_POOL_ID", ""
            )

            if participant_pool and participant_pool in issuer:
                user_type = "participant"
            elif researcher_pool and researcher_pool in issuer:
                user_type = "researcher"
            else:
                logger.error(
                    "Unable to determine user type from issuer: %s", issuer
                )
                return create_error_response(
                    message_key="invalid_token_format", status_code=401
                )

            logger.info("Detected user type: %s", user_type)

        except Exception as e:
            logger.error(f"Error decoding token: {e!s}")
            return create_error_response(
                message_key="invalid_token_format", status_code=401
            )

        # Get Cognito instance for the detected user type
        cognito_auth = CognitoAuthBase(user_type)

        # Use the CognitoAuthBase to refresh the token
        success, refresh_result = cognito_auth.refresh_id_token(refresh_token)

        if not success:
            logger.error("Token refresh failed")
            return create_error_response(
                refresh_result,
                status_code=401,
                error_code="REFRESH_FAILED",
            )

        # If successful, refresh_result contains new tokens
        new_id_token = refresh_result.get("new_id_token")
        new_access_token = refresh_result.get("new_access_token")

        if not new_id_token:
            logger.error("New ID token not found in refresh result")
            return create_error_response(
                "Token refresh failed to provide a new ID token",
                status_code=500,
                error_code="REFRESH_MISSING_NEW_ID_TOKEN",
            )

        # Validate the new ID token
        claims_success, _ = cognito_auth.validate_token_for_authenticated_route(
            new_id_token
        )
        if not claims_success:
            logger.warning("Failed to validate new ID token after refresh")
            return create_error_response(
                message_key="new_token_validation_failed", status_code=401
            )

        # Bundle tokens for cookie setter
        new_tokens_for_cookie = {
            "access_token": new_access_token or "",
            "id_token": new_id_token,
            "refresh_token": refresh_token,
        }

        # Create success response
        response = make_response(
            jsonify({"msg": "Tokens refreshed successfully"})
        )

        # Set cookies (CSRf cookies generated internally)
        response = set_auth_cookies(response, new_tokens_for_cookie)

        return response

    except Exception as e:
        logger.error(f"Token refresh error: {e!s}")
        return create_error_response(
            message_key="refresh_failed", status_code=500
        )
