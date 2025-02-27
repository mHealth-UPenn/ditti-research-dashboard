import functools
from flask import make_response, request, session
import logging
from aws_portal.utils.cognito.decorators import cognito_auth_required
from aws_portal.utils.cognito.researcher.auth_utils import validate_token_for_authenticated_route
from aws_portal.extensions import db
from aws_portal.models import Account, App, Study
from aws_portal.utils.cognito.researcher.auth_utils import (
    init_researcher_oauth_client,
    get_account_from_email,
    ResearcherAuth
)

logger = logging.getLogger(__name__)


def researcher_auth_required(action=None, resource=None):
    """
    Decorator that authenticates researchers using Cognito tokens and optionally checks permissions.

    This decorator:
    1. Validates the token using the base cognito_auth_required decorator
    2. If action/resource are specified, also checks the researcher's permissions
    3. Passes the account to the decorated function instead of token_claims
    4. Ensures archived accounts cannot authenticate

    Args:
        action (str, optional): The action to check permissions for
        resource (str, optional): The resource to check permissions for

    Returns:
        The decorated function with authentication and authorization added
    """
    # If called without parameters (as a direct decorator)
    if callable(action):
        # In this case, action is actually the function to decorate
        decorated_function = action

        # Use the base decorator without permission checks
        base_decorator = cognito_auth_required(
            validate_token_for_authenticated_route)

        # Create a wrapper that converts token_claims to account
        @functools.wraps(decorated_function)
        def wrapper(token_claims, *args, **kwargs):
            # Get email from token claims
            email = token_claims.get("email")
            if not email:
                logger.warning("No email found in token claims")
                return make_response({"msg": "Authentication failed"}, 401)

            # Check if an account with this email exists, regardless of archived status
            any_account = Account.query.filter_by(email=email).first()

            # If account exists but is archived
            if any_account and any_account.is_archived:
                logger.warning(
                    f"Attempt to access with archived account: {email}")
                return make_response({"msg": "Account unavailable. Please contact support."}, 403)

            # Get account from database (already filtered for non-archived)
            auth = ResearcherAuth()
            account = auth.get_account_from_email(email)
            if not account:
                # This should not happen with the above check, but just in case
                logger.warning(f"No active account found for email: {email}")
                return make_response({"msg": "Invalid credentials"}, 401)

            # Call the decorated function with account instead of token_claims
            return decorated_function(account=account, *args, **kwargs)

        # Apply the base decorator to our wrapper
        return base_decorator(wrapper)

    # If called with parameters (as a factory)
    def decorator(func):
        # Use the base decorator for token validation
        base_decorator = cognito_auth_required(
            validate_token_for_authenticated_route)

        # Create a wrapper that handles both authentication and permission checks
        @functools.wraps(func)
        def wrapper(token_claims, *args, **kwargs):
            # Get email from token claims
            email = token_claims.get("email")
            if not email:
                logger.warning("No email found in token claims")
                return make_response({"msg": "Authentication failed"}, 401)

            # Check if an account with this email exists, regardless of archived status
            any_account = Account.query.filter_by(email=email).first()

            # If account exists but is archived
            if any_account and any_account.is_archived:
                logger.warning(
                    f"Attempt to access with archived account: {email}")
                return make_response({"msg": "Account unavailable. Please contact support."}, 403)

            # Get account from database (already filtered for non-archived)
            auth = ResearcherAuth()
            account = auth.get_account_from_email(email)
            if not account:
                # This should not happen with the above check, but just in case
                logger.warning(f"No active account found for email: {email}")
                return make_response({"msg": "Invalid credentials"}, 401)

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

        # Apply the base decorator to our wrapper
        return base_decorator(wrapper)

    return decorator
