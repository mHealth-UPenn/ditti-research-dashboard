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
import os
import time

import boto3
import requests
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _context):
    """Secrets Manager Rotation Template for FLASK_SECRET_KEY."""
    if "SecretId" not in event:
        logger.info("Invocation event does not contain a SecretId. Exiting.")
        return

    arn = event["SecretId"]
    token = event["ClientRequestToken"]
    step = event["Step"]

    # Setup the client
    service_client = boto3.client("secretsmanager")

    # Make sure the version is staged correctly
    metadata = service_client.describe_secret(SecretId=arn)
    if not metadata["RotationEnabled"]:
        logger.error(f"Secret {arn} is not enabled for rotation")
        raise ValueError(f"Secret {arn} is not enabled for rotation")
    versions = metadata["VersionIdsToStages"]
    if token not in versions:
        logger.error(
            f"Secret version {token} has no stage for rotation of secret {arn}."
        )
        raise ValueError(
            f"Secret version {token} has no stage for rotation of secret {arn}."
        )
    if "AWSCURRENT" in versions[token]:
        logger.info(
            f"Secret version {token} already set as AWSCURRENT for secret {arn}."
        )
        return
    elif "AWSPENDING" not in versions[token]:
        logger.error(
            f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}."
        )
        raise ValueError(
            f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}."
        )

    if step == "createSecret":
        create_secret(service_client, arn, token)

    elif step == "setSecret":
        set_secret()

    elif step == "testSecret":
        test_secret(token)

    elif step == "finishSecret":
        finish_secret(service_client, arn, token)

    else:
        raise ValueError("Invalid step parameter")


def create_secret(service_client, arn, token):
    """Create the secret.

    This method generates a new secret and puts it with the passed in token.
    """
    # Make sure the current secret exists
    service_client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")

    # Now try to get the secret version, if that fails, put a new secret
    try:
        service_client.get_secret_value(
            SecretId=arn, VersionId=token, VersionStage="AWSPENDING"
        )
        logger.info(f"createSecret: Successfully retrieved secret for {arn}.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            # Get exclude characters from environment variable.
            # The Flask secret key can be any string, but for simplicity, we avoid
            # chars that might cause issues in shells or URLs.
            exclude_characters = os.environ.get("EXCLUDE_CHARACTERS", "/@\"'\\")
            # Generate a random password - 32 characters is a good length
            passwd = service_client.get_random_password(
                PasswordLength=32, ExcludeCharacters=exclude_characters
            )

            # Put the secret
            service_client.put_secret_value(
                SecretId=arn,
                ClientRequestToken=token,
                SecretString=passwd["RandomPassword"],
                VersionStages=["AWSPENDING"],
            )
            logger.info(
                f"createSecret: Successfully put secret for ARN {arn} and version {token}."
            )
        else:
            raise


def set_secret():
    """Set the secret.

    This method triggers an update of the app's Lambda function to force
    a restart, so it picks up the new secret. It also sets an environment
    variable to instruct the app to use the 'AWSPENDING' version of the
    secret for testing.
    """
    app_lambda_name = os.environ.get("APP_LAMBDA_FUNCTION_NAME")
    if not app_lambda_name:
        logger.error("Environment variable APP_LAMBDA_FUNCTION_NAME not set.")
        raise ValueError("APP_LAMBDA_FUNCTION_NAME not set.")

    lambda_client = boto3.client("lambda")

    try:
        # Get current environment variables
        config = lambda_client.get_function_configuration(
            FunctionName=app_lambda_name
        )
        env_vars = config.get("Environment", {}).get("Variables", {})

        # Update a dummy env var to trigger redeployment and tell the app to use
        # the pending secret for testing.
        env_vars["LAST_SECRET_ROTATION_TIMESTAMP"] = str(time.time())
        env_vars["SECRET_VERSION_STAGE"] = "AWSPENDING"  # noqa: S105

        # Update lambda configuration
        lambda_client.update_function_configuration(
            FunctionName=app_lambda_name, Environment={"Variables": env_vars}
        )
        logger.info(
            "Successfully triggered update for Lambda function: %s",
            app_lambda_name,
        )

    except Exception as e:
        logger.error(
            "Failed to trigger update for Lambda function %s: %s",
            app_lambda_name,
            e,
        )
        raise e


def _wait_for_lambda_ready(
    lambda_client: "boto3.client",
    function_name: str,
    *,
    timeout: int = 60,
    poll_interval: int = 2,
) -> None:
    """Block until the specified Lambda function is Active and fully updated.

    Parameters
    ----------
    lambda_client:
        A boto3 Lambda client.
    function_name:
        The name or ARN of the Lambda function to check.
    timeout:
        Maximum seconds to wait before giving up.
    poll_interval:
        Delay between successive *get_function* calls.

    Raises
    ------
    RuntimeError
        If the function enters a *Failed* state or the last update failed.
    TimeoutError
        If the function does not become ready within *timeout* seconds.
    """
    waited = 0
    while waited < timeout:
        try:
            resp = lambda_client.get_function(FunctionName=function_name)
            config = resp["Configuration"]
            state = config.get("State")
            last_update_status = config.get("LastUpdateStatus")

            logger.info(
                "Lambda %s state=%s last_update_status=%s",
                function_name,
                state,
                last_update_status,
            )

            if state == "Failed" or last_update_status == "Failed":
                raise RuntimeError(
                    f"Lambda function {function_name} update failed (state={state}, last_update_status={last_update_status})."
                )

            # Ready when Active and update has finished (Successful or None)
            if state == "Active" and last_update_status != "InProgress":
                return
        except Exception as exc:  # pragma: no cover
            # Swallow transient API errors but log them for visibility
            logger.warning("Error checking Lambda state: %s", exc)

        time.sleep(poll_interval)
        waited += poll_interval

    raise TimeoutError(
        f"Timed out waiting for Lambda function {function_name} to become Active within {timeout} seconds."
    )


def test_secret(token):
    """Tests the new secret by querying a health check endpoint on the app.

    This function verifies that the application is running and, more importantly,
    that it has loaded the correct (pending) version of the secret key.
    """
    logger.info(
        "Waiting for Lambda function to become active after secret rotation..."
    )
    app_lambda_name = os.environ.get("APP_LAMBDA_FUNCTION_NAME")
    if not app_lambda_name:
        logger.error(
            "Environment variable APP_LAMBDA_FUNCTION_NAME not set. Cannot test secret."
        )
        raise ValueError("APP_LAMBDA_FUNCTION_NAME not set.")

    lambda_client = boto3.client("lambda")

    # Wait until the Lambda update has finished and the function is invocable
    _wait_for_lambda_ready(lambda_client, app_lambda_name)

    app_url = os.environ.get("APP_URL")
    if not app_url:
        logger.error("Environment variable APP_URL not set. Cannot test secret.")
        raise ValueError("APP_URL not set.")

    # Construct the full URL for the health check endpoint
    health_check_url = f"{app_url.rstrip('/')}/health"
    logger.info(
        "Testing new secret by querying health check at %s", health_check_url
    )

    try:
        response = requests.get(health_check_url, timeout=20)
        response.raise_for_status()

        response_data = response.json()
        logger.info("Received health check response: %s", response_data)

        loaded_version = response_data.get("flask_secret_key_version_id")

        # The 'token' is the VersionId of the secret being tested (AWSPENDING)
        if loaded_version == token:
            logger.info(
                "SUCCESS: Application has correctly loaded secret version %s.",
                token,
            )
            return  # Test passed
        else:
            logger.error(
                "FAILURE: Application is using secret version '%s', but expected '%s'.",
                loaded_version,
                token,
            )
            raise ValueError("Application is using the wrong secret version.")

    except (
        requests.exceptions.RequestException,
        ValueError,
        json.JSONDecodeError,
    ) as e:
        logger.error(
            "Failed to connect to application or validate secret version at %s: %s",
            health_check_url,
            e,
        )
        raise e


def finish_secret(service_client, arn, token):
    """Finish the secret.

    This method finalizes the rotation process by marking the secret version
    passed in as the AWSCURRENT secret.
    """
    # First describe the secret to get the current version
    metadata = service_client.describe_secret(SecretId=arn)
    current_version = None
    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                # The correct version is already marked as current, return
                logger.info(
                    f"finishSecret: Version {version} already marked as AWSCURRENT for {arn}"
                )
                return
            current_version = version
            break

    # Finalize by staging the secret version current
    service_client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
    logger.info(
        f"finishSecret: Successfully set AWSCURRENT stage to version {token} for secret {arn}."
    )

    # Clean up the testing environment variable on the application Lambda
    app_lambda_name = os.environ.get("APP_LAMBDA_FUNCTION_NAME")
    if app_lambda_name:
        try:
            lambda_client = boto3.client("lambda")
            config = lambda_client.get_function_configuration(
                FunctionName=app_lambda_name
            )
            env_vars = config.get("Environment", {}).get("Variables", {})

            if "SECRET_VERSION_STAGE" in env_vars:
                del env_vars["SECRET_VERSION_STAGE"]
                lambda_client.update_function_configuration(
                    FunctionName=app_lambda_name,
                    Environment={"Variables": env_vars},
                )
                logger.info(
                    "Successfully cleaned up SECRET_VERSION_STAGE env var from %s",
                    app_lambda_name,
                )
        except Exception as e:
            # Log a warning instead of failing the rotation, as the key is
            # already rotated. The app will just keep using the new key.
            logger.warning(
                "Could not clean up SECRET_VERSION_STAGE on %s: %s",
                app_lambda_name,
                e,
            )
