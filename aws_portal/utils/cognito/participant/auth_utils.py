import logging
from flask import current_app
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import time
import requests
from functools import lru_cache
from aws_portal.extensions import oauth

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


def init_oauth_client():
    """
    Initialize OAuth client for Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    if "oidc" not in oauth._clients:
        region = current_app.config["COGNITO_PARTICIPANT_REGION"]
        user_pool_id = current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"]
        domain = current_app.config["COGNITO_PARTICIPANT_DOMAIN"]
        client_id = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
        client_secret = current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"]

        oauth.register(
            name="oidc",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid aws.cognito.signin.user.admin"},
            authorize_url=f"https://{domain}/oauth2/authorize",
            access_token_url=f"https://{domain}/oauth2/token",
            userinfo_endpoint=f"https://{domain}/oauth2/userInfo",
            jwks_uri=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        )


def validate_access_token(access_token, refresh_token=None):
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
        claims = jwt.decode(access_token, options={"verify_signature": False})
        exp = claims.get("exp", 0)
        now = int(time.time())

        # Token still valid
        if exp > now:
            return True, None

        # Token expired, try to refresh
        if not refresh_token:
            logger.warning(
                "Access token expired but no refresh token available")
            return False, "Token expired and no refresh token available"

        # Attempt token refresh
        try:
            domain = current_app.config["COGNITO_PARTICIPANT_DOMAIN"]
            client_id = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
            client_secret = current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"]

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
                    logger.error("Refresh token has expired or been revoked")
                    return False, "Refresh token expired - please log in again"

                logger.error(
                    f"Failed to refresh token: HTTP {status_code} - {error_body}")
                return False, "Failed to refresh token"

            # Success - return new token
            token_data = response.json()
            new_access_token = token_data["access_token"]
            logger.info("Successfully refreshed access token")
            return True, {"new_token": new_access_token}

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False, "Error during token refresh"

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


def validate_token_for_authenticated_route(id_token):
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
            return False, "Invalid token type"

        # Check issuer
        expected_issuer = f"https://cognito-idp.{current_app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{current_app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}"
        if unverified_claims.get("iss") != expected_issuer:
            logger.error(f"Invalid issuer: {unverified_claims.get('iss')}")
            return False, "Invalid token issuer"

        # Check audience
        expected_audience = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
        if unverified_claims.get("aud") != expected_audience:
            logger.error(f"Invalid audience: {unverified_claims.get('aud')}")
            return False, "Invalid token audience"

        # Check expiration
        now = int(time.time())
        if unverified_claims.get("exp", 0) <= now:
            logger.warning("ID token has expired")
            return False, "Token expired"

        # Manually verify signature using PyJWT instead of Authlib
        try:
            # Fetch JWKs from Cognito
            jwks_url = f"https://cognito-idp.{current_app.config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{current_app.config['COGNITO_PARTICIPANT_USER_POOL_ID']}/.well-known/jwks.json"
            jwks = get_cognito_jwks(jwks_url)

            if not jwks:
                logger.error(
                    f"Failed to fetch JWKS: {jwks_url}")
                return False, "Failed to validate token: couldn't fetch keys"

            # Find the key that matches our token's key ID
            kid = unverified_header.get("kid")
            key = None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    key = jwk
                    break

            if not key:
                logger.error(f"No matching key found for kid: {kid}")
                return False, "Token validation failed: no matching key"

            # Get public key in PEM format for PyJWT
            # This is a simple implementation - in production you might want to use a library
            # that properly converts JWK to PEM format
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

            # Check that we got expected user information
            if "cognito:username" not in claims:
                logger.warning("No cognito:username found in ID token")
                return False, "Invalid token content"

            return True, claims

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired during verification")
            return False, "Token expired"
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token during verification: {str(e)}")
            return False, f"Invalid token: {str(e)}"
        except Exception as e:
            logger.error(f"Error during manual token verification: {str(e)}")
            return False, f"Authentication error: {str(e)}"

    except ExpiredSignatureError:
        logger.warning("ID token has expired")
        return False, "Token expired"
    except InvalidTokenError as e:
        logger.error(f"Invalid ID token: {str(e)}")
        return False, f"Invalid token: {str(e)}"
    except Exception as e:
        logger.error(f"Error validating ID token: {str(e)}")
        return False, f"Authentication error: {str(e)}"
