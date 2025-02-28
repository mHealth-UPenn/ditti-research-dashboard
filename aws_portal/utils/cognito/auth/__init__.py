"""Authentication classes for Cognito."""

from aws_portal.utils.cognito.auth.base import CognitoAuthBase
# First import the classes only
from aws_portal.utils.cognito.auth.participant import ParticipantAuth, init_oauth_client
from aws_portal.utils.cognito.auth.researcher import ResearcherAuth, init_researcher_oauth_client

# Then import the decorators separately to avoid circular imports
from aws_portal.utils.cognito.auth.participant import participant_auth_required
from aws_portal.utils.cognito.auth.researcher import researcher_auth_required

__all__ = [
    "CognitoAuthBase",
    "ParticipantAuth",
    "init_oauth_client",
    "ResearcherAuth",
    "init_researcher_oauth_client",
    "participant_auth_required",
    "researcher_auth_required"
]
