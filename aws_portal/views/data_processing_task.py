import logging
import traceback
from flask import Blueprint, jsonify, make_response
from aws_portal.extensions import db
from aws_portal.models import LambdaTask
from aws_portal.utils.auth import auth_required
from aws_portal.utils.lambda_task import create_and_invoke_lambda_task

blueprint = Blueprint("data_processing_task", __name__,
                      url_prefix="/data_processing_task")
logger = logging.getLogger(__name__)


@blueprint.route("/", defaults={"task_id": None}, methods=["GET"])
@blueprint.route("/<int:task_id>", methods=["GET"])
@auth_required("View", "Lambda Task")  # Allow actions from any dashboard
def get_data_processing_tasks(task_id: int | None):
    """
    Retrieve all data processing tasks sorted by creation date.

    Request:
    --------
    GET /data_processing_task/

    Query Parameters:
    -----------------
    app: 1                        # Required

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
            tasks = LambdaTask.query.order_by(LambdaTask.created_on.desc()).all()
        res = [task.meta for task in tasks]
        return jsonify(res), 200

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(f"Error retrieving data processing tasks: {exc}")
        db.session.rollback()
        return make_response({"msg": "Internal server error when retrieving data processing tasks."}, 500)


@blueprint.route("/invoke", methods=["POST"])
@auth_required("Invoke", "Lambda Task")
def invoke_data_processing_task():
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
