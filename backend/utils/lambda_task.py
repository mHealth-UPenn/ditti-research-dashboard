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

import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import boto3
import requests
from flask import current_app
from sqlalchemy import or_

from backend.extensions import db
from backend.models import LambdaTask

logger = logging.getLogger(__name__)


def create_and_invoke_lambda_task():
    """Create a new LambdaTask and invokes the Lambda function."""
    try:
        now = datetime.now(UTC)
        # Create a new LambdaTask with status "Pending"
        lambda_task = LambdaTask(status="Pending", created_on=now, updated_on=now)
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
    Check if a LambdaTask has been run today.

    If not, invoke a new Lambda task.
    """
    try:
        # Get the latest completed or in progress lambda function
        latest_task = (
            LambdaTask.query.filter(
                or_(
                    LambdaTask.status == "InProgress",
                    LambdaTask.status == "Success",
                    LambdaTask.status == "CompletedWithErrors",
                )
            )
            .order_by(LambdaTask.created_on.desc())
            .first()
        )
        now = datetime.now(UTC)
        if latest_task:
            # Check if the latest task was run today
            if latest_task.created_on.date() == now.date():
                # A task has already been run today
                logger.info("Lambda task has already been run today.")
                return latest_task
            else:
                logger.info(
                    "No Lambda task has been run today. Invoking new Lambda task."
                )
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
    Invoke an AWS Lambda function asynchronously and store the task in the db.

    Parameters
    ----------
        function_id: The database ID of the LambdaTask to update.

    Returns
    -------
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
            payload = {"function_id": function_id}

            response = client.invoke(
                FunctionName=function_name,
                InvocationType="Event",  # Asynchronous invocation
                Payload=json.dumps(payload).encode(
                    "utf-8"
                ),  # Ensure payload is bytes
            )

            logger.info(
                f"Lambda invoked with function_id {function_id}. "
                f"Response: {response}"
            )

        else:
            # In development and testing environments,
            # send an async invocation to the local lambda endpoint
            def send_request(url, data):
                try:
                    requests.post(url, json=data, timeout=30)
                except requests.RequestException as e:
                    logger.error(f"Lambda invocation failed: {e}")

            url = current_app.config["LOCAL_LAMBDA_ENDPOINT"]
            data = {"function_id": function_id}
            executor = ThreadPoolExecutor()
            executor.submit(send_request, url, data)

        # Update the task status to 'InProgress'
        lambda_task = db.session.get(LambdaTask, function_id)
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
        lambda_task = db.session.get(LambdaTask, function_id)
        if lambda_task:
            lambda_task.status = "Failed"
            lambda_task.error_code = str(e)
            lambda_task.updated_on = datetime.now(UTC)
            db.session.commit()
        return lambda_task
