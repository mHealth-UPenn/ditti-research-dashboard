import logging
import os
import time
import base64
import hashlib
import requests
from functools import lru_cache
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask import current_app

logger = logging.getLogger(__name__)


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
