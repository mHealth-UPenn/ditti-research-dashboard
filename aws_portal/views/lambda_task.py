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


def get_lambda_tasks():
    """
    Get all lambda tasks.

    Response syntax (200)
    ---------------------
    [
        {
            ...LambdaTask data
        },
        ...
    ]
    """
    try:
        tasks = LambdaTask.query.order_by(LambdaTask.created_on.desc()).all()
        res = [task.meta for task in tasks]
        return jsonify(res), 200

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when retrieving lambda tasks."}, 500)


@blueprint.route("/trigger", methods=["POST"])
@sigv4_required
def trigger_lambda_task():
    """
    Manually trigger the lambda task.

    Request syntax
    --------------
    {
        "function_id": int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Lambda task triggered successfully",
        task: { ...LambdaTask data }
    }
    """
    try:
        data = request.json or {}
        function_id = data.get("function_id")

        if function_id is None:
            return make_response({"msg": "function_id is required"}, 400)

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
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when triggering lambda task."}, 500)


@blueprint.route("/update_status", methods=["POST"])
@sigv4_required
def update_lambda_task_status_route():
    """
    Endpoint for lambda functions to update the status of the task.

    Request syntax
    --------------
    {
        "task_id": int,
        "status": str,  # 'Success' or 'Failed'
        "error_message": str (optional),
        "billed_ms": int (optional)
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Status updated successfully"
    }
    """
    try:
        data = request.json
        task_id = data.get("task_id")
        status = data.get("status")
        error_message = data.get("error_message", None)
        billed_ms = data.get("billed_ms", None)

        if task_id is None or status is None:
            return make_response({"msg": "task_id and status are required"}, 400)

        if status not in ['Success', 'Failed']:
            return make_response({"msg": "Invalid status. Must be 'Success' or 'Failed'."}, 400)

        lambda_task = LambdaTask.query.filter_by(id=task_id).first()
        if not lambda_task:
            return make_response({"msg": f"LambdaTask with id {task_id} not found"}, 400)

        lambda_task.status = status
        lambda_task.error_message = error_message
        if billed_ms is not None:
            lambda_task.billed_ms = billed_ms
        lambda_task.updated_on = datetime.now(UTC)
        db.session.commit()

        return jsonify({"msg": "Status updated successfully"}), 200

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when updating status."}, 500)
