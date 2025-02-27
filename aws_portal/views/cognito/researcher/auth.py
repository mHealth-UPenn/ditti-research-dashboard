from datetime import datetime, timezone
import logging
from urllib.parse import urlencode
import boto3
import csv
import io
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, make_response, redirect, request, session, jsonify
import secrets
from aws_portal.extensions import db, oauth
from aws_portal.models import Account
from aws_portal.utils.cognito.researcher.auth_utils import (
    init_researcher_oauth_client, validate_token_for_authenticated_route, get_account_from_email, ResearcherAuth
)
from aws_portal.utils.cognito.common import (
    generate_code_verifier, create_code_challenge, initialize_oauth_and_security_params,
    clear_auth_cookies, set_auth_cookies, validate_security_params, get_cognito_logout_url,
    create_error_response, create_success_response, AUTH_ERROR_MESSAGES
)
from aws_portal.utils.cognito.researcher.decorators import researcher_auth_required

blueprint = Blueprint("researcher_cognito", __name__,
                      url_prefix="/researcher_cognito")
logger = logging.getLogger(__name__)
auth = ResearcherAuth()


def _get_account_from_token(id_token):
    """
    Extract account from a validated ID token.

    Validates the token and ensures the account exists and is not archived.

    Args:
        id_token (str): The ID token to validate

    Returns:
        tuple: (account, error_response)
            account: The researcher's Account object if valid, None otherwise
            error_response: Error response object if error occurred, None otherwise
    """
    try:
        # Validate token
        success, userinfo = validate_token_for_authenticated_route(id_token)

        if not success:
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="INVALID_TOKEN"
            )

        # Extract email
        email = userinfo.get("email")
        if not email:
            logger.warning("No email found in ID token")
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="MISSING_EMAIL"
            )

        # Check if an account with this email exists, regardless of archived status
        any_account = Account.query.filter_by(email=email).first()

        # If account exists but is archived
        if any_account and any_account.is_archived:
            logger.warning(f"Attempt to access with archived account: {email}")
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["account_archived"],
                status_code=403,
                error_code="ACCOUNT_ARCHIVED"
            )

        # Get active account from database (not archived)
        account = auth.get_account_from_email(email)
        if not account:
            if any_account:  # This shouldn't happen given the check above, but just for defensive coding
                logger.warning(
                    f"Attempt to access with archived account: {email}")
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["account_archived"],
                    status_code=403,
                    error_code="ACCOUNT_ARCHIVED"
                )
            else:
                logger.warning(f"No account found for email: {email}")
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_credentials"],
                    status_code=401,
                    error_code="ACCOUNT_NOT_FOUND"
                )

        return account, None

    except Exception as e:
        logger.error(f"Error retrieving account from token: {str(e)}")
        return None, create_error_response(
            AUTH_ERROR_MESSAGES["system_error"],
            status_code=500,
            error_code="TOKEN_PROCESSING_ERROR"
        )


@blueprint.route("/login")
def login():
    """
    Redirect researchers to the Cognito login page.

    This endpoint:
    1. Generates a secure nonce for ID token validation
    2. Generates a secure state parameter for CSRF protection
    3. Generates PKCE code_verifier and code_challenge for authorization code security
    4. Redirects to the Cognito authorization endpoint with all security parameters

    Returns:
        Redirect to Cognito login page
    """
    # Initialize OAuth client and generate security parameters
    security_params = initialize_oauth_and_security_params("researcher")

    # Redirect to Cognito authorization endpoint with all security parameters
    return oauth.researcher_oidc.authorize_redirect(
        current_app.config["COGNITO_RESEARCHER_REDIRECT_URI"],
        scope="openid email profile",
        nonce=security_params["nonce"],
        state=security_params["state"],
        code_challenge=security_params["code_challenge"],
        code_challenge_method="S256"
    )


@blueprint.route("/callback")
def cognito_callback():
    """
    Handle Cognito's authorization callback for researchers.

    This endpoint:
    1. Validates the state parameter to prevent CSRF attacks
    2. Provides the code_verifier for PKCE validation
    3. Exchanges the authorization code for tokens
    4. Validates the ID token with the stored nonce
    5. Retrieves the researcher in the database
    6. Sets secure cookies with the tokens
    7. Redirects to the frontend application

    Returns:
        Redirect to frontend with tokens set in cookies, or
        400 Bad Request on authentication errors
        403 Forbidden if account is archived
    """
    init_researcher_oauth_client()

    try:
        # Validate security parameters
        success, result = validate_security_params(request.args.get("state"))
        if not success:
            return result

        code_verifier = result["code_verifier"]
        nonce = result["nonce"]

        # Exchange code for tokens with PKCE code_verifier
        token = oauth.researcher_oidc.authorize_access_token(
            code_verifier=code_verifier)

        # Parse ID token with nonce validation
        try:
            userinfo = oauth.researcher_oidc.parse_id_token(token, nonce=nonce)
        except Exception as e:
            logger.error(f"Failed to validate ID token: {str(e)}")
            return create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="TOKEN_VALIDATION_FAILED"
            )

        # Extract account using ID token (which includes validation and archive checks)
        account, error = _get_account_from_token(token["id_token"])
        if error:
            return error

        # Set session data
        session["account_id"] = account.id
        session["user"] = userinfo

        # Create response with redirect to frontend
        frontend_url = current_app.config.get(
            "CORS_ORIGINS", "http://localhost:3000")
        admin_url = f"{frontend_url}/coordinator"
        response = make_response(redirect(admin_url))

        # Set auth cookies
        return set_auth_cookies(response, token)

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        db.session.rollback()
        return create_error_response(
            AUTH_ERROR_MESSAGES["auth_failed"],
            status_code=400,
            error_code="AUTHENTICATION_ERROR"
        )


@blueprint.route("/logout")
def logout():
    """
    Log out the researcher from the application and Cognito.

    This endpoint:
    1. Clears the session data
    2. Builds a logout URL for Cognito
    3. Clears authentication cookies
    4. Redirects to Cognito logout

    Returns:
        Redirect to Cognito logout URL with cookies cleared
    """
    init_researcher_oauth_client()

    # Clear session
    session.clear()

    # Create response with redirect to Cognito logout
    response = make_response(redirect(get_cognito_logout_url("researcher")))

    # Clear all auth cookies
    return clear_auth_cookies(response)


@blueprint.route("/check-login", methods=["GET"])
def check_login():
    """
    Verify active login status and return the researcher's info.

    This endpoint:
    1. Checks if the ID token exists in cookies
    2. Validates the token and extracts the account
    3. Returns the account info on success

    Returns:
        200 OK with account info on success
        401 Unauthorized if not authenticated or token invalid or account not found
        403 Forbidden if account is archived
    """
    init_researcher_oauth_client()

    # Check for ID token
    id_token = request.cookies.get("id_token")
    if not id_token:
        return create_error_response(
            AUTH_ERROR_MESSAGES["auth_required"],
            status_code=401,
            error_code="NO_TOKEN"
        )

    # Get account from token
    account, error = _get_account_from_token(id_token)
    if error:
        return error

    # Return success with account info
    return create_success_response(
        data={
            "email": account.email,
            "firstName": account.first_name,
            "lastName": account.last_name,
            "accountId": account.id,
            "msg": "Login successful"
        }
    )
