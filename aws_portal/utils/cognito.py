from functools import lru_cache, wraps
import json
import logging
import traceback

from flask import current_app, make_response, request
import jwt
from jwt.exceptions import InvalidTokenError, PyJWTError, ExpiredSignatureError
import requests
from requests.exceptions import RequestException
from sqlalchemy import select, func

from aws_portal.extensions import db
from aws_portal.models import StudySubject


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_cognito_jwks(participant_pool: bool):
    """
    Fetches and caches the JWKS (JSON Web Key Set) from the AWS Cognito User Pool.

    Returns:
        dict: JSON representation of the JWKS, which contains public keys for verifying tokens.

    Raises:
        ValueError: If the Cognito domain format is invalid.
        RequestException: If the JWKS could not be fetched due to a request issue.
    """
    if not participant_pool:
        raise ValueError("Only participant pool is supported at this time.")
    try:
        region = current_app.config['COGNITO_PARTICIPANT_REGION']
        user_pool_id = current_app.config['COGNITO_PARTICIPANT_USER_POOL_ID']
        issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        keys_url = f"{issuer}/.well-known/jwks.json"

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
        jwks = get_cognito_jwks(participant_pool=True)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise InvalidTokenError("No 'kid' found in token header.")

        # Locate the public key with matching 'kid' in JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        # Clear cache and retry if the key is not found (in case of key rotation)
        if not key:
            get_cognito_jwks.cache_clear()
            jwks = get_cognito_jwks(participant_pool=True)
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


def refresh_access_token(participant_pool: bool, refresh_token: str) -> str:
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
    if not participant_pool:
        raise ValueError("Only participant pool is supported at this time.")
    try:
        # Prepare the request data for the token refresh request
        cognito_domain = current_app.config['COGNITO_PARTICIPANT_DOMAIN']
        token_issuer_endpoint = f"https://{cognito_domain}/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
            "refresh_token": refresh_token
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Send the token refresh request and parse the response for the new access token
        response = requests.post(
            token_issuer_endpoint,
            data=data,
            headers=headers
        )
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


def verify_token(participant_pool: bool, token: str, token_use: str = "id") -> dict:
    """
    Decodes and verifies a JWT token (ID or Access) using the provided public key,
    audience, and issuer.

    Based on https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html

    Args:
        token (str): JWT token to be decoded and verified.
        token_use (str): Type of the token ('id' or 'access').

    Returns:
        dict: Decoded token claims if verification succeeds.

    Raises:
        PyJWTError: If token verification fails.
    """
    if not participant_pool:
        raise ValueError("Only participant pool is supported at this time.")
    try:
        # Retrieve public key
        public_key = get_public_key(token)

        if token_use not in ["id", "access"]:
            raise InvalidTokenError("Invalid token type specified.")

        # Decode and verify the token 'iss' claim and 'aud' claim for id tokens
        audience = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
        region = current_app.config['COGNITO_PARTICIPANT_REGION']
        user_pool_id = current_app.config['COGNITO_PARTICIPANT_USER_POOL_ID']
        issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=audience if token_use == "id" else None,
            issuer=issuer,
            options={"verify_aud": False} if token_use == "access" else None,
            # Allow 5 second leeway for clock skew.
            # Necessary for deleting Cognito user then immediatly creating new one.
            leeway=5
        )

        # Verify the 'token_use' claim
        if claims.get("token_use") != token_use:
            raise InvalidTokenError(
                f'Invalid token_use. Expected "{token_use}".')

        # Verify the 'client_id' claim in access tokens
        if token_use == "access":
            if claims.get("client_id") != current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]:
                raise InvalidTokenError(
                    "Access token 'client_id' does not match.")

        return claims

    except jwt.ExpiredSignatureError:
        logger.error("Token has expired.")
        raise
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise


def get_token_scopes(access_token: str) -> list:
    """
    Decodes the JWT access token and retrieves the scopes.

    Args:
        access_token (str): The JWT access token.

    Returns:
        list: A list of scopes included in the access token.
    """
    try:
        # Decode the token without verifying the signature
        decoded_token = jwt.decode(access_token, options={
                                   "verify_signature": False})

        # Extract scopes
        scopes = decoded_token.get("scope", "")
        scope_list = scopes.split()

        return scope_list
    except jwt.DecodeError as e:
        logger.error(f"Failed to decode access token: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        raise


def cognito_auth_required(f):
    """
    Decorator for routes to enforce Cognito authentication using tokens from cookies.

    This decorator verifies the access and ID tokens from cookies, handles token refresh if needed,
    extracts `ditti_id` from the ID token, and passes it to the decorated function.

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
            verify_token(True, access_token, token_use="access")
        except ExpiredSignatureError:
            # Attempt to refresh access token if expired
            if not refresh_token:
                return make_response({"msg": "Missing refresh token."}, 401)
            try:
                # Refresh the access token
                new_access_token = refresh_access_token(True, refresh_token)
                verify_token(True, new_access_token, token_use="access")

                response = make_response()
                response.set_cookie(
                    "access_token",
                    new_access_token,
                    httponly=True,
                    secure=True
                )
                access_token = new_access_token
            except Exception as e:
                return make_response({"msg": f"Failed to refresh access token: {str(e)}"}, 401)
        except InvalidTokenError as e:
            return make_response({"msg": f"Invalid access token: {str(e)}"}, 401)

        # Verify ID token and extract `ditti_id`
        try:
            claims = verify_token(True, id_token, token_use="id")
            cognito_ditti_id = claims.get("cognito:username")

            if not cognito_ditti_id:
                return make_response({"msg": "cognito:username not found in token."}, 400)

            # Cognito stores ditti IDs in lowercase, so retrieve actual ditti ID from the database instead.
            stmt = select(StudySubject.ditti_id)\
                .where(func.lower(StudySubject.ditti_id) == cognito_ditti_id)
            ditti_id = db.session.execute(stmt).scalar()

            if ditti_id is None:
                logger.warning(f"Participant with cognito:username {cognito_ditti_id} not found in database.")
                return make_response({"msg": f"Participant {cognito_ditti_id} not found."}, 400)

        except ExpiredSignatureError:
            return make_response({"msg": "ID token has expired."}, 401)
        except InvalidTokenError as e:
            return make_response({"msg": f"Invalid ID token: {str(e)}"}, 401)
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return make_response({"msg": "Unexpected server error."}, 500)

        # Pass `ditti_id` to the decorated function
        return f(*args, ditti_id=ditti_id, **kwargs)

    return decorated
