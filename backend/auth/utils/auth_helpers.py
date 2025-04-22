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

    Args:
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
