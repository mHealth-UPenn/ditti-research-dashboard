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
from functools import wraps

from flask import current_app, make_response, request
from flask_jwt_extended import current_user, verify_jwt_in_request

from backend.models import App, Study

logger = logging.getLogger(__name__)


def auth_required(action, _resource=None):
    """
    Wrap a view that requires permissions for a given action and resource.

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
