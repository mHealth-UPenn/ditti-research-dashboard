import boto3
import logging
import json
from aws_portal.extensions import db
from aws_portal.models import LambdaTask
from datetime import datetime, UTC
import traceback
from flask import current_app

logger = logging.getLogger(__name__)


def invoke_lambda_task(function_name=None, payload=None):
    """
    Invokes an AWS Lambda function asynchronously and stores the task in the database.

    Args:
        function_name (str, optional): The name of the lambda function to invoke.
        payload (dict, optional): The payload to send to the lambda function.

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

        if payload is None:
            payload = {}

        if function_name is None:
            function_name = current_app.config.get("LAMBDA_FUNCTION_NAME")

        response = client.invoke(
            FunctionName=function_name,
            InvocationType="Event",  # Asynchronous invocation
            Payload=json.dumps(payload)
        )

        # Get the request ID as a task ID
        task_id = response["ResponseMetadata"]["RequestId"]

        # Store the LambdaTask in the database
        lambda_task = LambdaTask(
            task_id=task_id,
            status="Pending",
            created_on=datetime.now(UTC),
            updated_on=datetime.now(UTC)
        )

        db.session.add(lambda_task)
        db.session.commit()

        return lambda_task

    except Exception as e:
        logger.error(f"Failed to invoke lambda function {function_name}: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)
        # Store the failed task in the database
        lambda_task = LambdaTask(
            task_id="N/A",
            status="Failed",
            created_on=datetime.now(UTC),
            updated_on=datetime.now(UTC),
            error_message=str(e)
        )
        db.session.add(lambda_task)
        db.session.commit()
        return lambda_task


def schedule_lambda_task():
    """
    Scheduled task to invoke the lambda function.
    """
    try:
        logger.info("Scheduling Lambda task to retrieve and store sleep data.")
        payload = {
            "action": "retrieve_and_store_sleep_data",
            # Add any additional data needed by the Lambda function
        }
        invoke_lambda_task(payload=payload)
    except Exception as e:
        logger.error(f"Error in scheduled Lambda task: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)


def update_lambda_task_status(task_id, status, error_message=None):
    """
    Updates the status of a LambdaTask.

    Args:
        task_id (str): The ID of the task to update.
        status (str): The new status ("Success" or "Failed").
        error_message (str, optional): The error message if status is "Failed".
    """
    try:
        lambda_task = LambdaTask.query.filter_by(task_id=task_id).first()
        if not lambda_task:
            logger.warning(f"LambdaTask with task_id {task_id} not found.")
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
