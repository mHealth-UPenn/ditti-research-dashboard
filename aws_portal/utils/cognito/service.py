from flask import current_app
from functools import lru_cache
import json
import logging
import jwt
from jwt.exceptions import InvalidTokenError, PyJWTError, ExpiredSignatureError
import requests
from requests.exceptions import RequestException
from aws_portal.utils.cognito.config import CognitoPoolConfig

logger = logging.getLogger(__name__)


class CognitoService:
    def __init__(self, config: CognitoPoolConfig):
        self.config = config

    @lru_cache(maxsize=1)
    def get_jwks(self):
        """
        Fetches and caches the JWKS (JSON Web Key Set) from the AWS Cognito User Pool.

        Returns:
            dict: JSON representation of the JWKS, which contains public keys for verifying tokens.

        Raises:
            RequestException: If the JWKS could not be fetched due to a request issue.
        """
        try:
            keys_url = f"{self.config.issuer}/.well-known/jwks.json"

            # Fetch and return the JWKS JSON data
            response = requests.get(keys_url)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to fetch JWKS from {keys_url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching JWKS: {str({e})}")
            raise

    def get_public_key(self, token: str):
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
            jwks = self.get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise InvalidTokenError("No 'kid' found in token header.")

            # Locate the public key with matching 'kid' in JWKS
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

            # Clear cache and retry if the key is not found (in case of key rotation)
            if not key:
                self.get_jwks.cache_clear()
                jwks = self.get_jwks()
                key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

            if not key:
                raise InvalidTokenError("Public key not found in JWKS.")

            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        except PyJWTError as e:
            logger.error(f"Error retrieving public key: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_public_key: {e}")
            raise

    def verify_token(self, token: str, token_use: str = "id") -> dict:
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
            InvalidTokenError: If the token type is invalid or the the token does not match.
        """
        try:
            public_key = self.get_public_key(token)

            if token_use not in ["id", "access"]:
                raise InvalidTokenError("Invalid token type specified.")

            claims = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.config.client_id if token_use == "id" else None,
                issuer=self.config.issuer,
                options={"verify_aud": False} if token_use == "access" else None,
                # Allow 5 second leeway for clock skew.
                # Necessary for deleting Cognito user then immediatly creating new one.
                leeway=5
            )

            # Verify the "token_use" claim
            if claims.get("token_use") != token_use:
                raise InvalidTokenError(
                    f'Invalid token_use. Expected "{token_use}".')

            # Verify the "client_id" claim in access tokens
            if token_use == "access" and claims.get("client_id") != self.config.client_id:
                raise InvalidTokenError(
                    "Access token 'client_id' does not match.")

            return claims
        except ExpiredSignatureError:
            logger.error("Token has expired.")
            raise
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during token verification: {str(e)}")
            raise

    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh an access token using a refresh token"""
        try:
            token_url = f"https://{self.config.domain}/oauth2/token"
            data = {
                "grant_type": "refresh_token",
                "client_id": self.config.client_id,
                "refresh_token": refresh_token
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            return token_data["access_token"]
        except RequestException as e:
            logger.error(f"HTTP error during token refresh: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            raise

    def get_token_scopes(access_token: str) -> list:
        """
        Decodes the JWT access token and retrieves the scopes.

        Args:
            access_token (str): The JWT access token.

        Returns:
            list: A list of scopes included in the access token.

        Raises:
            jwt.DecodeError: If the token cannot be decoded.
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
            logger.error(f"Failed to decode access token: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            raise


def get_participant_service():
    config = CognitoPoolConfig(
        client_id=current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
        client_secret=current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"],
        domain=current_app.config["COGNITO_PARTICIPANT_DOMAIN"],
        region=current_app.config["COGNITO_PARTICIPANT_REGION"],
        user_pool_id=current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"],
        redirect_uri=current_app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
        logout_uri=current_app.config["COGNITO_PARTICIPANT_LOGOUT_URI"],
    )
    return CognitoService(config)
