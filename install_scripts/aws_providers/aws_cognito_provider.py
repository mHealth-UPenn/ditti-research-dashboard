from install_scripts.utils import Logger
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.aws_providers.aws_client_provider import AWSClientProvider


class AwsCognitoProvider:
    def __init__(self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.cognito_client = aws_client_provider.cognito_client

    def get_participant_client_secret(self) -> str:
        return self.cognito_client.describe_user_pool_client(
            UserPoolId=self.settings.participant_user_pool_id,
            ClientId=self.settings.participant_client_id
        )["UserPoolClient"]["ClientSecret"]

    def get_researcher_client_secret(self) -> str:
        return self.cognito_client.describe_user_pool_client(
            UserPoolId=self.settings.researcher_user_pool_id,
            ClientId=self.settings.researcher_client_id
        )["UserPoolClient"]["ClientSecret"]
