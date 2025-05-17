# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools
import inspect
import logging

from flask import make_response, request
from flask_jwt_extended import verify_jwt_in_request

from backend.auth.controllers import ParticipantAuthController

logger = logging.getLogger(__name__)


def participant_auth_required(decorated_func=None):
    """
    Authenticate participants using tokens.

    This decorator:
    1. Validates the token using the auth controller
    2. Gets the study_subject from the database based on the token claims
    3. Passes the ditti_id to the decorated function
    4. Ensures archived study subjects cannot authenticate

    Parameters
    ----------
        decorated_func (function, optional): The function to decorate.
            If None, returns a decorator.

    Returns
    -------
        The decorated function with authentication added
    """
    # Return a decorator if called without arguments
    if decorated_func is None:
        return lambda f: participant_auth_required(f)

    @functools.wraps(decorated_func)
    def wrapper(*args, **kwargs):
        # First verify the JWT with Flask-JWT-Extended to enable CSRF protection
        verify_jwt_in_request()

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
        auth_controller = ParticipantAuthController()
        ditti_id, error_response = auth_controller.get_user_from_token(id_token)

        if not ditti_id:
            # If validation failed, return error response
            return error_response

        # Check if the decorated function expects 'ditti_id'
        sig = inspect.signature(decorated_func)
        if "ditti_id" in sig.parameters:
            # Call the decorated function with ditti_id
            return decorated_func(*args, ditti_id=ditti_id, **kwargs)
        else:
            # Call the decorated function without ditti_id
            return decorated_func(*args, **kwargs)

    return wrapper
