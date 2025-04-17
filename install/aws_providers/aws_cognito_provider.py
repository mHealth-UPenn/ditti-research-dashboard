import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import AwsProviderError

class AwsCognitoProvider:
    def __init__(self, *,
            logger: Logger,
            config: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.config = config
        self.cognito_client = aws_client_provider.cognito_client

    def get_participant_client_secret(self) -> str:
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.config.participant_user_pool_id,
                ClientId=self.config.participant_client_id
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error getting participant client secret due to ClientError: {Colorizer.white(e)}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error getting participant client secret due to unexpected error: {Colorizer.white(e)}")
            raise AwsProviderError(e)

    def get_researcher_client_secret(self) -> str:
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.config.researcher_user_pool_id,
                ClientId=self.config.researcher_client_id
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error getting researcher client secret due to ClientError: {Colorizer.white(e)}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error getting researcher client secret due to unexpected error: {Colorizer.white(e)}")
            raise AwsProviderError(e)
