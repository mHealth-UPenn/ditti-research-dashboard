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

from flask import make_response


def create_error_response(message, status_code=401, error_code=None):
    """
    Create a standardized error response.

    Args:
        message (str): The user-friendly error message
        status_code (int): The HTTP status code (default: 401)
        error_code (str, optional): An optional error code for the client

    Returns
    -------
        Response: A Flask response with standardized error format
    """
    response = {"msg": message}

    if error_code:
        response["code"] = error_code

    return make_response(response, status_code)


def create_success_response(
    data=None, message="Operation successful", status_code=200
):
    """
    Create a standardized success response.

    Args:
        data (dict, optional): The response data
        message (str): The success message (default: "Operation successful")
        status_code (int): The HTTP status code (default: 200)

    Returns
    -------
        tuple: (response_dict, status_code) for Flask to convert to
            a JSON response
    """
    response = {}

    if data:
        # First merge data into response
        response.update(data)

    # Then set the message to ensure it takes precedence
    response["msg"] = message

    return response, status_code
