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

    def __init__(self):
        """
        Initializes the AWS Secrets Manager client.
        """
        self.client = boto3.client("secretsmanager")

    def _get_secret_name(self, api_name: str) -> str:
        """
        Constructs the secret name based on the API name.

        Args:
            api_name (str): The name of the API.

        Returns:
            str: The constructed secret name.
        """
        return f"{api_name}-tokens"

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

    def add_or_update_api_token(self, api_name: str, study_subject_id: int, tokens: Dict[str, Any]) -> None:
        """
        Adds or updates the tokens for a specific study subject within an API's secret.

        Args:
            api_name (str): The name of the API.
            study_subject_id (int): The ID of the study subject.
            tokens (Dict[str, Any]): A dictionary containing token information.

        Raises:
            Exception: If there is an error during the process.
        """
        secret_name = self._get_secret_name(api_name)
        try:
            secret_data = self._retrieve_secret(secret_name)
            secret_data[str(study_subject_id)] = tokens
            self._store_secret(secret_name, secret_data)
            logger.info(
                f"Added/Updated tokens for Study Subject ID {study_subject_id} in API '{api_name}'.")
        except Exception as e:
            logger.error(f"Failed to add/update tokens for Study Subject ID {
                         study_subject_id} in API '{api_name}': {e}")
            raise

    def get_api_tokens(self, api_name: str, study_subject_id: int) -> Dict[str, Any]:
        """
        Retrieves the tokens for a specific study subject within an API's secret.

        Args:
            api_name (str): The name of the API.
            study_subject_id (int): The ID of the study subject.

        Returns:
            Dict[str, Any]: The tokens for the study subject.

        Raises:
            KeyError: If the secret or the study subject's tokens are not found.
            Exception: If there is an error during the process.
        """
        secret_name = self._get_secret_name(api_name)
        try:
            secret_data = self._retrieve_secret(secret_name)
            tokens = secret_data.get(str(study_subject_id))
            if not tokens:
                logger.error(f"Tokens for Study Subject ID {
                             study_subject_id} not found in API '{api_name}'.")
                raise KeyError(f"Tokens for Study Subject ID {
                               study_subject_id} not found in API '{api_name}'.")
            return tokens
        except KeyError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve tokens for Study Subject ID {
                         study_subject_id} in API '{api_name}': {e}")
            raise

    def delete_api_tokens(self, api_name: str, study_subject_id: int) -> None:
        """
        Deletes the tokens for a specific study subject within an API's secret.

        Args:
            api_name (str): The name of the API.
            study_subject_id (int): The ID of the study subject.

        Raises:
            KeyError: If the secret or the study subject's tokens are not found.
            Exception: If there is an error during the process.
        """
        secret_name = self._get_secret_name(api_name)
        try:
            secret_data = self._retrieve_secret(secret_name)
            if str(study_subject_id) not in secret_data:
                logger.error(f"Tokens for Study Subject ID {
                             study_subject_id} not found in API '{api_name}'.")
                raise KeyError(f"Tokens for Study Subject ID {
                               study_subject_id} not found in API '{api_name}'.")
            del secret_data[str(study_subject_id)]
            self._store_secret(secret_name, secret_data)
            logger.info(f"Deleted tokens for Study Subject ID {
                        study_subject_id} from API '{api_name}'.")
        except KeyError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Failed to delete tokens for Study Subject ID {
                         study_subject_id} in API '{api_name}': {e}")
            raise
