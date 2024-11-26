import boto3
import logging
import json
from aws_portal.extensions import db
from aws_portal.models import LambdaTask
from datetime import datetime, UTC
import traceback
from flask import current_app

logger = logging.getLogger(__name__)


def invoke_lambda_task(function_id):
    """
    Invokes an AWS Lambda function asynchronously and stores the task in the database.

    Args:
        function_id: The database ID of the LambdaTask to update.

    Returns:
        LambdaTask: The LambdaTask object stored in the database.
    """
    try:
        session = boto3.Session(
            aws_access_key_id=current_app.config["LAMBDA_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["LAMBDA_SECRET_ACCESS_KEY"],
            region_name=current_app.config["LAMBDA_AWS_REGION"]
        )
        client = session.client("lambda")

        # Retrieve the Lambda function name from configuration
        function_name = current_app.config.get("LAMBDA_FUNCTION_NAME")
        if not function_name:
            raise ValueError("LAMBDA_FUNCTION_NAME is not configured.")

        # Payload contains only the function_id
        payload = {
            "function_id": function_id
        }

        response = client.invoke(
            FunctionName=function_name,
            InvocationType="Event",  # Asynchronous invocation
            Payload=json.dumps(payload)
        )

        logger.info(
            f"Lambda invoked with function_id {function_id}. "
            f"Response: {response}"
        )

        return LambdaTask.query.get(function_id)

    except Exception as e:
        logger.error(f"Failed to invoke lambda function: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)
        # Update the LambdaTask status to 'Failed'
        lambda_task = LambdaTask.query.get(function_id)
        if lambda_task:
            lambda_task.status = "Failed"
            lambda_task.error_message = str(e)
            lambda_task.updated_on = datetime.now(UTC)
            db.session.commit()
        return lambda_task


def schedule_lambda_task():
    """
    Scheduled task to invoke the lambda function.
    """
    try:
        logger.info("Scheduling Lambda task to retrieve and store sleep data.")
        # Create a new LambdaTask with status 'Pending'
        lambda_task = LambdaTask(
            status="Pending",
            created_on=datetime.now(UTC),
            updated_on=datetime.now(UTC)
        )
        db.session.add(lambda_task)
        db.session.commit()

        # Pass the function_id to the Lambda function
        invoke_lambda_task(function_id=lambda_task.id)
    except Exception as e:
        logger.error(f"Error in scheduled Lambda task: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)


def update_lambda_task_status(task_id, status, error_message=None):
    """
    Updates the status of a LambdaTask.

    Args:
        task_id (int): The ID of the task to update.
        status (str): The new status ("Success" or "Failed").
        error_message (str, optional): The error message if status is "Failed".
    """
    try:
        lambda_task = LambdaTask.query.filter_by(id=task_id).first()
        if not lambda_task:
            logger.warning(f"LambdaTask with id {task_id} not found.")
            return

        lambda_task.status = status
        lambda_task.error_message = error_message
        lambda_task.updated_on = datetime.now(UTC)
        db.session.commit()
        logger.info(f"Updated LambdaTask {task_id} status to {status}.")
    except Exception as e:
        logger.error(f"Failed to update LambdaTask {task_id}: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)
        db.session.rollback()
