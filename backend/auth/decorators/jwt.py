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
from functools import wraps

from flask import current_app, make_response, request
from flask_jwt_extended import current_user, verify_jwt_in_request

from backend.models import App, Study

logger = logging.getLogger(__name__)


def auth_required(action, _resource=None):
    """
    Wraps a view that requires permissions for a given action and resource.

    DEPRECATED: This decorator is maintained for backward compatibility.
    Consider using more specific decorators like participant_auth_required or
    researcher_auth_required instead.

    Args
    ----
    action: str
        The action to check permissions for
    _resource: str (optional)
        The resource to check permissions for
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _, jwt_data = verify_jwt_in_request()

            # Check CSRF token
            csrf_methods = current_app.config["JWT_CSRF_METHODS"]
            csrf_header = current_app.config["JWT_ACCESS_CSRF_HEADER_NAME"]
            if request.method in csrf_methods:
                try:
                    csrf_token = jwt_data["csrf"]
                    if csrf_token != request.headers[csrf_header]:
                        raise ValueError
                except (ValueError, KeyError):
                    return make_response({"msg": "Missing CSRF token"}, 403)

            data = request.args or request.json
            app_id = data.get("app")
            study_id = data.get("study")
            resource = _resource or data.get("resource")

            # check whether the user has permissions
            try:
                permissions = current_user.get_permissions(app_id, study_id)
                current_user.validate_ask(action, resource, permissions)

            # when the user does not have permission
            except ValueError:
                # log an error
                app = App.query.get(app_id) if study_id else None
                study = Study.query.get(study_id) if study_id else None
                ask = f"{app} -> {study} -> {action} -> {resource}"
                s = current_user, ask
                logger.warning("Unauthorized request from {}: {}".format(*s))

                # return 403
                return make_response({"msg": "Unauthorized Request"}, 403)

            # return the view as normal
            return func(*args, **kwargs)

        return wrapper

    return decorator
