from typing import TypedDict


class CloudFormationParameter(TypedDict):
    """
    Type definition for CloudFormation parameters.

    Represents key-value pairs used as parameters when creating
    or updating CloudFormation stacks.
    """

    ParameterKey: str
    ParameterValue: str


class DevSecretValue(TypedDict):
    """
    Type definition for development environment secrets.

    Contains credential values required for third-party integrations
    and authentication in the development environment.
    """

    FITBIT_CLIENT_ID: str
    FITBIT_CLIENT_SECRET: str
    COGNITO_PARTICIPANT_CLIENT_SECRET: str
    COGNITO_RESEARCHER_CLIENT_SECRET: str


class S3Object(TypedDict):
    """
    Type definition for S3 object identifiers.

    Contains the key and version ID needed to uniquely identify
    objects in versioned S3 buckets.
    """

    Key: str
    VersionId: str
