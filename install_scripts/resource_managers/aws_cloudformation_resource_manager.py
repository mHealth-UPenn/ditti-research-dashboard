import traceback
import sys

from botocore.exceptions import ClientError

from install_scripts.aws_providers import AWSClientProvider
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.resource_managers.resource_manager_types import CloudFormationParameter
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.utils import Logger

class AwsCloudformationResourceManager(BaseResourceManager):
    dev_template: str = "cloudformation/dev-environment.yml"
    prod_template: str = "cloudformation/prod-environment.yml"

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cloudformation_client

    def on_start(self) -> None:
        """Run when the script starts."""
        self.logger.cyan("\n[AWS Resource Setup]")

    def on_end(self) -> None:
        """Run when the script ends."""
        pass

    def dev(self) -> None:
        """Run the provider in development mode."""
        self.create_cloudformation_stack(
            template=self.dev_template,
            parameters=self.get_dev_parameters()
        )

    def staging(self) -> None:
        """Run the provider in staging mode."""
        pass

    def prod(self) -> None:
        """Run the provider in production mode."""
        pass

    def get_dev_parameters(self) -> list[CloudFormationParameter]:
        return [
            {
                "ParameterKey": "ParticipantUserPoolName",
                "ParameterValue": self.settings.participant_user_pool_name,
            },
            {
                "ParameterKey": "ParticipantUserPoolDomainName",
                "ParameterValue": self.settings.participant_user_pool_domain,
            },
            {
                "ParameterKey": "ResearcherUserPoolName",
                "ParameterValue": self.settings.researcher_user_pool_name,
            },
            {
                "ParameterKey": "ResearcherUserPoolDomainName",
                "ParameterValue": self.settings.researcher_user_pool_domain,
            },
            {
                "ParameterKey": "LogsBucketName",
                "ParameterValue": self.settings.logs_bucket_name,
            },
            {
                "ParameterKey": "AudioBucketName",
                "ParameterValue": self.settings.audio_bucket_name,
            },
            {
                "ParameterKey": "SecretName",
                "ParameterValue": self.settings.secret_name,
            },
            {
                "ParameterKey": "TokensSecretName",
                "ParameterValue": self.settings.tokens_secret_name,
            },
        ]

    def create_cloudformation_stack(
            self, *,
            template: str,
            parameters: list[CloudFormationParameter],
        ) -> None:
        """Set up AWS resources using CloudFormation."""
        # Read CloudFormation template
        with open(template, "r") as f:
            template_body = f.read()

        # Create CloudFormation stack
        try:
            self.client.create_stack(
                StackName=self.settings.stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=["CAPABILITY_IAM"]
            )

            # Wait for stack creation to complete
            self.logger("Waiting for AWS resources to be created...")
            waiter = self.client.get_waiter("stack_create_complete")
            waiter.wait(StackName=self.settings.stack_name)

        except ClientError:
            traceback.print_exc()
            self.logger.red("AWS resource creation failed")
            sys.exit(1)
