from functools import wraps
import logging
from flask import make_response, request, current_app
from aws_portal.extensions import db
from aws_portal.models import Account, App, Study
from aws_portal.utils.cognito.researcher.auth_utils import (
    init_researcher_oauth_client, validate_access_token,
    validate_token_for_authenticated_route, get_account_from_email
)

logger = logging.getLogger(__name__)


def researcher_auth_required(action=None, resource=None):
    """
    Decorator that authenticates researchers using Cognito tokens and checks permissions.

    This decorator:
    1. Validates the access and ID tokens from cookies
    2. Refreshes tokens if expired
    3. Maps the researcher's email to an Account in the database
    4. Checks permissions for the action and resource (if specified)
    5. Passes the account to the decorated function

    Args:
        action (str, optional): The action to check permissions for
        resource (str, optional): The resource to check permissions for

    Returns:
        The decorated function with authentication and authorization added
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Initialize OAuth client
            init_researcher_oauth_client()

            # Get tokens from cookies
            id_token = request.cookies.get("id_token")
            access_token = request.cookies.get("access_token")
            refresh_token = request.cookies.get("refresh_token")

            # Validate that required tokens exist
            if not id_token or not access_token:
                logger.warning("Missing required authentication tokens")
                return make_response({"msg": "Missing authentication tokens."}, 401)

            # Validate access token and refresh if needed
            success, result = validate_access_token(
                access_token, refresh_token)

            if not success:
                # Handle refresh token expiration
                if "refresh token expired" in result.lower():
                    return make_response({"msg": result, "requires_relogin": True}, 401)

                logger.warning(f"Access token validation failed: {result}")
                return make_response({"msg": result}, 401)

            # Store new access token if it was refreshed
            new_access_token = None
            if isinstance(result, dict) and "new_token" in result:
                new_access_token = result["new_token"]

            # Validate ID token
            try:
                success, userinfo = validate_token_for_authenticated_route(
                    id_token)

                if not success:
                    # Handle token expiration
                    if "token expired" in userinfo.lower():
                        return make_response({"msg": userinfo, "requires_relogin": True}, 401)

                    logger.warning(f"ID token validation failed: {userinfo}")
                    return make_response({"msg": userinfo}, 401)

                # Get email from token
                email = userinfo.get("email")
                if not email:
                    logger.error("No email found in ID token")
                    return make_response({"msg": "Invalid token content"}, 401)

                # Get account from database
                account, error = get_account_from_email(email)
                if error:
                    return make_response({"msg": error}, 401)

                # Check permissions if action is provided
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
                        return make_response({"msg": "Unauthorized Request"}, 403)

                # Call the decorated function
                response = f(*args, account=account, **kwargs)

                # Add refreshed access token to response if needed
                if new_access_token:
                    if isinstance(response, tuple):
                        # Handle tuple responses (data, status_code)
                        resp_obj = make_response(response[0], response[1])
                        resp_obj.set_cookie(
                            "access_token", new_access_token,
                            httponly=True, secure=True, samesite="None"
                        )
                        return resp_obj
                    else:
                        # Handle regular responses
                        response.set_cookie(
                            "access_token", new_access_token,
                            httponly=True, secure=True, samesite="None"
                        )

                return response

            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return make_response({"msg": f"Authentication error: {str(e)}"}, 401)

        return decorated
    return decorator
