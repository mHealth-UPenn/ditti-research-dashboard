import functools
import inspect
import logging
from collections.abc import Callable
from typing import Any, TypeVar, cast

from flask import make_response

from backend.auth.controllers import ResearcherAuthController
from backend.auth.utils.auth_helpers import (
    check_permissions,
    get_token_from_request,
)
from backend.models import Account

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def researcher_auth_required(
    action: str | Callable | None = None,
    resource: str | None = None,
) -> Callable:
    """
    Authenticate researchers using tokens and optionally checks permissions.

    This decorator:
    1. Validates the token using the auth controller
    2. If action/resource are specified, also checks the researcher's permissions
    3. Passes the account to the decorated function instead of token_claims
    4. Ensures archived accounts cannot authenticate

    Parameters
    ----------
        action: The action to check permissions for or the function to decorate
        resource: The resource to check permissions for

    Returns
    -------
        The decorated function with authentication and authorization added
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: dict[str, Any]) -> Any:
            # Check if we've already authenticated in a previous decorator
            # and added account to kwargs - only add once to avoid param conflict
            if "account" in kwargs:
                # Account already authenticated and added by a previous decorator
                auth_account = cast(Account, kwargs["account"])
            else:
                # First decorator to run, need to authenticate
                id_token = get_token_from_request()

                if not id_token:
                    logger.warning("No token found in request")
                    return make_response({"msg": "Authentication required"}, 401)

                # Create auth controller and validate token
                auth_controller = ResearcherAuthController()
                auth_account, error_response = (
                    auth_controller.get_user_from_token(id_token)
                )

                if not auth_account:
                    # If validation failed, return error response
                    return error_response

                # Save account to kwargs for this and future decorators
                kwargs["account"] = auth_account

            # Check permissions if action was provided
            if isinstance(action_param, str):
                has_permission, error_response = check_permissions(
                    auth_account, action_param, resource
                )
                if not has_permission:
                    return error_response

            # Call the decorated function with account
            # Check if the function expects 'account' parameter
            sig = inspect.signature(func)

            # Simplify the parameter passing logic
            if "account" not in sig.parameters and "account" in kwargs:
                # If function doesn't expect 'account', remove it from kwargs
                kwargs.pop("account")

            return func(*args, **kwargs)

        return cast(F, wrapper)

    # Store the action parameter to use in the wrapper
    action_param = action

    # If called without parameters (as a direct decorator)
    if callable(action):
        decorated_function = action
        action_param = None
        return decorator(decorated_function)

    # If called with parameters (as a factory)
    return decorator
