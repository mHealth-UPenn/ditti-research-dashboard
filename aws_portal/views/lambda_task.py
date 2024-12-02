import logging
import traceback
from flask import Blueprint, jsonify, make_response
from aws_portal.extensions import db
from aws_portal.models import LambdaTask
from aws_portal.utils.auth import auth_required
from aws_portal.utils.lambda_task import create_and_invoke_lambda_task

blueprint = Blueprint("lambda_task", __name__, url_prefix="/lambda_task")
logger = logging.getLogger(__name__)


@blueprint.route("/", methods=["GET"])
@auth_required("View", "Admin Dashboard")
@auth_required("View", "Lambda Task")
def get_lambda_tasks():
    """
    Retrieve all Lambda tasks sorted by creation date.

    Request:
    --------
    GET /lambda_task/

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
        "msg": "Internal server error when retrieving lambda tasks."
    }
    """
    try:
        # Retrieve all tasks sorted by created_on in descending order (most recent first)
        tasks = LambdaTask.query.order_by(LambdaTask.created_on.desc()).all()
        res = [task.meta for task in tasks]
        return jsonify(res), 200

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(f"Error retrieving Lambda tasks: {exc}")
        db.session.rollback()
        return make_response({"msg": "Internal server error when retrieving lambda tasks."}, 500)


@blueprint.route("/invoke", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Invoke", "Lambda Task")
def invoke_lambda_task():
    """
    Manually invoke a Lambda task.

    Request:
    --------
    POST /lambda_task/invoke

    Body (JSON):
    ------------
    {
        "app": 1,                   # Required
    }

    Response (200 OK):
    ------------------
    {
        "msg": "Lambda task invoked successfully",
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
        "msg": "Internal server error when invoking lambda task."
    }
    """
    try:
        # Create and invoke a new LambdaTask
        lambda_task = create_and_invoke_lambda_task()
        if lambda_task is None:
            raise Exception("Failed to create and invoke Lambda task.")

        return jsonify({
            "msg": "Lambda task invoked successfully",
            "task": lambda_task.meta
        }), 200

    except Exception:
        exc = traceback.format_exc()
        logger.warning(f"Error invoking Lambda task: {exc}")
        db.session.rollback()
        return make_response({"msg": "Internal server error when invoking lambda task."}, 500)
