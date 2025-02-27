import functools
from flask import make_response, request, session
import logging

logger = logging.getLogger(__name__)


def cognito_auth_required(validate_token_func):
    """
    Base decorator factory for requiring Cognito authentication.

    Args:
        validate_token_func: Function to validate a token
            Should take an id_token string and return (success, result) tuple

    Returns:
        decorator: A decorator that requires the user to be authenticated
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
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

            # Validate the token
            success, result = validate_token_func(id_token)

            if not success:
                # If validation failed, result contains error message
                return make_response({"msg": "Authentication failed"}, 401)

            # If validation succeeded, pass the token claims in kwargs
            kwargs["token_claims"] = result
            return f(*args, **kwargs)

        return decorated_function

    return decorator
