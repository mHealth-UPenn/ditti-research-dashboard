import logging
from flask import current_app
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import time
import requests
import os
import base64
import hashlib
from functools import lru_cache
from aws_portal.extensions import oauth
from aws_portal.utils.cognito.common import CognitoAuthBase, get_cognito_jwks, generate_code_verifier, create_code_challenge

logger = logging.getLogger(__name__)


class ParticipantAuth(CognitoAuthBase):
    """Specialized authentication class for participants."""

    def __init__(self):
        super().__init__("participant")

    def get_user_from_claims(self, claims):
        """Extract user information from ID token claims."""
        return {
            "id": claims.get("cognito:username"),
            "email": claims.get("email"),
            "name": claims.get("name", "")
        }


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


def validate_token_for_authenticated_route(id_token):
    """
    Validate ID token for authenticated routes.
    This is a wrapper around the base class method to maintain backwards compatibility.

    Args:
        id_token (str): The ID token to validate

    Returns:
        tuple: (success, result)
            - If success is True, result contains the parsed user info
            - If success is False, result contains an error message
    """
    auth = ParticipantAuth()
    return auth.validate_token_for_authenticated_route(id_token)
