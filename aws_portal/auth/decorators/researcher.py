import functools
import logging
from flask import make_response, request

from aws_portal.auth.controllers import ResearcherAuthController
from aws_portal.models import App, Study

logger = logging.getLogger(__name__)


def researcher_auth_required(action=None, resource=None):
    """
    Decorator that authenticates researchers using tokens and optionally checks permissions.

    This decorator:
    1. Validates the token using the auth controller
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

            # Create auth controller and validate token
            auth_controller = ResearcherAuthController()
            account, error_response = auth_controller.get_user_from_token(
                id_token)

            if not account:
                # If validation failed, return error response
                return error_response

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
