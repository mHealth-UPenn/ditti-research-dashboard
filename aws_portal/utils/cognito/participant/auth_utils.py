import logging
from flask import current_app
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import time
import requests
from aws_portal.extensions import oauth

logger = logging.getLogger(__name__)


def init_oauth_client():
    """
    Initialize OAuth client for Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    if "oidc" not in oauth._clients:
        oauth.register(
            name="oidc",
            client_id=current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
            client_secret=current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"],
            server_metadata_url=f"https://cognito-idp.{current_app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{current_app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid aws.cognito.signin.user.admin"},
            authorize_url=f"https://{current_app.config['COGNITO_PARTICIPANT_DOMAIN']}/oauth2/authorize",
            access_token_url=f"https://{current_app.config['COGNITO_PARTICIPANT_DOMAIN']}/oauth2/token",
            userinfo_endpoint=f"https://{current_app.config['COGNITO_PARTICIPANT_DOMAIN']}/oauth2/userInfo",
            jwks_uri=f"https://cognito-idp.{current_app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{current_app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}/.well-known/jwks.json"
        )


def validate_access_token(access_token, refresh_token=None):
    """
    Validates the access token and refreshes it if expired.

    Args:
        access_token (str): The access token to validate
        refresh_token (str, optional): The refresh token to use if access_token is expired

    Returns:
        True if valid, a response object if invalid, or dict with new token if refreshed
    """
    try:
        # Check token expiration by decoding without verification
        unverified_claims = jwt.decode(
            access_token,
            options={"verify_signature": False}
        )

        # Check expiration time
        exp = unverified_claims.get("exp", 0)
        now = int(time.time())

        if exp <= now:
            # Token expired, try to refresh
            if not refresh_token:
                logger.warning(
                    "Access token expired but no refresh token available")
                return False, "Token expired and no refresh token available"

            # Refresh the token
            try:
                token_url = f"https://{current_app.config['COGNITO_PARTICIPANT_DOMAIN']}/oauth2/token"
                data = {
                    "grant_type": "refresh_token",
                    "client_id": current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
                    "client_secret": current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"],
                    "refresh_token": refresh_token
                }
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                refresh_response = requests.post(
                    token_url, data=data, headers=headers)

                if not refresh_response.ok:
                    logger.error(
                        f"Failed to refresh token: HTTP {refresh_response.status_code}")
                    return False, "Failed to refresh token"

                token_data = refresh_response.json()
                new_access_token = token_data["access_token"]
                logger.info("Successfully refreshed access token")

                return True, {"new_token": new_access_token}

            except Exception as refresh_error:
                logger.error(f"Failed to refresh token: {str(refresh_error)}")
                return False, "Error during token refresh"

        # Token not expired, consider it valid
        return True, None

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return False, "Invalid token format"


def parse_and_validate_id_token(id_token, required_nonce=None):
    """
    Parse and validate an ID token, with proper nonce validation.

    Args:
        id_token (str): The ID token to parse and validate
        required_nonce (str, optional): The nonce that should be in the token

    Returns:
        tuple: (success, result)
            - If success is True, result contains the parsed user info
            - If success is False, result contains an error message
    """
    try:
        # Always require nonce validation in secure contexts
        if required_nonce is None and current_app.config["ENV"] != "development":
            logger.warning(
                "Missing nonce for token validation in non-development environment")
            return False, "Missing security validation"

        # Parse ID token with authlib
        userinfo = oauth.oidc.parse_id_token(
            {"id_token": id_token}, nonce=required_nonce)

        # Check that we got expected user information
        if not userinfo.get("cognito:username"):
            logger.warning("No cognito:username found in ID token")
            return False, "Invalid token content"

        return True, userinfo

    except ExpiredSignatureError as e:
        logger.warning(f"ID token expired: {str(e)}")
        return False, "Token expired"
    except InvalidTokenError as e:
        logger.error(f"Invalid ID token: {str(e)}")
        return False, "Invalid token"
    except Exception as e:
        logger.error(f"Error processing ID token: {str(e)}")
        return False, "Authentication error"
