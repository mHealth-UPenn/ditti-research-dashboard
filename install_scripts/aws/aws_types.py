from typing import TypedDict


class CloudFormationParameter(TypedDict):
    ParameterKey: str
    ParameterValue: str
