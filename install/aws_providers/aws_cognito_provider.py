import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import AwsProviderError


class AwsCognitoProvider:
    """
    Provider for AWS Cognito operations.

    Manages Cognito user pools and app clients for authentication
    in the application.
    """

    def __init__(
        self,
        *,
        logger: Logger,
        config: ProjectConfigProvider,
        aws_client_provider: AwsClientProvider,
    ):
        self.logger = logger
        self.config = config
        self.cognito_client = aws_client_provider.cognito_client

    def get_participant_client_secret(self) -> str:
        """
        Get the client secret for the participant app client.

        Retrieves the client secret for the Cognito participant user pool
        app client.

        Returns
        -------
        str
            The participant client secret.

        Raises
        ------
        AwsProviderError
            If there is an error retrieving the client secret.
        """
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.config.participant_user_pool_id,
                ClientId=self.config.participant_client_id,
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting participant client secret due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting participant client secret due to unexpected "
                f"error: {Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e

    def get_researcher_client_secret(self) -> str:
        """
        Get the client secret for the researcher app client.

        Retrieves the client secret for the Cognito researcher user pool
        app client.

        Returns
        -------
        str
            The researcher client secret.

        Raises
        ------
        AwsProviderError
            If there is an error retrieving the client secret.
        """
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.config.researcher_user_pool_id,
                ClientId=self.config.researcher_client_id,
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting researcher client secret due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting researcher client secret due to unexpected "
                f"error: {Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
