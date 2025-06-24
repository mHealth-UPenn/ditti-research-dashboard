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

import boto3
from botocore.credentials import Credentials
from botocore.exceptions import ClientError

from shared.lambda_secrets_provider import get_secret

logger = logging.getLogger(__name__)


class LambdaCredentialsManager:
    """
    Manage AWS credentials for the Lambda execution user.

    Retrieves shared Lambda credentials for SigV4 authentication
    using AWS Secrets Manager.
    """

    def __init__(self, secret_name: str, region_name: str = "us-east-1"):
        """
        Initialize the Secrets Manager client and sets the secret name and region.

        Parameters
        ----------
            secret_name (str): The name of the secret to retrieve.
            region_name (str): AWS region where the secret is stored.
        """
        self.secret_name = secret_name
        self.region_name = region_name
        self.client = boto3.client("secretsmanager", region_name=self.region_name)
        self.credentials = None  # Cache credentials after retrieval

    def get_credentials(self) -> Credentials:
        """
        Retrieve AWS credentials from Secrets Manager.

        Caches credentials after the first retrieval.

        Returns
        -------
            Credentials: botocore.credentials.Credentials object
                containing access key and secret key.

        Raises
        ------
            Exception: If unable to retrieve or parse the secret.
        """
        if self.credentials:
            logger.debug("Using cached Lambda credentials.")
            return self.credentials

        try:
            secret_data = get_secret(self.secret_name).secret_dict

            if secret_data is None:
                logger.error(
                    "Secret '%s' returned no data (secret_dict is None).",
                    self.secret_name,
                )
                raise ValueError(
                    "Unable to retrieve Lambda credentials; secret is empty."
                )

            access_key = secret_data.get("LAMBDA_ACCESS_KEY_ID")
            secret_key = secret_data.get("LAMBDA_SECRET_ACCESS_KEY")
            secret_data.get("LAMBDA_AWS_REGION", self.region_name)

            if not access_key or not secret_key:
                logger.error(
                    "Access Key ID or Secret Access Key missing in the secret."
                )
                raise ValueError(
                    "Access Key ID or Secret Access Key missing in the secret."
                )

            self.credentials = Credentials(access_key, secret_key)
            logger.info(
                "Successfully retrieved and cached Lambda execution "
                "credentials from Secrets Manager."
            )
            return self.credentials

        except ClientError as e:
            logger.error(f"Error retrieving secret '{self.secret_name}': {e}")
            raise e
        except json.JSONDecodeError as e:
            logger.error(
                f"Error decoding JSON from secret '{self.secret_name}': {e}"
            )
            raise e
        except Exception as e:
            logger.error(f"Unexpected error retrieving credentials: {e}")
            raise e
