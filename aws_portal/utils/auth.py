from functools import wraps
import logging
from flask import current_app, make_response, request
from flask_jwt_extended import current_user, decode_token, verify_jwt_in_request
from aws_portal.models import App, Study

logger = logging.getLogger(__name__)


def validate_password(password):
    """
    Validates whether a given password is 8-64 characters long

    Args
    ----
    password: str
        The password to validate
    
    Returns
    -------
    str: "valid" or an error message
    """
    if len(password) < 8:
        return "Minimum password length is 8 characters"

    if 64 < len(password):
        return "Maximum password length is 64 characters"

    return "valid"
