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
import traceback

from flask import Blueprint, current_app, jsonify, make_response
from sqlalchemy import text

from backend.extensions import db

blueprint = Blueprint("base", __name__)
logger = logging.getLogger(__name__)


@blueprint.route("/health")
def health_check():
    """
    Verify the service is running and the flask secret key version.

    Response Syntax (200)
    ---------------------
    {
        "msg": "Service is healthy.",
        "flask_secret_key_version_id": "..."
    }

    Response syntax (500)
    ---------------------
    {
        "msg": "Service is unhealthy.",
        "flask_secret_key_version_id": "..."
    }
    """
    version_id = current_app.config.get("FLASK_SECRET_KEY_VERSION_ID", "not_set")
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify(
            {
                "msg": "Service is healthy.",
                "flask_secret_key_version_id": version_id,
            }
        )
    except Exception:
        exc = traceback.format_exc()
        logger.error(exc)
        return make_response(
            {
                "msg": "Service is unhealthy.",
                "flask_secret_key_version_id": version_id,
            },
            500,
        )


@blueprint.route("/healthz")
def healthz():
    """
    Provide a health check endpoint for monitoring purposes.

    This endpoint confirms that the application is running and returns the
    version ID of the Flask secret key currently in use, which is critical
    for validating secret rotation.
    """
    status = {
        "status": "ok",
        "flask_secret_key_version_id": current_app.config.get(
            "FLASK_SECRET_KEY_VERSION_ID", "not_set"
        ),
    }
    return jsonify(status)
