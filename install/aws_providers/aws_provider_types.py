from typing import TypedDict


class DevCloudformationOutputs(TypedDict):
    """
    Type definition for CloudFormation outputs in development environment.

    Contains output parameter names that are expected from the
    CloudFormation stack in the development environment.
    """

    ParticipantUserPoolId: str
    ParticipantClientId: str
    ResearcherUserPoolId: str
    ResearcherClientId: str
