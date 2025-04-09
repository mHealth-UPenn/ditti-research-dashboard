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

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, UTC
import json
import logging
import traceback

import boto3
from flask import current_app
import requests
from sqlalchemy import or_

from aws_portal.extensions import db
from aws_portal.models import LambdaTask


logger = logging.getLogger(__name__)


def create_and_invoke_lambda_task():
    """
    Creates a new LambdaTask and invokes the Lambda function.
    """
    try:
        now = datetime.now(UTC)
        # Create a new LambdaTask with status "Pending"
        lambda_task = LambdaTask(
            status="Pending",
            created_on=now,
            updated_on=now
        )
        db.session.add(lambda_task)
        db.session.commit()

        # Invoke the Lambda function with the function_id
        invoke_lambda_task(function_id=lambda_task.id)

        return lambda_task
    except Exception as e:
        logger.error(f"Error creating and invoking Lambda task: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)
        db.session.rollback()
        return None


def check_and_invoke_lambda_task():
    """
    Checks if a LambdaTask has been run today. If not, invokes a new Lambda task.
    """
    try:
        # Get the latest completed or in progress lambda function
        latest_task = LambdaTask.query\
            .filter(
                or_(
                    LambdaTask.status == "InProgress",
                    LambdaTask.status == "Success",
                    LambdaTask.status == "CompletedWithErrors"
                )
            )\
            .order_by(
                LambdaTask.created_on.desc()
            ).first()
        now = datetime.now(UTC)
        # TODO: Update with finalized retrieval schedule
        if latest_task:
            # Check if the latest task was run today
            if latest_task.created_on.date() == now.date():
                # A task has already been run today
                logger.info("Lambda task has already been run today.")
                return latest_task
            else:
                logger.info(
                    "No Lambda task has been run today. Invoking new Lambda task.")
                # Create and invoke a new LambdaTask
                lambda_task = create_and_invoke_lambda_task()
                return lambda_task
        else:
            # No task has been run yet
            logger.info("No Lambda task found. Invoking first Lambda task.")
            # Create and invoke a new LambdaTask
            lambda_task = create_and_invoke_lambda_task()
            return lambda_task
    except Exception as e:
        logger.error(f"Error checking/invoking Lambda task: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)
        db.session.rollback()
        return None


def invoke_lambda_task(function_id):
    """
    Invokes an AWS Lambda function asynchronously and stores the task in the database.

    Args:
        function_id: The database ID of the LambdaTask to update.

    Returns:
        LambdaTask: The LambdaTask object stored in the database.
    """
    try:
        if current_app.config["ENV"] in {"staging", "production", "testing"}:
            client = boto3.client("lambda")

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
                Payload=json.dumps(payload).encode(
                    'utf-8')  # Ensure payload is bytes
            )

            logger.info(
                f"Lambda invoked with function_id {function_id}. "
                f"Response: {response}"
            )

        else:
            # In development and testing environments send an async invocation to the local lambda endpoint
            def send_request(url, data):
                try:
                    requests.post(url, json=data)
                except requests.RequestException as e:
                    logger.error(f"Lambda invocation failed: {e}")

            url = current_app.config["LOCAL_LAMBDA_ENDPOINT"]
            data = {"function_id": function_id}
            executor = ThreadPoolExecutor()
            executor.submit(send_request, url, data)

        # Update the task status to 'InProgress'
        lambda_task = LambdaTask.query.get(function_id)
        if lambda_task:
            lambda_task.status = "InProgress"
            lambda_task.updated_on = datetime.now(UTC)
            db.session.commit()

        return lambda_task

    except Exception as e:
        logger.error(f"Failed to invoke lambda function: {e}")
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)
        # Update the LambdaTask status to 'Failed' and set error_code
        lambda_task = LambdaTask.query.get(function_id)
        if lambda_task:
            lambda_task.status = "Failed"
            lambda_task.error_code = str(e)
            lambda_task.updated_on = datetime.now(UTC)
            db.session.commit()
        return lambda_task


# def schedule_lambda_task():
#     """
#     Scheduled task to invoke the lambda function.
#     """
#     try:
#         logger.info("Scheduling Lambda task to retrieve and store sleep data.")
#         # Create a new LambdaTask with status 'Pending'
#         lambda_task = LambdaTask(
#             status="Pending",
#             created_on=datetime.now(UTC),
#             updated_on=datetime.now(UTC)
#         )
#         db.session.add(lambda_task)
#         db.session.commit()

#         # Pass the function_id to the Lambda function
#         invoke_lambda_task(function_id=lambda_task.id)
#     except Exception as e:
#         logger.error(f"Error in scheduled Lambda task: {e}")
#         traceback_str = traceback.format_exc()
#         logger.error(traceback_str)
