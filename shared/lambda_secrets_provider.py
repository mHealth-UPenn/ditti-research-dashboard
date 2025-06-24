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
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import boto3
import requests
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


T = TypeVar("T")


@dataclass
class SecretPayload(Generic[T]):
    """Represents the data retrieved for a secret from AWS Secrets Manager."""

    version_id: str
    secret_string: str | None = None
    secret_dict: T | None = None
    version_stages: list[str] = field(default_factory=list)
    name: str | None = None
    arn: str | None = None


def _parse_response_to_payload(response_body: dict[str, Any]) -> SecretPayload:
    """
    Parse the full response from AWS Secrets Manager into a SecretPayload.

    Parameters
    ----------
    response_body : dict[str, Any]
        The raw response from AWS Secrets Manager.

    Returns
    -------
    SecretPayload
        The parsed secret payload with metadata.
    """
    secret_string = ""
    if "SecretString" in response_body:
        secret_string = response_body["SecretString"]
    elif "SecretBinary" in response_body:
        secret_string = response_body["SecretBinary"].decode("utf-8")
    else:
        raise ValueError(
            "Secret response must contain 'SecretString' or 'SecretBinary'."
        )

    secret_dict: dict[str, Any] | None = None
    try:
        secret_dict = json.loads(secret_string)
    except json.JSONDecodeError:
        logger.debug("Secret is not a JSON object, treating as a raw string.")
        secret_dict = None

    return SecretPayload(
        secret_dict=secret_dict,
        secret_string=secret_string,
        version_id=response_body["VersionId"],
        version_stages=response_body.get("VersionStages", []),
        name=response_body.get("Name"),
        arn=response_body.get("ARN"),
    )


def get_secret(
    secret_name: str,
    version_id: str | None = None,
    version_stage: str | None = None,
) -> SecretPayload:
    """
    Retrieve a secret from AWS Secrets Manager, using the Lambda extension if available.

    This function first attempts to retrieve the secret from the AWS Parameters
    and Secrets Lambda Extension, which is the preferred method for performance
    and cost savings in a Lambda environment. If the extension is not available
    (e.g., when running in a local development environment), it falls back to
    using the standard boto3 AWS SDK.

    Parameters
    ----------
    secret_name : str
        The name or ARN of the secret to retrieve from AWS Secrets Manager.
    version_id : str, optional
        The unique identifier of the version of the secret to retrieve.
    version_stage : str, optional
        The staging label of the version of the secret to retrieve.

    Returns
    -------
    SecretPayload
        An object containing the parsed secret dictionary and its metadata.

    Raises
    ------
    requests.exceptions.RequestException
        If there is a network-related error when calling the Lambda extension.
    ValueError
        If the secret payload is malformed.
    ClientError
        If the boto3 fallback fails to retrieve the secret.
    Exception
        For any other unexpected errors during the process.
    """
    # Check if running in a Lambda environment where the extension is expected to be present.
    if (
        "AWS_SESSION_TOKEN" in os.environ
        and "AWS_LAMBDA_RUNTIME_API" in os.environ
    ):
        params = {"secretId": secret_name}
        if version_id:
            params["versionId"] = version_id
        if version_stage:
            params["versionStage"] = version_stage

        session_token = os.environ["AWS_SESSION_TOKEN"]
        endpoint = "http://localhost:2773/secretsmanager/get"
        headers = {"X-Aws-Parameters-Secrets-Token": session_token}

        try:
            logger.info(
                "Attempting to retrieve secret '%s' from Lambda extension.",
                secret_name,
            )
            response = requests.get(
                endpoint, headers=headers, params=params, timeout=5
            )
            response.raise_for_status()
            secret_payload_json = response.json()

            logger.info(
                "Successfully retrieved secret '%s' from Lambda extension.",
                secret_name,
            )
            return _parse_response_to_payload(secret_payload_json)

        except (
            requests.exceptions.RequestException,
            ValueError,
            json.JSONDecodeError,
        ) as e:
            logger.warning(
                "Failed to retrieve secret from Lambda extension: %s. "
                "Falling back to boto3.",
                e,
            )

    # Fallback to boto3 if not in Lambda or if the extension fails
    logger.info("Attempting to retrieve secret '%s' using boto3.", secret_name)
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name="secretsmanager",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        boto_params = {"SecretId": secret_name}
        if version_id:
            boto_params["VersionId"] = version_id
        if version_stage:
            boto_params["VersionStage"] = version_stage

        response = client.get_secret_value(**boto_params)
        return _parse_response_to_payload(response)

    except ClientError as e:
        logger.error(
            "Error retrieving secret '%s' with boto3: %s", secret_name, e
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error retrieving secret '%s' with boto3: %s",
            secret_name,
            e,
        )
        raise


class SecretProvider(Generic[T]):
    """
    Generic provider for retrieving and parsing AWS Secrets Manager secrets.

    This class wraps `get_secret` and enables type-safe access to secret payloads.

    Example
    -------
    >>> from typing import TypedDict
    >>> class MySecretSchema(TypedDict):
    ...     username: str
    ...     password: str
    >>> provider = SecretProvider[MySecretSchema]("my-secret-name")
    >>> payload = provider.get_secret()
    >>> user = payload.secret_dict["username"]  # type-checked
    """

    def __init__(
        self,
        secret_name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
    ) -> None:
        self._secret_name = secret_name
        self._version_id = version_id
        self._version_stage = version_stage

    def get_secret(self) -> "SecretPayload[T]":
        """
        Retrieve and parse the secret, preserving the type parameter `T`.

        Returns
        -------
        SecretPayload[T]
            The parsed secret payload with the correct type for `secret_dict`.
        """
        return get_secret(
            self._secret_name,
            version_id=self._version_id,
            version_stage=self._version_stage,
        )  # type: ignore[return-value]
