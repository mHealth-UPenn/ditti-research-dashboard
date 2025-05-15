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

from flask import make_response


def create_error_response(message, status_code=401, error_code=None):
    """
    Create a standardized error response.

    Parameters
    ----------
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
    response = {}

    if data:
        # First merge data into response
        response.update(data)

    # Then set the message to ensure it takes precedence
    response["msg"] = message

    return response, status_code
