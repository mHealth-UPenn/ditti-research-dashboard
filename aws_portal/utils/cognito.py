import json
import jwt
from jwt.exceptions import InvalidTokenError, PyJWTError, ExpiredSignatureError
import requests
from requests.exceptions import RequestException
import logging
from functools import lru_cache, wraps
from flask import current_app, make_response, request

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_cognito_jwks():
    """
    Fetches and caches the JWKS (JSON Web Key Set) from the AWS Cognito User Pool.

    Returns:
        dict: JSON representation of the JWKS, which contains public keys for verifying tokens.

    Raises:
        ValueError: If the Cognito domain format is invalid.
        RequestException: If the JWKS could not be fetched due to a request issue.
    """
    try:
        # Obtain Cognito domain and User Pool ID from the configuration
        cognito_domain = current_app.config['COGNITO_DOMAIN']
        user_pool_id = current_app.config['COGNITO_USER_POOL_ID']

        # Extract AWS region from the domain format and construct the JWKS URL
        region = cognito_domain.split(".")[2]
        keys_url = (
            f"https://cognito-idp.{region}.amazonaws.com/"
            f"{user_pool_id}/.well-known/jwks.json"
        )

        # Fetch and return the JWKS JSON data
        response = requests.get(keys_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch JWKS from {keys_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching JWKS: {e}")
        raise


def get_public_key(token: str):
    """
    Retrieves the public key for a JWT based on its 'kid' (key ID) field.

    Args:
        token (str): JWT token from which to retrieve the public key.

    Returns:
        RSAAlgorithm key: The public key object for verifying the JWT.

    Raises:
        InvalidTokenError: If the key ID in the token is not found in the JWKS.
    """
    try:
        # Get JWKS and extract 'kid' from the token header
        jwks = get_cognito_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise InvalidTokenError("No 'kid' found in token header.")

        # Locate the public key with matching 'kid' in JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        # Clear cache and retry if the key is not found (in case of key rotation)
        if not key:
            get_cognito_jwks.cache_clear()
            jwks = get_cognito_jwks()
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        if not key:
            raise InvalidTokenError("Public key not found in JWKS.")

        # Return public key
        return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    except PyJWTError as e:
        logger.error(f"Error retrieving public key: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_public_key: {e}")
        raise


def decode_token(token, key, audience, issuer, verify_aud=True, verify_exp=True):
    """
    Decodes and verifies a JWT token using the provided public key, audience, and issuer.

    Args:
        token (str): JWT token to be decoded and verified.
        key: Public key for verifying the JWT.
        audience (str): Expected audience for the token.
        issuer (str): Expected issuer of the token.
        verify_aud (bool): Flag to indicate if audience should be verified.
        verify_exp (bool): Flag to indicate if expiration should be verified.

    Returns:
        dict: Decoded token claims if verification succeeds.

    Raises:
        PyJWTError: If token verification fails.
    """
    try:
        # Decode the token and verify claims based on provided options
        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=audience if verify_aud else None,
            issuer=issuer,
            options={"verify_aud": verify_aud, "verify_exp": verify_exp}
        )
    except PyJWTError as e:
        logger.error(f"Error decoding token: {e}")
        raise


def refresh_access_token(refresh_token: str) -> str:
    """
    Refreshes the access token using the provided refresh token by making an OAuth2 token request.

    Args:
        refresh_token (str): The refresh token for obtaining a new access token.

    Returns:
        str: The new access token, if refresh is successful.

    Raises:
        RequestException: If there is an HTTP error in the token refresh request.
        Exception: For any unexpected issues in the refresh process.
    """
    try:
        cognito_domain = current_app.config['COGNITO_DOMAIN']
        # TODO: Record this in the config
        token_url = f"https://{cognito_domain}/oauth2/token"

        # Prepare the request data for the token refresh request
        data = {
            "grant_type": "refresh_token",
            "client_id": current_app.config["COGNITO_CLIENT_ID"],
            "refresh_token": refresh_token
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Send the token refresh request and parse the response for the new access token
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        new_access_token = token_data.get("access_token")

        if not new_access_token:
            raise Exception("No 'access_token' found in refresh response.")

        return new_access_token
    except RequestException as e:
        logger.error(f"HTTP error during access token refresh: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to refresh access token: {e}")
        raise


def cognito_auth_required(f):
    """
    Decorator for routes to enforce Cognito authentication using tokens from cookies.

    This decorator verifies the access and ID tokens from cookies, handles token refresh if needed,
    and populates Flask's global context with token claims.

    Args:
        f (Callable): The route function to decorate.

    Returns:
        Callable: The wrapped function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract tokens from cookies and check presence of access and ID tokens
        id_token = request.cookies.get('id_token')
        access_token = request.cookies.get('access_token')
        refresh_token = request.cookies.get('refresh_token')

        if not id_token or not access_token:
            return make_response({"msg": "Missing authentication tokens."}, 401)

        # Verify access token and handle token refresh if expired
        try:
            public_key = get_public_key(access_token)
            access_claims = jwt.decode(
                access_token,
                public_key,
                algorithms=["RS256"],
                issuer=(
                    f"https://cognito-idp."
                    f"{current_app.config['COGNITO_DOMAIN'].split('.')[2]}"
                    f".amazonaws.com/"
                    f"{current_app.config['COGNITO_USER_POOL_ID']}"
                )
            )

            # Confirm 'client_id' in access claims
            if access_claims.get("client_id") != current_app.config["COGNITO_CLIENT_ID"]:
                raise InvalidTokenError(
                    "Access token 'client_id' does not match."
                )
        except ExpiredSignatureError:
            # Attempt to refresh access token if expired
            if not refresh_token:
                return make_response({"msg": "Missing refresh token."}, 401)
            try:
                # Refresh the access token
                new_access_token = refresh_access_token(refresh_token)
                new_access_claims = jwt.decode(
                    new_access_token,
                    get_public_key(new_access_token),
                    algorithms=["RS256"],
                    issuer=(
                        f"https://cognito-idp."
                        f"{current_app.config['COGNITO_DOMAIN'].split('.')[2]}"
                        f".amazonaws.com/"
                        f"{current_app.config['COGNITO_USER_POOL_ID']}"
                    )
                )

                response = make_response(f(*args, **kwargs))
                response.set_cookie(
                    "access_token",
                    new_access_token,
                    httponly=True,
                    secure=True
                )
                return response
            except Exception as e:
                return make_response({"msg": f"Failed to refresh access token: {str(e)}"}, 401)
        except InvalidTokenError as e:
            return make_response({"msg": f"Invalid access token: {str(e)}"}, 401)

        # Verify ID token and check that claims match the expected values
        try:
            public_key_id = get_public_key(id_token)
            id_claims = jwt.decode(
                id_token,
                public_key_id,
                algorithms=["RS256"],
                audience=current_app.config["COGNITO_CLIENT_ID"],
                issuer=(
                    f"https://cognito-idp."
                    f"{current_app.config['COGNITO_DOMAIN'].split('.')[2]}"
                    f".amazonaws.com/"
                    f"{current_app.config['COGNITO_USER_POOL_ID']}"
                )
            )
        except ExpiredSignatureError:
            return make_response({"msg": "ID token has expired."}, 401)
        except InvalidTokenError as e:
            return make_response({"msg": f"Invalid ID token: {str(e)}"}, 401)

        return f(*args, **kwargs)

    return decorated
