import functools
from flask import make_response, request, session
import logging
from aws_portal.utils.cognito.decorators import cognito_auth_required
from aws_portal.utils.cognito.participant.auth_utils import (
    validate_token_for_authenticated_route,
    ParticipantAuth
)
from aws_portal.models import StudySubject
from sqlalchemy import select, func as sql_func
from aws_portal.extensions import db

logger = logging.getLogger(__name__)


def participant_auth_required(decorated_func=None):
    """
    Decorator that authenticates participants using Cognito tokens.

    This decorator:
    1. Validates the token using the base cognito_auth_required decorator
    2. Gets the study_subject from the database based on the token claims
    3. Passes the ditti_id to the decorated function
    4. Ensures archived study subjects cannot authenticate

    Args:
        decorated_func (function, optional): The function to decorate. If None, returns a decorator.

    Returns:
        The decorated function with authentication added
    """
    # Return a decorator if called without arguments
    if decorated_func is None:
        return lambda f: participant_auth_required(f)

    # Use the base decorator for token validation
    base_decorator = cognito_auth_required(
        validate_token_for_authenticated_route)

    # Create a wrapper that converts token_claims to ditti_id
    @functools.wraps(decorated_func)
    def wrapper(token_claims, *args, **kwargs):
        # Get cognito_username from token claims
        cognito_username = token_claims.get("cognito:username")
        if not cognito_username:
            logger.warning("No cognito:username found in token claims")
            return make_response({"msg": "Authentication failed"}, 401)

        # Get study_subject from database
        stmt = select(StudySubject).where(
            sql_func.lower(StudySubject.ditti_id) == cognito_username.lower()
        )
        study_subject = db.session.execute(stmt).scalar_one_or_none()

        if not study_subject:
            logger.warning(
                f"No study subject found for ID: {cognito_username}")
            return make_response({"msg": "User profile not found"}, 404)

        if study_subject.is_archived:
            logger.warning(
                f"Attempt to access with archived study subject: {cognito_username}")
            return make_response({"msg": "Account unavailable. Please contact support."}, 403)

        # Call the decorated function with ditti_id instead of study_subject
        return decorated_func(ditti_id=study_subject.ditti_id, *args, **kwargs)

    # Apply the base decorator to our wrapper
    return base_decorator(wrapper)
