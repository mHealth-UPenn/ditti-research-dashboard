from functools import wraps
import logging
from flask import make_response, request
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito.participant.auth_utils import init_oauth_client, validate_access_token, parse_and_validate_id_token

logger = logging.getLogger(__name__)


def participant_auth_required(f):
    """
    Decorator to authenticate participants using Cognito tokens.

    This decorator:
    1. Validates the access and ID tokens from cookies
    2. Refreshes tokens if expired
    3. Extracts the participant's ditti_id from the database
    4. Passes the ditti_id to the decorated function

    Args:
        f: The function to decorate

    Returns:
        The decorated function with added authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Initialize OAuth client if needed
        init_oauth_client()

        # Get tokens from cookies
        id_token = request.cookies.get("id_token")
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        # Check if required tokens exist
        if not id_token or not access_token:
            logger.warning("Missing required authentication tokens")
            return make_response({"msg": "Missing authentication tokens."}, 401)

        # Validate access token and refresh if needed
        success, result = validate_access_token(access_token, refresh_token)

        if not success:
            logger.warning(f"Access token validation failed: {result}")
            return make_response({"msg": result}, 401)

        # If token was refreshed, store new token for response
        new_access_token = None
        if isinstance(result, dict) and "new_token" in result:
            new_access_token = result["new_token"]

        # Validate ID token and get user info
        try:
            # Parse ID token - we can't use a nonce for existing tokens in decorators
            # but we'll enforce stricter validation in production
            success, userinfo = parse_and_validate_id_token(id_token)

            if not success:
                logger.warning(f"ID token validation failed: {userinfo}")
                return make_response({"msg": userinfo}, 401)

            cognito_username = userinfo.get("cognito:username")

            # Get ditti_id from database (Cognito stores ditti IDs in lowercase)
            try:
                # Using SQLAlchemy ORM query instead of raw SQL
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

            # If we have a new access token, add it to the response
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
