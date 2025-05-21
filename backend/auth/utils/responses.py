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

from typing import Any

from flask import Response, make_response

from backend.auth.providers.cognito.constants import (
    AUTH_ERROR_MESSAGES,
    get_error_code,
)
from backend.auth.providers.cognito.types import ErrorResponseMessageKey


def create_error_response(
    message: str | None = None,
    status_code: int = 401,
    error_code: ErrorResponseMessageKey | None = None,
    message_key: ErrorResponseMessageKey | None = None,
) -> Response:
    """
    Create a standardized error response.

    Parameters
    ----------
        message (str): The user-friendly error message
        status_code (int): The HTTP status code (default: 401)
        error_code (str, optional): An optional error code for the client
        message_key (str, optional): The key in AUTH_ERROR_MESSAGES to use for
            both message and error_code (if provided, overrides both)

    Returns
    -------
        Response: A Flask response with standardized error format
    """
    # If message_key is provided, use it to get both message and error_code
    if message_key and message_key in AUTH_ERROR_MESSAGES:
        message = AUTH_ERROR_MESSAGES[message_key]
        error_code = get_error_code(message_key)
    # Otherwise, if message is a key in AUTH_ERROR_MESSAGES, use it for both
    elif message and message in AUTH_ERROR_MESSAGES and not error_code:
        error_code = get_error_code(message)
        message = AUTH_ERROR_MESSAGES[message]

    response_data: dict[str, Any] = {"msg": message}

    if error_code:
        response_data["code"] = error_code

    return make_response(response_data, status_code)


def create_success_response(
    data: dict[str, Any] | None = None,
    message: str = "Operation successful",
    status_code: int = 200,
) -> tuple[dict[str, Any], int]:
    """
    Create a standardized success response.

    Parameters
    ----------
        data (dict, optional): The response data
        message (str): The success message (default: "Operation successful")
        status_code (int): The HTTP status code (default: 200)

    Returns
    -------
        tuple: (response_dict, status_code) for Flask to convert to
            a JSON response
    """
    response_data: dict[str, Any] = {}

    if data:
        # First merge data into response
        response_data.update(data)

    # Then set the message to ensure it takes precedence
    response_data["msg"] = message

    return response_data, status_code
