import logging
import os
import time
import base64
import hashlib
import requests
from functools import lru_cache
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask import current_app, session, make_response
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


def initialize_oauth_and_security_params(user_type):
    """
    Initialize OAuth client and generate security parameters for authentication flow.

    This function:
    1. Initializes the appropriate OAuth client (participant or researcher)
    2. Generates a secure nonce for ID token validation
    3. Generates a secure state parameter for CSRF protection
    4. Generates PKCE code_verifier and code_challenge for authorization code security

    Args:
        user_type (str): Either "participant" or "researcher"

    Returns:
        dict: Security parameters needed for OAuth authentication
            - nonce: The generated nonce
            - state: The generated state parameter
            - code_verifier: The PKCE code verifier
            - code_challenge: The PKCE code challenge
    """
    # Initialize the appropriate OAuth client
    if user_type == "participant":
        from aws_portal.utils.cognito.participant.auth_utils import init_oauth_client
        init_oauth_client()
    else:  # researcher
        from aws_portal.utils.cognito.researcher.auth_utils import init_researcher_oauth_client
        init_researcher_oauth_client()

    # Generate and store nonce for ID token validation
    nonce = secrets.token_urlsafe(32)
    session["cognito_nonce"] = nonce
    session["cognito_nonce_generated"] = int(
        datetime.now(timezone.utc).timestamp())

    # Generate and store state for CSRF protection
    state = secrets.token_urlsafe(32)
    session["cognito_state"] = state

    # Generate and store PKCE code_verifier and code_challenge
    code_verifier = generate_code_verifier()
    code_challenge = create_code_challenge(code_verifier)
    session["cognito_code_verifier"] = code_verifier

    # Return all security parameters
    return {
        "nonce": nonce,
        "state": state,
        "code_verifier": code_verifier,
        "code_challenge": code_challenge
    }


# Cache for JWKS to avoid repeated HTTP requests
@lru_cache(maxsize=1)
def get_cognito_jwks(jwks_url):
    """
    Retrieve and cache the JSON Web Key Set (JWKS) from Cognito.

    Args:
        jwks_url (str): The URL to the JWKS endpoint

    Returns:
        dict: The JWKS response or None if request failed
    """
    try:
        response = requests.get(jwks_url)
        if response.ok:
            return response.json()
        logger.error(f"Failed to fetch JWKS: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error fetching JWKS: {str(e)}")
        return None


def generate_code_verifier(length: int = 128) -> str:
    """
    Generates a high-entropy cryptographic random string for PKCE (Proof Key for Code Exchange).

    Args:
        length (int, optional): Length of the code verifier. Must be between 43 and 128 characters.
                                Defaults to 128.

    Returns:
        str: A securely generated code verifier string.

    Raises:
        ValueError: If the specified length is not within the allowed range.
    """
    if not 43 <= length <= 128:
        raise ValueError("length must be between 43 and 128 characters")
    code_verifier = base64.urlsafe_b64encode(os.urandom(length))\
        .rstrip(b"=")\
        .decode("utf-8")
    return code_verifier[:length]


def create_code_challenge(code_verifier: str) -> str:
    """
    Creates a S256 code challenge from the provided code verifier for PKCE.

    Args:
        code_verifier (str): The code verifier string.

    Returns:
        str: The generated code challenge string.
    """
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge)\
        .rstrip(b"=")\
        .decode("utf-8")
    return code_challenge


class CognitoAuthBase:
    """Base class for Cognito authentication operations."""

    def __init__(self, user_type):
        """
        Initialize with user type (participant or researcher).

        Args:
            user_type (str): Either "participant" or "researcher"
        """
        self.user_type = user_type
        self.oauth_client_name = "oidc" if user_type == "participant" else "researcher_oidc"

    def get_config_prefix(self):
        """Get the configuration prefix for this user type."""
        return f"COGNITO_{self.user_type.upper()}"

    def get_config(self, key):
        """Get a configuration value for this user type."""
        return current_app.config[f"{self.get_config_prefix()}_{key}"]

    def validate_access_token(self, access_token, refresh_token=None):
        """
        Validates the access token and refreshes it if expired.

        Args:
            access_token (str): The access token to validate
            refresh_token (str, optional): The refresh token to use if access_token is expired

        Returns:
            tuple: (success, result)
                - If success is True, result is None or dict with new_token
                - If success is False, result contains an error message
        """
        try:
            # Check token expiration
            claims = jwt.decode(access_token, options={
                                "verify_signature": False})
            exp = claims.get("exp", 0)
            now = int(time.time())

            # Token still valid
            if exp > now:
                return True, None

            # Token expired, try to refresh
            if not refresh_token:
                logger.warning(
                    "Access token expired but no refresh token available")
                return False, "Session expired. Please login again."

            # Attempt token refresh
            try:
                domain = self.get_config("DOMAIN")
                client_id = self.get_config("CLIENT_ID")
                client_secret = self.get_config("CLIENT_SECRET")

                token_url = f"https://{domain}/oauth2/token"
                data = {
                    "grant_type": "refresh_token",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token
                }
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                response = requests.post(token_url, data=data, headers=headers)

                if not response.ok:
                    status_code = response.status_code
                    error_body = response.json() if response.content else {}

                    # Check for expired refresh token
                    if status_code == 400 and error_body.get("error") == "invalid_grant":
                        logger.error(
                            "Refresh token has expired or been revoked")
                        return False, "Session expired. Please login again."

                    logger.error(
                        f"Failed to refresh token: HTTP {status_code} - {error_body}")
                    return False, "Session refresh failed. Please login again."

                # Success - return new token
                token_data = response.json()
                new_access_token = token_data["access_token"]
                logger.info("Successfully refreshed access token")
                return True, {"new_token": new_access_token}

            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}")
                return False, "Session refresh failed. Please login again."

        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return False, "Authentication failed"

    def validate_token_for_authenticated_route(self, id_token):
        """
        Validate ID token for authenticated routes (without nonce validation).

        This is a secure alternative to parse_and_validate_id_token when validating
        existing tokens in authenticated routes where nonce isn't available.

        Args:
            id_token (str): The ID token to validate

        Returns:
            tuple: (success, result)
                - If success is True, result contains the parsed user info
                - If success is False, result contains an error message
        """
        try:
            # First, decode the token without verification to get the header and basic claims
            unverified_header = jwt.get_unverified_header(id_token)

            unverified_claims = jwt.decode(
                id_token,
                options={"verify_signature": False}
            )

            # Check basic claims before fetching keys
            # Check token_use
            if unverified_claims.get("token_use") != "id":
                logger.error(
                    f"Invalid token use: {unverified_claims.get('token_use')}")
                return False, "Authentication failed"

            # Check issuer
            region = self.get_config("REGION")
            user_pool_id = self.get_config("USER_POOL_ID")
            expected_issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
            if unverified_claims.get("iss") != expected_issuer:
                logger.error(f"Invalid issuer: {unverified_claims.get('iss')}")
                return False, "Authentication failed"

            # Check audience
            expected_audience = self.get_config("CLIENT_ID")
            if unverified_claims.get("aud") != expected_audience:
                logger.error(
                    f"Invalid audience: {unverified_claims.get('aud')}")
                return False, "Authentication failed"

            # Check expiration
            now = int(time.time())
            if unverified_claims.get("exp", 0) <= now:
                logger.warning("ID token has expired")
                return False, "Session expired. Please login again."

            # Manually verify signature using PyJWT instead of Authlib
            try:
                # Fetch JWKs from Cognito
                jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
                jwks = get_cognito_jwks(jwks_url)

                if not jwks:
                    logger.error(
                        f"Failed to fetch JWKS: {jwks_url}")
                    return False, "Authentication service unavailable"

                # Find the key that matches our token's key ID
                kid = unverified_header.get("kid")
                key = None
                for jwk in jwks.get("keys", []):
                    if jwk.get("kid") == kid:
                        key = jwk
                        break

                if not key:
                    logger.error(f"No matching key found for kid: {kid}")
                    return False, "Authentication failed"

                # Get public key in PEM format for PyJWT
                from jwt.algorithms import RSAAlgorithm
                public_key = RSAAlgorithm.from_jwk(key)

                # Verify the token
                claims = jwt.decode(
                    id_token,
                    public_key,
                    algorithms=["RS256"],
                    audience=expected_audience,
                    issuer=expected_issuer,
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iat": True,
                        "verify_aud": True,
                        "verify_iss": True
                    }
                )

                # Validation successful
                return True, claims

            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired during verification")
                return False, "Session expired. Please login again."
            except jwt.InvalidTokenError as e:
                logger.error(f"Invalid token during verification: {str(e)}")
                return False, "Authentication failed"
            except Exception as e:
                logger.error(
                    f"Error during manual token verification: {str(e)}")
                return False, "Authentication failed"

        except ExpiredSignatureError:
            logger.warning("ID token has expired")
            return False, "Session expired. Please login again."
        except InvalidTokenError as e:
            logger.error(f"Invalid ID token: {str(e)}")
            return False, "Authentication failed"
        except Exception as e:
            logger.error(f"Error validating ID token: {str(e)}")
            return False, "Authentication failed"


def clear_auth_cookies(response):
    """
    Clear authentication cookies from a response.

    Args:
        response: Flask response object to clear cookies from

    Returns:
        The response object with cleared cookies
    """
    # Clear all auth cookies
    for cookie_name in ["id_token", "access_token", "refresh_token"]:
        response.set_cookie(
            cookie_name, "", expires=0,
            httponly=True, secure=True, samesite="None"
        )

    return response


def set_auth_cookies(response, token):
    """
    Set authentication cookies on a response.

    Args:
        response: Flask response object to set cookies on
        token: Dict containing tokens (id_token, access_token, and optionally refresh_token)

    Returns:
        The response object with set cookies
    """
    # Set ID token cookie
    response.set_cookie(
        "id_token", token["id_token"],
        httponly=True, secure=True, samesite="None"
    )

    # Set access token cookie
    response.set_cookie(
        "access_token", token["access_token"],
        httponly=True, secure=True, samesite="None"
    )

    # Set refresh token cookie if present
    if "refresh_token" in token:
        response.set_cookie(
            "refresh_token", token["refresh_token"],
            httponly=True, secure=True, samesite="None"
        )

    return response


def validate_security_params(request_state):
    """
    Validate the security parameters in a callback request.

    This function:
    1. Validates the state parameter to prevent CSRF attacks
    2. Retrieves the code_verifier for PKCE validation
    3. Validates the nonce

    Args:
        request_state (str): The state parameter from the request

    Returns:
        tuple: (success, result)
            - If success is True, result is a dict with code_verifier
            - If success is False, result is a response object with error details
    """
    # Validate state parameter to prevent CSRF attacks
    state = session.pop("cognito_state", None)
    if not state or state != request_state:
        logger.warning("Invalid state parameter in callback")
        return False, make_response({"msg": "Invalid authentication request"}, 401)

    # Get code_verifier for PKCE
    code_verifier = session.pop("cognito_code_verifier", None)
    if not code_verifier:
        logger.warning("Missing code_verifier in session")
        return False, make_response({"msg": "Authentication request rejected"}, 401)

    # Validate nonce
    nonce = session.pop("cognito_nonce", None)
    nonce_generated = session.pop("cognito_nonce_generated", 0)

    # Check if nonce is valid
    nonce_age = int(datetime.now(timezone.utc).timestamp()) - nonce_generated
    if not nonce or nonce_age > 300:  # 5 minutes expiration
        logger.warning(f"Invalid or expired nonce. Age: {nonce_age}s")
        return False, make_response({"msg": "Authentication session expired"}, 401)

    # Return success with security parameters
    return True, {
        "code_verifier": code_verifier,
        "nonce": nonce
    }


def get_cognito_logout_url(user_type):
    """
    Build the Cognito logout URL with appropriate parameters.

    Args:
        user_type (str): Either "participant" or "researcher"

    Returns:
        str: The Cognito logout URL
    """
    # Get the appropriate configuration based on user type
    prefix = f"COGNITO_{user_type.upper()}"
    domain = current_app.config[f"{prefix}_DOMAIN"]
    client_id = current_app.config[f"{prefix}_CLIENT_ID"]
    logout_uri = current_app.config[f"{prefix}_LOGOUT_URI"]

    # Build the query parameters
    params = {
        "client_id": client_id,
        "logout_uri": logout_uri,
        "response_type": "code"
    }

    # Return the full logout URL
    return f"https://{domain}/logout?{urlencode(params)}"
