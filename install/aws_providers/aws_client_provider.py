from typing import Any

import boto3


class AwsClientProvider:
    sts_client: Any
    cognito_client: Any
    s3_client: Any
    secrets_manager_client: Any
    cloudformation_client: Any
    ecr_client: Any

    # Unit test: boto3.client is initialized with expected arguments
    def __init__(self):
        self.sts_client = boto3.client("sts")
        self.cognito_client = boto3.client("cognito-idp")
        self.s3_client = boto3.client("s3")
        self.secrets_manager_client = boto3.client("secretsmanager")
        self.cloudformation_client = boto3.client("cloudformation")
        self.ecr_client = boto3.client("ecr")
