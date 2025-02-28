import functools
import logging
from flask import make_response, request
from aws_portal.extensions import oauth
from aws_portal.models import Account, App, Study
from aws_portal.utils.cognito.auth.base import CognitoAuthBase

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

    def get_account_from_email(self, email, include_archived=False):
        """
        Get Account object from email address.

        Args:
            email (str): The email address to search for
            include_archived (bool, optional): Whether to include archived accounts

        Returns:
            Account or None: The matching account or None if not found
        """
        if not email:
            return None

        query = Account.query.filter_by(email=email)

        if not include_archived:
            query = query.filter_by(is_archived=False)

        return query.first()

    def get_account_from_token(self, id_token, include_archived=False):
        """
        Get an account from an ID token.

        Args:
            id_token (str): The ID token
            include_archived (bool, optional): Whether to include archived accounts

        Returns:
            tuple: (account, error_message)
                account: The Account object if successful, None otherwise
                error_message: Error message if account is None, None otherwise
        """
        success, claims = self.validate_token_for_authenticated_route(id_token)

        if not success:
            return None, claims

        email = claims.get("email")
        if not email:
            logger.warning("No email found in token claims")
            return None, "Invalid token"

        # First check if account exists regardless of archived status
        any_account = self.get_account_from_email(email, include_archived=True)

        if any_account and any_account.is_archived and not include_archived:
            logger.warning(f"Attempt to access with archived account: {email}")
            return None, "Account unavailable. Please contact support."

        account = self.get_account_from_email(email, include_archived)

        if not account:
            logger.warning(f"No active account found for email: {email}")
            return None, "Invalid credentials"

        return account, None


def init_researcher_oauth_client():
    """
    Initialize OAuth client for Researcher Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    from flask import current_app

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


def researcher_auth_required(action=None, resource=None):
    """
    Decorator that authenticates researchers using Cognito tokens and optionally checks permissions.

    This decorator:
    1. Validates the token using the auth_manager
    2. If action/resource are specified, also checks the researcher's permissions
    3. Passes the account to the decorated function instead of token_claims
    4. Ensures archived accounts cannot authenticate

    Args:
        action (str, optional): The action to check permissions for
        resource (str, optional): The resource to check permissions for

    Returns:
        The decorated function with authentication and authorization added
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check for token in Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                id_token = auth_header[7:]  # Remove "Bearer " prefix
            else:
                # Check for token in cookies
                id_token = request.cookies.get("id_token")

            if not id_token:
                logger.warning("No token found in request")
                return make_response({"msg": "Authentication required"}, 401)

            # Create auth manager and validate token
            auth_manager = ResearcherAuth()
            account, error_msg = auth_manager.get_account_from_token(id_token)

            if not account:
                # If validation failed, return error response
                logger.warning(f"Token validation failed: {error_msg}")
                return make_response({"msg": error_msg if error_msg else "Authentication failed"}, 401)

            # Check permissions if action was provided
            if action:
                data = request.args or request.json or {}
                app_id = data.get("app")
                study_id = data.get("study")

                # If resource not provided as arg, get from request
                resource_to_check = resource or data.get("resource")

                try:
                    permissions = account.get_permissions(app_id, study_id)
                    account.validate_ask(
                        action, resource_to_check, permissions)
                except ValueError:
                    # Log unauthorized request
                    app = App.query.get(app_id) if app_id else None
                    study = Study.query.get(study_id) if study_id else None
                    ask = "%s -> %s -> %s -> %s" % (app,
                                                    study, action, resource_to_check)
                    logger.warning(
                        f"Unauthorized request from {account}: {ask}")
                    return make_response({"msg": "Insufficient permissions"}, 403)

            # Call the decorated function with account
            return func(account=account, *args, **kwargs)

        return wrapper

    # If called without parameters (as a direct decorator)
    if callable(action):
        decorated_function = action
        action = None
        resource = None
        return decorator(decorated_function)

    # If called with parameters (as a factory)
    return decorator
