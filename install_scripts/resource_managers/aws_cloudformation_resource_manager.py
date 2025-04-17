import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers import AwsClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.resource_managers.resource_manager_types import CloudFormationParameter
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.utils import Logger, Colorizer
from install_scripts.utils.exceptions import ResourceManagerError, UninstallError


class AwsCloudformationResourceManager(BaseResourceManager):
    dev_template: str = "cloudformation/dev-environment.yml"
    prod_template: str = "cloudformation/prod-environment.yml"

    def __init__(
            self, *,
            logger: Logger,
            config: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.config = config
        self.client = aws_client_provider.cloudformation_client

    def dev(self) -> None:
        """Run the provider in development mode."""
        try:
            self.create_cloudformation_stack(
                template_body=self.get_dev_template_body(),
                parameters=self.get_dev_parameters()
            )
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"AWS resource creation failed due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

    def get_dev_parameters(self) -> list[CloudFormationParameter]:
        return [
            {
                "ParameterKey": "ParticipantUserPoolName",
                "ParameterValue": self.config.participant_user_pool_name,
            },
            {
                "ParameterKey": "ParticipantUserPoolDomainName",
                "ParameterValue": self.config.participant_user_pool_domain,
            },
            {
                "ParameterKey": "ResearcherUserPoolName",
                "ParameterValue": self.config.researcher_user_pool_name,
            },
            {
                "ParameterKey": "ResearcherUserPoolDomainName",
                "ParameterValue": self.config.researcher_user_pool_domain,
            },
            {
                "ParameterKey": "LogsBucketName",
                "ParameterValue": self.config.logs_bucket_name,
            },
            {
                "ParameterKey": "AudioBucketName",
                "ParameterValue": self.config.audio_bucket_name,
            },
            {
                "ParameterKey": "SecretName",
                "ParameterValue": self.config.secret_name,
            },
            {
                "ParameterKey": "TokensSecretName",
                "ParameterValue": self.config.tokens_secret_name,
            },
        ]

    def get_dev_template_body(self) -> str:
        with open(self.dev_template, "r") as f:
            return f.read()

    def create_cloudformation_stack(
            self, *,
            template_body: str,
            parameters: list[CloudFormationParameter],
        ) -> dict:
        """Set up AWS resources using CloudFormation."""
        try:
            res = self.client.create_stack(
                StackName=self.config.stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=["CAPABILITY_IAM"]
            )
            self.logger(f"Creation of CloudFormation stack {Colorizer.blue(self.config.stack_name)} started")

            # Wait for stack creation to complete
            self.logger("Waiting for AWS resources to be created...")
            waiter = self.client.get_waiter("stack_create_complete")
            waiter.wait(StackName=self.config.stack_name)
            self.logger(f"Creation of CloudFormation stack {Colorizer.blue(self.config.stack_name)} completed")

            return res

        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"AWS resource creation failed due to ClientError: {Colorizer.white(e)}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"AWS resource creation failed due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

    def dev_uninstall(self) -> None:
        """Uninstall the resources in development mode."""
        try:
            self.client.delete_stack(StackName=self.config.stack_name)
            self.logger(f"Deletion of CloudFormation stack {Colorizer.blue(self.config.stack_name)} started")

            # Wait for stack deletion to complete
            waiter = self.client.get_waiter("stack_delete_complete")
            waiter.wait(StackName=self.config.stack_name)
            self.logger(f"Deletion of CloudFormation stack {Colorizer.blue(self.config.stack_name)} completed")

        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"AWS resource deletion failed due to ClientError: {Colorizer.white(e)}")
            raise UninstallError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"AWS resource deletion failed due to unexpected error: {Colorizer.white(e)}")
            raise UninstallError(e)
