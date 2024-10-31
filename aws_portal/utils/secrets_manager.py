import boto3
import logging
import json
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class StudySubjectSecretsManager:
    """
    Manages secrets for StudySubjects using AWS Secrets Manager or local storage for testing.
    """

    def __init__(self, testing=False):
        self.testing = testing
        if not self.testing:
            self.client = boto3.client("secretsmanager")
            logger.info("Initialized AWS Secrets Manager client.")
        else:
            self._local_secrets = {}
            logger.info("Initialized local Secrets Manager for testing.")

    def store_secret(self, secret_uuid, secret_value, label):
        """
        Stores a secret. Accepts either a string or a dict (which will be stored as JSON).
        """
        labled_secret_uuid = f"{label}-{secret_uuid}"
        if isinstance(secret_value, dict):
            secret_string = json.dumps(secret_value)
        else:
            secret_string = secret_value

        if self.testing:
            self._local_secrets[labled_secret_uuid] = secret_string
            logger.info(
                f"(Test) Stored secret locally for UUID: {labled_secret_uuid}")
        else:
            try:
                # Attempt to update the secret in AWS Secrets Manager
                self.client.put_secret_value(
                    SecretId=labled_secret_uuid,
                    SecretString=secret_string
                )
                logger.info(f"Updated secret for UUID: {labled_secret_uuid}")
            except self.client.exceptions.ResourceNotFoundException:
                # Secret doesn't exist; create it in AWS Secrets Manager
                self.client.create_secret(
                    Name=labled_secret_uuid,
                    SecretString=secret_string
                )
                logger.info(f"Created secret for UUID: {labled_secret_uuid}")
            except ClientError as e:
                logger.error(f"Error storing secret: {e}")
                raise

    def get_secret(self, secret_uuid):
        """
        Retrieves a secret. Returns either a string or a dict if the secret is JSON-formatted.
        """
        if self.testing:
            secret_string = self._local_secrets.get(secret_uuid)
            if secret_string is None:
                logger.error(
                    f"(Test) Secret not found locally for UUID: {secret_uuid}")
                raise KeyError(f"Secret with UUID {secret_uuid} not found.")
            else:
                logger.info(
                    f"(Test) Retrieved secret locally for UUID: {secret_uuid}")
        else:
            try:
                response = self.client.get_secret_value(
                    SecretId=secret_uuid
                )
                secret_string = response["SecretString"]
                logger.info(
                    f"Retrieved secret from AWS for UUID: {secret_uuid}")
            except ClientError as e:
                logger.error(f"Error retrieving secret: {e}")
                raise

        try:
            secret_value = json.loads(secret_string)
        except json.JSONDecodeError:
            secret_value = secret_string

        return secret_value
