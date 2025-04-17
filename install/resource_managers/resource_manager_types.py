from typing import TypedDict


class CloudFormationParameter(TypedDict):
    ParameterKey: str
    ParameterValue: str


class DevSecretValue(TypedDict):
    FITBIT_CLIENT_ID: str
    FITBIT_CLIENT_SECRET: str
    COGNITO_PARTICIPANT_CLIENT_SECRET: str
    COGNITO_RESEARCHER_CLIENT_SECRET: str


class S3Object(TypedDict):
    Key: str
    VersionId: str
