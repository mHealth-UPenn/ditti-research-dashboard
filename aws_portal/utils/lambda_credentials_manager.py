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

import boto3
import logging
import json
from botocore.exceptions import ClientError
from botocore.credentials import Credentials

logger = logging.getLogger(__name__)


class LambdaCredentialsManager:
    """
    Manages AWS credentials for the Lambda execution user using AWS Secrets Manager.
    Retrieves shared Lambda credentials for SigV4 authentication.
    """

    def __init__(self, secret_name: str, region_name: str = "us-east-1"):
        """
        Initializes the Secrets Manager client and sets the secret name and region.

        Args:
            secret_name (str): The name of the secret to retrieve.
            region_name (str): AWS region where the secret is stored.
        """
        self.secret_name = secret_name
        self.region_name = region_name
        self.client = boto3.client(
            "secretsmanager", region_name=self.region_name)
        self.credentials = None  # Cache credentials after retrieval

    def get_credentials(self) -> Credentials:
        """
        Retrieves AWS credentials from Secrets Manager.
        Caches credentials after the first retrieval.

        Returns:
            Credentials: botocore.credentials.Credentials object containing access key and secret key.

        Raises:
            Exception: If unable to retrieve or parse the secret.
        """
        if self.credentials:
            logger.debug("Using cached Lambda credentials.")
            return self.credentials

        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secret_string = response.get("SecretString")
            if not secret_string:
                logger.error(
                    f"Secret '{self.secret_name}' does not contain 'SecretString'.")
                raise ValueError(
                    f"Secret '{self.secret_name}' does not contain 'SecretString'.")
            secret_data = json.loads(secret_string)
            access_key = secret_data.get("LAMBDA_ACCESS_KEY_ID")
            secret_key = secret_data.get("LAMBDA_SECRET_ACCESS_KEY")
            region = secret_data.get("LAMBDA_AWS_REGION", self.region_name)

            if not access_key or not secret_key:
                logger.error(
                    "Access Key ID or Secret Access Key missing in the secret.")
                raise ValueError(
                    "Access Key ID or Secret Access Key missing in the secret.")

            self.credentials = Credentials(access_key, secret_key)
            logger.info(
                "Successfully retrieved and cached Lambda execution credentials from Secrets Manager.")
            return self.credentials

        except ClientError as e:
            logger.error(f"Error retrieving secret '{self.secret_name}': {e}")
            raise e
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from secret '{
                         self.secret_name}': {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error retrieving credentials: {e}")
            raise e
