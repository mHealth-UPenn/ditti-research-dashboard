import traceback

from boto3.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AWSClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import AwsProviderError

class AwsCognitoProvider:
    # Unit test: self.cognito_client is initialized with expected arguments
    def __init__(self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.cognito_client = aws_client_provider.cognito_client

    # Unit test: self.cognito_client.describe_user_pool_client is called with expected arguments
    # Unit test: self.cognito_client.describe_user_pool_client returns mocked value
    # Unit test: ClientError is raised when user pool client is not found
    # Unit test: self.logger.red is called once on ClientError
    def get_participant_client_secret(self) -> str:
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.settings.participant_user_pool_id,
                ClientId=self.settings.participant_client_id
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"Error getting participant client secret due to ClientError: {e}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error getting participant client secret due to unexpected error: {e}")
            raise AwsProviderError(e)

    # Unit test: self.cognito_client.describe_user_pool_client is called with expected arguments
    # Unit test: self.cognito_client.describe_user_pool_client returns mocked value
    # Unit test: ClientError is raised when user pool client is not found
    # Unit test: self.logger.red is called once on ClientError
    def get_researcher_client_secret(self) -> str:
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.settings.researcher_user_pool_id,
                ClientId=self.settings.researcher_client_id
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"Error getting researcher client secret due to ClientError: {e}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error getting researcher client secret due to unexpected error: {e}")
            raise AwsProviderError(e)
