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
from aws_portal.extensions import oauth, db
from aws_portal.models import Account
from aws_portal.utils.cognito.common import CognitoAuthBase, get_cognito_jwks, generate_code_verifier, create_code_challenge

logger = logging.getLogger(__name__)


class ResearcherAuth(CognitoAuthBase):
    """Specialized authentication class for researchers."""

    def __init__(self):
        super().__init__("researcher")

    def get_user_from_claims(self, claims):
        """Extract user information from ID token claims."""
        return {
            "email": claims.get("email"),
            "name": claims.get("name", "")
        }

    def get_account_from_email(self, email):
        """Get Account object from email address."""
        if not email:
            return None

        return Account.query.filter_by(email=email).first()


def init_researcher_oauth_client():
    """
    Initialize OAuth client for Researcher Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    if "researcher_oidc" not in oauth._clients:
        region = current_app.config["COGNITO_RESEARCHER_REGION"]
        user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]
        domain = current_app.config["COGNITO_RESEARCHER_DOMAIN"]
        client_id = current_app.config["COGNITO_RESEARCHER_CLIENT_ID"]
        client_secret = current_app.config["COGNITO_RESEARCHER_CLIENT_SECRET"]

        oauth.register(
            name="researcher_oidc",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
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
    auth = ResearcherAuth()
    return auth.validate_token_for_authenticated_route(id_token)


def get_account_from_email(email):
    """
    Helper function to get an Account object from an email address.
    Maintained for backwards compatibility.

    Args:
        email (str): Email address to look up

    Returns:
        Account or None: The matching Account object or None if not found
    """
    auth = ResearcherAuth()
    return auth.get_account_from_email(email)
