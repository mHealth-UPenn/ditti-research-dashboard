import json
import jwt
import requests
import logging
from functools import lru_cache, wraps
from flask import current_app, make_response, request, g
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@lru_cache()
def get_cognito_jwks():
    """
    Fetches and caches the JWKS from the Cognito User Pool.

    Returns:
        dict: The JWKS JSON data.
    """
    try:
        cognito_domain = current_app.config['COGNITO_DOMAIN']
        logger.debug(f"Fetching JWKS for domain: {cognito_domain}")

        # Extract region from domain: e.g., your-domain.auth.us-east-1.amazoncognito.com
        try:
            region = cognito_domain.split(".")[2]
            logger.debug(f"Extracted AWS region from domain: {region}")
        except IndexError as e:
            logger.error(f"Error extracting region from Cognito domain '{
                         cognito_domain}': {e}")
            raise ValueError("Invalid Cognito domain format.")

        user_pool_id = current_app.config['COGNITO_USER_POOL_ID']
        logger.debug(f"Using User Pool ID: {user_pool_id}")

        keys_url = f"https://cognito-idp.{region}.amazonaws.com/{
            user_pool_id}/.well-known/jwks.json"
        logger.debug(f"JWKS URL: {keys_url}")

        response = requests.get(keys_url)
        response.raise_for_status()
        jwks = response.json()
        logger.debug(f"Successfully fetched JWKS: {jwks}")
        return jwks
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch JWKS from {keys_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching JWKS: {e}")
        raise


def get_public_key(token: str):
    """
    Retrieves the public key for a given token's 'kid'.

    Args:
        token (str): The JWT token.

    Returns:
        RSAAlgorithm key: The public key object.

    Raises:
        jwt.exceptions.InvalidTokenError: If the key is not found or other JWT errors.
    """
    try:
        jwks = get_cognito_jwks()
        logger.debug(f"Retrieved JWKS: {jwks}")

        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        logger.debug(f"Token 'kid' extracted: {kid}")

        if not kid:
            logger.error("No 'kid' found in token header.")
            raise jwt.exceptions.InvalidTokenError(
                "No 'kid' found in token header.")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            logger.warning(f"No matching key found in JWKS for kid: {
                           kid}. Attempting cache clear and retry.")
            # Possible key rotation, clear cache and retry
            get_cognito_jwks.cache_clear()
            jwks = get_cognito_jwks()
            logger.debug(f"JWKS after cache clear: {jwks}")
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if not key:
                logger.error(f"Public key with kid {
                             kid} not found after cache clear.")
                raise jwt.exceptions.InvalidTokenError(
                    "Public key not found in JWKS after cache clear.")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        logger.debug(f"Successfully retrieved public key for kid {
                     kid}: {public_key}")
        return public_key
    except jwt.exceptions.PyJWTError as e:
        logger.error(f"Error retrieving public key: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_public_key: {e}")
        raise


def decode_token(token, key, audience, issuer, verify_aud=True, verify_exp=True):
    """
    Decodes and verifies a JWT token using the provided key, audience, and issuer.

    Args:
        token (str): The JWT token.
        key: The public key for verification.
        audience (str): The expected audience.
        issuer (str): The expected issuer.
        verify_aud (bool): Whether to verify the audience.
        verify_exp (bool): Whether to verify the expiration.

    Returns:
        dict: The decoded token claims.
    """
    try:
        decoded = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=audience if verify_aud else None,
            issuer=issuer,
            options={"verify_aud": verify_aud, "verify_exp": verify_exp},
            leeway=60  # Adjust if needed
        )
        logger.debug(f"Successfully decoded token: {decoded}")
        return decoded
    except jwt.PyJWTError as e:
        logger.error(f"Error decoding token: {e}")
        raise


def refresh_access_token(refresh_token: str) -> str:
    """
    Refreshes the access token using the provided refresh token.

    Args:
        refresh_token (str): The refresh token.

    Returns:
        str: The new access token.

    Raises:
        Exception: If the token refresh fails.
    """
    try:
        cognito_domain = current_app.config['COGNITO_DOMAIN']
        token_url = f"https://{cognito_domain}/oauth2/token"
        logger.debug(f"Preparing to refresh access token at URL: {token_url}")

        data = {
            "grant_type": "refresh_token",
            "client_id": current_app.config["COGNITO_CLIENT_ID"],
            "refresh_token": refresh_token
        }
        logger.debug(f"Refresh token data: {data}")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        logger.debug(f"Request headers for token refresh: {headers}")

        response = requests.post(token_url, data=data, headers=headers)
        logger.debug(f"Token refresh response status: {response.status_code}")
        response.raise_for_status()
        token_data = response.json()
        logger.debug(f"Token refresh response data: {token_data}")

        new_access_token = token_data.get("access_token")
        if not new_access_token:
            logger.error(
                "No 'access_token' found in the token refresh response.")
            raise Exception("No 'access_token' found in refresh response.")

        logger.info("Successfully refreshed access token.")
        return new_access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error during access token refresh: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to refresh access token: {e}")
        raise


def cognito_auth_required(f):
    """
    Decorator to protect routes with Cognito authentication.

    It checks for 'id_token' and 'access_token' in secure cookies, verifies them,
    and handles token refresh if access_token is expired.

    Args:
        f (Callable): The route function to decorate.

    Returns:
        Callable: The wrapped function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.debug("Entering cognito_auth_required decorator.")

        # Extract tokens from cookies
        id_token = request.cookies.get('id_token')
        access_token = request.cookies.get('access_token')
        refresh_token = request.cookies.get('refresh_token')

        logger.debug(
            f"Retrieved tokens from cookies - ID Token: {
                'Present' if id_token else 'Missing'}, "
            f"Access Token: {'Present' if access_token else 'Missing'}, "
            f"Refresh Token: {'Present' if refresh_token else 'Missing'}"
        )

        if not id_token or not access_token:
            msg = "Missing authentication tokens."
            logger.warning(msg)
            return make_response({"msg": msg}, 401)

        # Verify access token
        try:
            public_key = get_public_key(access_token)
            logger.debug("Decoding and verifying access token.")

            # Decode access token without verifying 'aud' claim
            access_claims = jwt.decode(
                access_token,
                public_key,
                algorithms=["RS256"],
                issuer=(
                    f"https://cognito-idp.{current_app.config['COGNITO_DOMAIN'].split('.')[
                        2]}.amazonaws.com/"
                    f"{current_app.config['COGNITO_USER_POOL_ID']}"
                ),
                options={"verify_aud": False},
                leeway=60
            )
            logger.debug(f"Access token claims: {access_claims}")

            # Manually verify 'client_id' since 'aud' is not present in access_token
            expected_client_id = current_app.config["COGNITO_CLIENT_ID"]
            token_client_id = access_claims.get("client_id")
            logger.debug(f"Expected client_id: {
                         expected_client_id}, Token client_id: {token_client_id}")

            if token_client_id != expected_client_id:
                logger.error(f"Access token 'client_id' mismatch: expected {
                             expected_client_id}, got {token_client_id}")
                raise jwt.InvalidTokenError(
                    "Access token 'client_id' does not match.")

            # Store claims in Flask's global context
            g.cognito_access_claims = access_claims
            logger.info("Access token successfully verified.")
        except jwt.ExpiredSignatureError:
            logger.info("Access token has expired. Attempting to refresh.")
            if not refresh_token:
                msg = "Missing refresh token."
                logger.warning(msg)
                return make_response({"msg": msg}, 401)
            try:
                # Refresh the access token
                new_access_token = refresh_access_token(refresh_token)
                logger.debug(f"New access token obtained: {new_access_token}")

                # Decode the new access token without verifying 'aud' claim
                decoded_new_access = jwt.decode(
                    new_access_token,
                    get_public_key(new_access_token),
                    algorithms=["RS256"],
                    issuer=(
                        f"https://cognito-idp.{current_app.config['COGNITO_DOMAIN'].split('.')[
                            2]}.amazonaws.com/"
                        f"{current_app.config['COGNITO_USER_POOL_ID']}"
                    ),
                    # Handle expiration manually
                    options={"verify_aud": False, "verify_exp": False}
                )
                logger.debug(f"New access token claims: {decoded_new_access}")

                new_access_exp = decoded_new_access.get(
                    "exp", int(datetime.utcnow().timestamp()) + 3600)
                logger.debug(f"New access token expires at: {
                             datetime.fromtimestamp(new_access_exp, tz=timezone.utc)} UTC")

                # Manually verify 'client_id'
                token_client_id = decoded_new_access.get("client_id")
                logger.debug(f"Expected client_id: {
                             expected_client_id}, New Token client_id: {token_client_id}")

                if token_client_id != expected_client_id:
                    logger.error(f"New access token 'client_id' mismatch: expected {
                                 expected_client_id}, got {token_client_id}")
                    raise jwt.InvalidTokenError(
                        "New access token 'client_id' does not match.")

                # Set the new access token in the cookie
                response = make_response(f(*args, **kwargs))
                response.set_cookie(
                    "access_token",
                    new_access_token,
                    expires=datetime.fromtimestamp(
                        new_access_exp, tz=timezone.utc),
                    httponly=True,
                    secure=True,  # Ensure HTTPS in production
                    samesite="Lax"
                )
                logger.info("Access token refreshed and cookie updated.")

                # Update the global context with new access claims
                g.cognito_access_claims = decoded_new_access

                return response
            except Exception as e:
                msg = f"Failed to refresh access token: {str(e)}"
                logger.error(msg)
                return make_response({"msg": msg}, 401)
        except jwt.InvalidTokenError as e:
            msg = f"Invalid access token: {str(e)}"
            logger.warning(msg)
            return make_response({"msg": msg}, 401)

        # Verify ID token
        try:
            public_key_id = get_public_key(id_token)
            logger.debug("Decoding and verifying ID token.")

            id_claims = jwt.decode(
                id_token,
                public_key_id,
                algorithms=["RS256"],
                audience=current_app.config["COGNITO_CLIENT_ID"],
                issuer=(
                    f"https://cognito-idp.{current_app.config['COGNITO_DOMAIN'].split('.')[
                        2]}.amazonaws.com/"
                    f"{current_app.config['COGNITO_USER_POOL_ID']}"
                ),
                leeway=60
            )
            logger.debug(f"ID token claims: {id_claims}")

            # Store claims in Flask's global context
            g.cognito_id_claims = id_claims
            logger.info("ID token successfully verified.")
        except jwt.ExpiredSignatureError:
            msg = "ID token has expired."
            logger.warning(msg)
            return make_response({"msg": msg}, 401)
        except jwt.InvalidTokenError as e:
            msg = f"Invalid ID token: {str(e)}"
            logger.warning(msg)
            return make_response({"msg": msg}, 401)

        logger.debug("User is authenticated and tokens are valid.")
        return f(*args, **kwargs)

    return decorated
