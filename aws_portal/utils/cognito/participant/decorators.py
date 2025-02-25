from functools import wraps
import logging
from flask import make_response, request
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito.participant.auth_utils import (
    init_oauth_client, validate_access_token, validate_token_for_authenticated_route
)

logger = logging.getLogger(__name__)


def participant_auth_required(f):
    """
    Decorator that authenticates participants using Cognito tokens.

    This decorator:
    1. Validates the access and ID tokens from cookies
    2. Refreshes tokens if expired
    3. Extracts the participant's ditti_id from the database
    4. Passes the ditti_id to the decorated function

    Args:
        f: The function to decorate

    Returns:
        The decorated function with authentication added
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Initialize OAuth client
        init_oauth_client()

        # Get tokens from cookies
        id_token = request.cookies.get("id_token")
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        # Validate that required tokens exist
        if not id_token or not access_token:
            logger.warning("Missing required authentication tokens")
            return make_response({"msg": "Missing authentication tokens."}, 401)

        # Validate access token and refresh if needed
        success, result = validate_access_token(access_token, refresh_token)

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

            # Get ditti_id from database
            try:
                cognito_username = userinfo.get("cognito:username")

                # Find study subject by ditti_id (case-insensitive)
                study_subject = StudySubject.query.filter(
                    db.func.lower(
                        StudySubject.ditti_id) == cognito_username.lower()
                ).first()

                if not study_subject:
                    logger.error(f"Participant {cognito_username} not found.")
                    return make_response({"msg": "Participant not found."}, 400)

                ditti_id = study_subject.ditti_id

            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                return make_response({"msg": "Database error."}, 500)

            # Call the decorated function
            response = f(*args, ditti_id=ditti_id, **kwargs)

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
            return make_response({"msg": "Authentication error."}, 401)

    return decorated
