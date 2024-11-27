from datetime import datetime, UTC
import logging
import traceback
from flask import Blueprint, jsonify, make_response, request
from aws_portal.extensions import db
from aws_portal.models import LambdaTask
from aws_portal.utils.lambda_task import invoke_lambda_task
from aws_portal.utils.sigv4_auth import sigv4_required

blueprint = Blueprint("lambda_task", __name__, url_prefix="/lambda_task")
logger = logging.getLogger(__name__)


@blueprint.route("/", methods=["GET"])
# TODO: Add correct authentication decorator
def get_lambda_tasks():
    """
    Retrieve all Lambda tasks sorted by creation date.

    Request:
    --------
    GET /lambda_task/

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


@blueprint.route("/trigger", methods=["POST"])
# TODO: Add correct authentication decorator
# TODO: Will be called when someone opens the app and after the database starts running
def trigger_lambda_task():
    """
    Manually trigger a Lambda task.

    Request:
    --------
    POST /lambda_task/trigger

    Response (200 OK):
    ------------------
    {
        "msg": "Lambda task triggered successfully",
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
        "msg": "Internal server error when triggering lambda task."
    }
    """
    try:
        # Create a new LambdaTask with status 'Pending'
        lambda_task = LambdaTask(
            status="Pending",
            created_on=datetime.now(UTC),
            updated_on=datetime.now(UTC)
        )
        db.session.add(lambda_task)
        db.session.commit()

        # Invoke the Lambda function with the function_id
        invoke_lambda_task(function_id=lambda_task.id)

        return jsonify({
            "msg": "Lambda task triggered successfully",
            "task": lambda_task.meta
        }), 200

    except Exception:
        exc = traceback.format_exc()
        logger.warning(f"Error triggering Lambda task: {exc}")
        db.session.rollback()
        return make_response({"msg": "Internal server error when triggering lambda task."}, 500)
