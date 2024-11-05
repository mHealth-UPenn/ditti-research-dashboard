import boto3
import logging
import json
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Manages secrets using AWS Secrets Manager.
    """

    def __init__(self):
        """
        Initializes the AWS Secrets Manager client.
        """
        self.client = boto3.client("secretsmanager")

    def store_secret(self, secret_uuid, secret_value):
        """
        Stores a secret in AWS Secrets Manager.

        Args:
            secret_uuid (str): The unique identifier for the secret.
            secret_value (str or dict): The secret value to store. If a dictionary is provided, it will be stored as a JSON string.

        Raises:
            ClientError: If an error occurs while storing the secret.
        """
        if isinstance(secret_value, dict):
            secret_string = json.dumps(secret_value)
        else:
            secret_string = secret_value

        try:
            # Attempt to update the existing secret
            self.client.put_secret_value(
                SecretId=secret_uuid,
                SecretString=secret_string
            )
            logger.info(f"Updated secret for UUID: {secret_uuid}")
        except self.client.exceptions.ResourceNotFoundException:
            # Secret does not exist; create a new one
            self.client.create_secret(
                Name=secret_uuid,
                SecretString=secret_string
            )
            logger.info(f"Created secret for UUID: {secret_uuid}")
        except ClientError as e:
            logger.error(f"Error storing secret: {e}")
            raise

    def get_secret(self, secret_uuid):
        """
        Retrieves a secret from AWS Secrets Manager.

        Args:
            secret_uuid (str): The unique identifier for the secret.

        Returns:
            str or dict: The retrieved secret. Returns a dictionary if the secret is JSON-formatted, otherwise returns a string.

        Raises:
            ClientError: If an error occurs while retrieving the secret.
            KeyError: If the secret does not exist.
        """
        try:
            response = self.client.get_secret_value(
                SecretId=secret_uuid
            )
            secret_string = response.get("SecretString")
            if secret_string is None:
                logger.error(f"SecretString not found for UUID: {secret_uuid}")
                raise KeyError(f"Secret with UUID {
                               secret_uuid} does not contain a SecretString.")
            logger.info(f"Retrieved secret from AWS for UUID: {secret_uuid}")
        except self.client.exceptions.ResourceNotFoundException:
            logger.error(f"Secret not found for UUID: {secret_uuid}")
            raise KeyError(f"Secret with UUID {secret_uuid} not found.")
        except ClientError as e:
            logger.error(f"Error retrieving secret: {e}")
            raise

        try:
            secret_value = json.loads(secret_string)
        except json.JSONDecodeError:
            secret_value = secret_string

        return secret_value
