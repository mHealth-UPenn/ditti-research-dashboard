import traceback
import sys

from botocore.exceptions import ClientError

from install_scripts.utils import Logger, BaseProvider
from install_scripts.aws.aws_client_provider import AWSClientProvider
from install_scripts.project_settings_provider import ProjectSettingsProvider


class AwsResourcesProvider(BaseProvider):
    dev_template: str = "cloudformation/dev-environment.yml"
    prod_template: str = "cloudformation/prod-environment.yml"

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cloudformation_client
        self.cognito_client = aws_client_provider.cognito_client
        self.secrets_client = aws_client_provider.secrets_manager_client

    def on_start(self) -> None:
        """Run when the script starts."""
        self.logger.cyan("\n[AWS Resource Setup]")

    def on_end(self) -> None:
        """Run when the script ends."""
        self.create_admin_user()

    def dev(self) -> None:
        """Run the provider in development mode."""
        self.setup_aws_resources(self.dev_template)

    def staging(self) -> None:
        """Run the provider in staging mode."""
        pass

    def prod(self) -> None:
        """Run the provider in production mode."""
        pass

    def setup_aws_resources(self, template: str) -> None:
        """Set up AWS resources using CloudFormation."""
        # Read CloudFormation template
        with open(template, "r") as f:
            template_body = f.read()

        # Create CloudFormation stack
        try:
            response = self.client.create_stack(
                StackName=self.settings.stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        "ParameterKey": "ParticipantUserPoolName",
                        "ParameterValue": \
                            self.settings.participant_user_pool_name
                    },
                    {
                        "ParameterKey": "ParticipantUserPoolDomainName",
                        "ParameterValue": \
                            self.settings.participant_user_pool_domain
                    },
                    {
                        "ParameterKey": "ResearcherUserPoolName",
                        "ParameterValue": \
                            self.settings.researcher_user_pool_name
                    },
                    {
                        "ParameterKey": "ResearcherUserPoolDomainName",
                        "ParameterValue": \
                            self.settings.researcher_user_pool_domain
                    },
                    {
                        "ParameterKey": "LogsBucketName",
                        "ParameterValue": self.settings.logs_bucket_name
                    },
                    {
                        "ParameterKey": "AudioBucketName",
                        "ParameterValue": self.settings.audio_bucket_name
                    },
                    {
                        "ParameterKey": "SecretName",
                        "ParameterValue": self.settings.secret_name
                    },
                    {
                        "ParameterKey": "TokensSecretName",
                        "ParameterValue": self.settings.tokens_secret_name
                    },
                ],
                Capabilities=["CAPABILITY_IAM"]
            )

            # Wait for stack creation to complete
            self.logger("Waiting for AWS resources to be created...")
            waiter = self.client.get_waiter("stack_create_complete")
            waiter.wait(StackName=self.settings.stack_name)

            # Get stack outputs
            response = self.client \
                .describe_stacks(StackName=self.settings.stack_name)
            outputs = {
                output["OutputKey"]: output["OutputValue"]
                for output in response["Stacks"][0]["Outputs"]
            }

            self.settings.participant_user_pool_id = \
                outputs["ParticipantUserPoolId"]
            self.settings.participant_client_id = outputs["ParticipantClientId"]
            self.settings.researcher_user_pool_id = \
                outputs["ResearcherUserPoolId"]
            self.settings.researcher_client_id = outputs["ResearcherClientId"]

            self.logger.green("AWS resources created successfully")

        except ClientError as e:
            traceback.print_exc()
            self.logger.red("AWS resource creation failed")
            sys.exit(1)

    def create_admin_user(self) -> None:
        """Create an admin user in the Cognito user pool."""
        self.cognito_client.admin_create_user(
            UserPoolId=self.settings.participant_user_pool_id,
            Username=self.settings.admin_email,
        )

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
