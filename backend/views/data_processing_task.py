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
import traceback
from datetime import datetime, UTC
from flask import Blueprint, jsonify, make_response, request
from backend.extensions import db
from backend.models import LambdaTask
from backend.auth.decorators import researcher_auth_required
from backend.utils.lambda_task import create_and_invoke_lambda_task

blueprint = Blueprint("data_processing_task", __name__,
                      url_prefix="/data_processing_task")
logger = logging.getLogger(__name__)


@blueprint.route("/", defaults={"task_id": None}, methods=["GET"])
@blueprint.route("/<int:task_id>", methods=["GET"])
# Allow actions from any dashboard
@researcher_auth_required("View", "Data Retrieval Task")
def get_data_processing_tasks(account, task_id: int | None):
    """
    Retrieve all data processing tasks sorted by creation date.

    Optionally, retrieve a specific data processing task by ID. If task_id is provided, the response will contain a
    single task.

    Request:
    --------
    GET /data_processing_task/
    GET /data_processing_task/<task_id>

    Query Parameters:
    -----------------
    app: int

    Response (200 OK):
    ------------------
    [
        {
            "id": int,
            "status": str,          # "Pending", "InProgress", "Success", "Failed", or "CompletedWithErrors"
            "billedMs": int,
            "createdOn": str,       # ISO 8601 format
            "updatedOn": str,       # ISO 8601 format
            "completedOn": str,     # ISO 8601 format or null
            "logFile": str or null,
            "errorCode": str or null
        },
        ...
    ]

    Response (500 Internal Server Error):
    -------------------------------------
    {
        "msg": "Internal server error when retrieving data processing tasks."
    }
    """
    try:
        if task_id is not None:
            tasks = LambdaTask.query.filter(LambdaTask.id == task_id).all()
        else:
            # Retrieve all tasks sorted by created_on in descending order (most recent first)
            tasks = LambdaTask.query.order_by(
                LambdaTask.created_on.desc()).all()
        res = [task.meta for task in tasks]
        return jsonify(res), 200

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(f"Error retrieving data processing tasks: {exc}")
        db.session.rollback()
        return make_response({"msg": "Internal server error when retrieving data processing tasks."}, 500)


@blueprint.route("/invoke", methods=["POST"])
@researcher_auth_required("Invoke", "Data Retrieval Task")
def invoke_data_processing_task(account):
    """
    Manually invoke a data processing task.

    Request:
    --------
    POST /data_processing_task/invoke

    Body (JSON):
    ------------
    {
        "app": 1,                   # Required
    }

    Response (200 OK):
    ------------------
    {
        "msg": "Data processing task invoked successfully",
        "task": {
            "id": int,
            "status": str,          # "Pending", "InProgress", "Success", "Failed", or "CompletedWithErrors"
            "billedMs": int,
            "createdOn": str,       # ISO 8601 format
            "updatedOn": str,       # ISO 8601 format
            "completedOn": str,     # ISO 8601 format or null
            "logFile": str or null,
            "errorCode": str or null
        }
    }

    Response (400 Bad Request):
    --------------------------
    {
        "msg": "function_id is required"
    }

    Response (500 Internal Server Error):
    -------------------------------------
    {
        "msg": "Internal server error when invoking data processing task."
    }
    """
    try:
        # Create and invoke a new LambdaTask
        lambda_task = create_and_invoke_lambda_task()
        if lambda_task is None:
            raise Exception(
                "Failed to create and invoke data processing task.")

        return jsonify({
            "msg": "Data processing task invoked successfully",
            "task": lambda_task.meta
        }), 200

    except Exception:
        exc = traceback.format_exc()
        logger.warning(f"Error invoking data processing task: {exc}")
        db.session.rollback()
        return make_response({"msg": "Internal server error when invoking data processing task."}, 500)
    

@blueprint.route("/force-stop", methods=["POST"])
@researcher_auth_required("Invoke", "Data Retrieval Task")
def force_stop_data_processing_task(account):
    """
    Manually stop a data processing task.

    Request:
    --------
    POST /data_processing_task/force-stop

    Body (JSON):
    ------------
    {
        "app": 1,                   # Required
        "function_id": 1,               # Required
    }

    Response (200 OK):
    ------------------
    {
        "msg": "Data processing task stopped successfully"
    }

    Response (400 Bad Request):
    --------------------------
    {
        "msg": "function_id is required"
    }

    Response (500 Internal Server Error):
    -------------------------------------
    {
        "msg": "Internal server error when stopping data processing task."
    }
    """
    try:
        function_id = request.json.get("function_id")
        if function_id is None:
            raise make_response({"msg": "function_id is required"}, 400)

        lambda_task = LambdaTask.query.filter(LambdaTask.id == function_id).first()
        if lambda_task is None:
            raise Exception(f"Data processing task with id {function_id} not found.")
        
        lambda_task.status = "Failed"
        lambda_task.completed_on = datetime.now(UTC)
        lambda_task.error_code = "ForceStopped"
        db.session.commit()
        return jsonify({"msg": "Data processing task stopped successfully"}), 200
    except Exception:
        exc = traceback.format_exc()
        logger.warning(f"Error stopping data processing task: {exc}")
        db.session.rollback()
        return make_response({"msg": "Internal server error when stopping data processing task."}, 500)
