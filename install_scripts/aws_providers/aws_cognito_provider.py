import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import AwsProviderError

class AwsCognitoProvider:
    def __init__(self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.cognito_client = aws_client_provider.cognito_client

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
            raise

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
            raise
