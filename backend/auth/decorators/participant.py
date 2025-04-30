# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import functools
import logging

from flask import make_response, request

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

    Args:
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

        # Call the decorated function with ditti_id
        return decorated_func(ditti_id=ditti_id, *args, **kwargs)

    return wrapper
