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

import logging

from flask import Response, make_response, request

from backend.models import Account, App, Study

logger = logging.getLogger(__name__)


def get_token_from_request() -> str | None:
    """
    Extract authentication token from request headers or cookies.

    Returns
    -------
        str or None: The extracted token or None if not found
    """
    # Check for token in Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix

    # Check for token in cookies
    return request.cookies.get("id_token")


def check_permissions(
    auth_account: Account, action: str, resource_param: str | None = None
) -> tuple[bool, Response | None]:
    """
    Check if the authenticated account has the required permissions.

    Parameters
    ----------
        auth_account: The authenticated account
        action: The action to check permissions for
        resource_param: The resource to check permissions for

    Returns
    -------
        tuple: (success, error_response)
            success: True if permission check passed, False otherwise
            error_response: Error response if check failed, None otherwise
    """
    # Get data from appropriate sources based on request method
    if request.method == "GET":
        data = request.args or {}
    else:
        data = request.json or request.args or {}

    app_id = data.get("app")
    study_id = data.get("study")

    # If resource not provided as param, get from request
    resource_to_check = resource_param or data.get("resource")

    try:
        permissions = auth_account.get_permissions(app_id, study_id)
        auth_account.validate_ask(action, resource_to_check, permissions)
        return True, None
    except ValueError:
        # Log unauthorized request
        app = App.query.get(app_id) if app_id else None
        study = Study.query.get(study_id) if study_id else None
        ask = f"{app} -> {study} -> {action} -> {resource_to_check}"
        logger.warning(f"Unauthorized request from {auth_account}: {ask}")
        return False, make_response({"msg": "Insufficient permissions"}, 403)
