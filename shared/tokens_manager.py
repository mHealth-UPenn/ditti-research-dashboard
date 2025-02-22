# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
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
from typing import Any, Dict

logger = logging.getLogger(__name__)


class TokensManager:
    """
    Manages API tokens using AWS Secrets Manager.
    Each API has a single secret storing tokens for all study subjects.
    """
    def __init__(self, /, *, fstr="{api_name}-tokens"):
        """
        Initializes the AWS Secrets Manager client.
        """
        self.fstr = fstr
        self.client = boto3.client("secretsmanager")

    def _get_secret_name(self, api_name: str) -> str:
        """
        Constructs the secret name based on the API name.

        Args:
            api_name (str): The name of the API.

        Returns:
            str: The constructed secret name.
        """
        return self.fstr.format(api_name=api_name)

    def _retrieve_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Retrieves the secret JSON object from AWS Secrets Manager.

        Args:
            secret_name (str): The name of the secret.

        Returns:
            Dict[str, Any]: The secret data as a dictionary.

        Raises:
            ClientError: If there is an error retrieving the secret.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response.get("SecretString")
            if secret_string is None:
                logger.error(
                    f"SecretString not found for secret: {secret_name}")
                raise KeyError(
                    f"Secret '{secret_name}' does not contain a SecretString.")
            secret_data = json.loads(secret_string)
            logger.info(f"Retrieved secret for API: {secret_name}")
            return secret_data
        except self.client.exceptions.ResourceNotFoundException:
            logger.warning(
                f"Secret '{secret_name}' not found. It will be created.")
            return {}
        except ClientError as e:
            logger.error(f"Error retrieving secret '{secret_name}': {e}")
            raise

    def _store_secret(self, secret_name: str, secret_data: Dict[str, Any]) -> None:
        """
        Stores the secret JSON object to AWS Secrets Manager.

        Args:
            secret_name (str): The name of the secret.
            secret_data (Dict[str, Any]): The secret data to store.

        Raises:
            ClientError: If there is an error storing the secret.
        """
        secret_string = json.dumps(secret_data)
        try:
            # Try updating the secret if it exists
            self.client.put_secret_value(
                SecretId=secret_name,
                SecretString=secret_string
            )
            logger.info(f"Updated secret for API: {secret_name}")
        except self.client.exceptions.ResourceNotFoundException:
            # If the secret does not exist, create it
            self.client.create_secret(
                Name=secret_name,
                SecretString=secret_string
            )
            logger.info(f"Created secret for API: {secret_name}")
        except ClientError as e:
            logger.error(f"Error storing secret '{secret_name}': {e}")
            raise

    def add_or_update_api_token(self, api_name: str, ditti_id: str, tokens: Dict[str, Any]) -> None:
        """
        Adds or updates the tokens for a specific study subject within an API's secret.

        Args:
            api_name (str): The name of the API.
            ditti_id (str): The Ditti ID of the study subject.
            tokens (Dict[str, Any]): A dictionary containing token information.

        Raises:
            ValueError: If api_name is invalid.
            Exception: If there is an error during the process.
        """
        if not isinstance(api_name, str) or not api_name.strip():
            raise ValueError("api_name must be a non-empty string.")

        secret_name = self._get_secret_name(api_name)
        try:
            secret_data = self._retrieve_secret(secret_name)

            if ditti_id in secret_data:
                # Merge existing tokens with new tokens
                secret_data[ditti_id].update(tokens)
            else:
                # Add new study subject tokens
                secret_data[ditti_id] = tokens

            self._store_secret(secret_name, secret_data)
            logger.info(
                f"Added/Updated tokens for Study Subject {ditti_id} in API '{api_name}'.")
        except Exception as e:
            logger.error(f"Failed to add/update tokens for Study Subject {ditti_id} in API '{api_name}': {e}")
            raise

    def get_api_tokens(self, api_name: str, ditti_id: str) -> Dict[str, Any]:
        """
        Retrieves the tokens for a specific study subject within an API's secret.

        Args:
            api_name (str): The name of the API.
            ditti_id (int): The ID of the study subject.

        Returns:
            Dict[str, Any]: The tokens for the study subject.

        Raises:
            KeyError: If the secret or the study subject's tokens are not found.
            Exception: If there is an error during the process.
        """
        secret_name = self._get_secret_name(api_name)
        try:
            secret_data = self._retrieve_secret(secret_name)
            tokens = secret_data.get(ditti_id)
            if not tokens:
                logger.error(f"Tokens for Study Subject {ditti_id} not found in API '{api_name}'.")
                raise KeyError(f"Tokens for Study Subject {ditti_id} not found in API '{api_name}'.")
            return tokens
        except KeyError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve tokens for Study Subject {ditti_id} in API '{api_name}': {e}")
            raise

    def delete_api_tokens(self, api_name: str, ditti_id: str) -> None:
        """
        Deletes the tokens for a specific study subject within an API's secret.

        Args:
            api_name (str): The name of the API.
            ditti_id (int): The ID of the study subject.

        Raises:
            KeyError: If the secret or the study subject's tokens are not found.
            Exception: If there is an error during the process.
        """
        secret_name = self._get_secret_name(api_name)
        try:
            secret_data = self._retrieve_secret(secret_name)
            if ditti_id not in secret_data:
                logger.error(f"Tokens for Study Subject {ditti_id} not found in API '{api_name}'.")
                raise KeyError(f"Tokens for Study Subject {ditti_id} not found in API '{api_name}'.")
            del secret_data[ditti_id]
            self._store_secret(secret_name, secret_data)
            logger.info(f"Deleted tokens for Study Subject {ditti_id} from API '{api_name}'.")
        except KeyError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Failed to delete tokens for Study Subject {ditti_id} in API '{api_name}': {e}")
            raise

    def init_app(self, app):
        """
        Configure the Tokens Manager instance with a Flask app's configuration. This sets the default format string to
        that set in the Flask app's config dictionary.

        Args:
            app (Flask): The Flask app.
        """
        self.fstr = app.config["TM_FSTRING"]
