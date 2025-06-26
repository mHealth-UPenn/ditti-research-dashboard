import logging
from typing import TypedDict

from shared.lambda_secrets_provider import SecretProvider

logger = logging.getLogger(__name__)


class DatabaseCredentials(TypedDict):
    username: str
    password: str


class DatabaseCredentialsProvider:
    """
    Provides database credentials for the application.

    This class is responsible for retrieving database credentials from AWS
    Secrets Manager and providing them to the application.

    Args
    ----
    secret_name: str
        The name of the AWS Secrets Manager secret that contains the database
        credentials.
    """

    def __init__(self, secret_name: str):
        self.secret_provider = SecretProvider[DatabaseCredentials](secret_name)

    def get_credentials(self) -> DatabaseCredentials:
        """
        Get the database credentials from AWS Secrets Manager.

        Returns
        -------
        DatabaseCredentials

        Raises
        ------
        Exception
            If there is an error retrieving the database credentials.
        """
        try:
            secret_dict = self.secret_provider.get_secret().secret_dict
            if not secret_dict:
                raise ValueError("No database credentials found.")
            return secret_dict
        except Exception as e:
            logger.error(f"Error retrieving database credentials: {e}")
            raise e

    def get_connection_string(
        self, /, *, host: str, port: int, database: str
    ) -> str:
        """
        Get the database connection string.

        Args
        ----
        host: str
            The host of the database.
        port: int
            The port of the database.
        database: str
            The name of the database.

        Returns
        -------
        str
            The database connection string.
        """
        credentials = self.get_credentials()
        return (
            f"postgresql://{credentials['username']}:{credentials['password']}@"
            f"{host}:{port}/{database}"
        )
