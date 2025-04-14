from unittest.mock import MagicMock
from typing import Any, Optional


class MockFactory:
    """Factory class to create consistent mocks for testing."""

    @staticmethod
    def create_mock_settings_provider() -> MagicMock:
        """Create a mock settings object with common attributes."""
        settings = MagicMock()
        settings.admin_email = "test-admin-email"
        settings.fitbit_client_id = "test-fitbit-client-id"
        settings.fitbit_client_secret = "test-fitbit-client-secret"
        settings.project_name = "test-project-name"
        settings.participant_user_pool_name = "test-participant-user-pool-name"
        settings.participant_user_pool_domain = "test-participant-user-pool-domain"
        settings.participant_user_pool_id = "test-participant-user-pool-id"
        settings.participant_client_id = "test-participant-client-id"
        settings.researcher_user_pool_name = "test-researcher-user-pool-name"
        settings.researcher_user_pool_domain = "test-researcher-user-pool-domain"
        settings.researcher_user_pool_id = "test-researcher-user-pool-id"
        settings.researcher_client_id = "test-researcher-client-id"
        settings.logs_bucket_name = "test-logs-bucket-name"
        settings.audio_bucket_name = "test-audio-bucket-name"
        settings.secret_name = "test-secret-name"
        settings.tokens_secret_name = "test-tokens-secret-name"
        settings.stack_name = "test-stack-name"
        settings.network_name = "test-network-name"
        settings.postgres_container_name = "test-postgres-container-name"
        settings.wearable_data_retrieval_container_name = "test-wearable-data-retrieval-container-name"
        return settings

    @staticmethod
    def create_mock_sts_client(
        region_name: str = "us-west-2",
        account_id: str = "123456789012"
    ) -> MagicMock:
        """Create a mock STS client."""
        sts_client = MagicMock()
        sts_client.meta.region_name = region_name
        sts_client.get_caller_identity.return_value = {"Account": account_id}
        return sts_client

    @staticmethod
    def create_mock_cognito_client(
        participant_client_secret: str = "test-participant-secret",
        researcher_client_secret: str = "test-researcher-secret"
    ) -> MagicMock:
        """Create a mock Cognito client."""
        cognito_client = MagicMock()
        
        def describe_user_pool_client_side_effect(**kwargs: Any) -> dict[str, Any]:
            if kwargs.get("ClientId") == "test-participant-client":
                return {"UserPoolClient": {"ClientSecret": participant_client_secret}}
            elif kwargs.get("ClientId") == "test-researcher-client":
                return {"UserPoolClient": {"ClientSecret": researcher_client_secret}}
            raise Exception("Unknown client ID")
            
        cognito_client.describe_user_pool_client.side_effect = describe_user_pool_client_side_effect
        return cognito_client

    @staticmethod
    def create_mock_ecr_client(auth_token: str = "test-auth-token") -> MagicMock:
        """Create a mock ECR client."""
        ecr_client = MagicMock()
        ecr_client.get_authorization_token.return_value = {
            "authorizationData": [{"authorizationToken": auth_token}]
        }
        return ecr_client

    @staticmethod
    def create_mock_cloudformation_client(
        stack_name: str = "test-stack",
        outputs: Optional[list[dict[str, str]]] = None
    ) -> MagicMock:
        """Create a mock CloudFormation client."""
        if outputs is None:
            outputs = [
                {"OutputKey": "TestOutput1", "OutputValue": "value1"},
                {"OutputKey": "TestOutput2", "OutputValue": "value2"}
            ]

        cloudformation_client = MagicMock()
        cloudformation_client.describe_stacks.return_value = {
            "Stacks": [{
                "StackName": stack_name,
                "Outputs": outputs
            }]
        }
        return cloudformation_client

    @staticmethod
    def create_mock_aws_client_provider(
        sts_client: Optional[MagicMock] = None,
        cognito_client: Optional[MagicMock] = None,
        ecr_client: Optional[MagicMock] = None,
        cloudformation_client: Optional[MagicMock] = None
    ) -> MagicMock:
        """Create a mock AWS client provider with all necessary clients."""
        aws_client_provider = MagicMock()
        aws_client_provider.sts_client = sts_client or MockFactory.create_mock_sts_client()
        aws_client_provider.cognito_client = cognito_client or MockFactory.create_mock_cognito_client()
        aws_client_provider.ecr_client = ecr_client or MockFactory.create_mock_ecr_client()
        aws_client_provider.cloudformation_client = cloudformation_client or MockFactory.create_mock_cloudformation_client()
        return aws_client_provider

    @staticmethod
    def create_mock_subprocess(
        aws_access_key_id: str = "test-access-key",
        aws_secret_access_key: str = "test-secret-key"
    ) -> MagicMock:
        """Create a mock subprocess for AWS CLI commands."""
        mock_subprocess = MagicMock()
        
        def check_output_side_effect(args: list[str], **kwargs: Any) -> bytes:
            if "aws_access_key_id" in args:
                return aws_access_key_id.encode()
            elif "aws_secret_access_key" in args:
                return aws_secret_access_key.encode()
            raise Exception("Unknown command")
            
        mock_subprocess.check_output.side_effect = check_output_side_effect
        return mock_subprocess
