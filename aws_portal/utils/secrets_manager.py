import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# TODO: Automatically refresh key when necessary before providing it


class SecretsManager:
    # Class-level dictionary to store secrets locally during testing
    _local_secrets = {}

    def __init__(self, testing=False):
        # Don't use AWS Secrets Manager if testing
        self.testing = testing

        if not self.testing:
            # Initialize AWS Secrets Manager client
            self.client = boto3.client("secretsmanager")
            logger.info("Initialized AWS Secrets Manager client.")
        else:
            logger.info("Initialized local Secrets Manager for testing.")

    def store_secret(self, secret_uuid, secret_value):
        if self.testing:
            # Store secret locally in the dictionary
            self._local_secrets[secret_uuid] = secret_value
            logger.info(
                f"(Test) Stored secret locally for UUID: {secret_uuid} as {secret_value}")
        else:
            try:
                # Attempt to update the secret in AWS Secrets Manager
                self.client.put_secret_value(
                    SecretId=secret_uuid,
                    SecretString=secret_value
                )
                logger.info(f"Updated secret for UUID: {
                            secret_uuid} as {secret_value}")
            except self.client.exceptions.ResourceNotFoundException:
                # Secret doesn't exist; create it in AWS Secrets Manager
                self.client.create_secret(
                    Name=secret_uuid,
                    SecretString=secret_value
                )
                logger.info(f"Created secret for UUID: {
                            secret_uuid} as {secret_value}")
            except ClientError as e:
                # Log and re-raise any other client errors
                logger.error(f"Error storing secret: {e}")
                raise

    def get_secret(self, secret_uuid):
        if self.testing:
            # Retrieve secret from the local dictionary
            secret = self._local_secrets.get(secret_uuid)
            if secret is not None:
                logger.info(
                    f"(Test) Retrieved secret locally for UUID: {secret_uuid} as {secret}")
                return secret
            else:
                logger.error(
                    f"(Test) Secret not found locally for UUID: {secret_uuid}")
                raise KeyError(f"Secret with UUID {secret_uuid} not found.")
        else:
            try:
                # Retrieve secret from AWS Secrets Manager
                response = self.client.get_secret_value(
                    SecretId=secret_uuid
                )
                return response["SecretString"]
            except ClientError as e:
                # Log and re-raise any client errors
                logger.error(f"Error retrieving secret: {e}")
                raise


secrets_manager = SecretsManager(testing=True)
