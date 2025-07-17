# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Disable linter warnings for print statements (quick fix for logging issues with alembic)
# ruff: noqa: T201

import json
from typing import Any

import boto3


class SecretManager:
    """AWS Secrets Manager implementation."""

    def __init__(self, client=None):
        """
        Initialize the AWS Secret Manager.

        Args:
            client: Boto3 secrets manager client instance.
        """
        self.client = client or boto3.client("secretsmanager")

    def get_secret(self, secret_arn: str) -> dict[str, Any]:
        """
        Retrieve a secret from AWS Secrets Manager.

        Args:
            secret_arn: The ARN of the secret to retrieve.

        Returns
        -------
            The secret as a dictionary.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_arn)
            return json.loads(response["SecretString"])
        except Exception as e:
            print(f"Error getting secret: {e}")
            raise
