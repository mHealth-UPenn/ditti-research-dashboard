"""
Cognito-specific authentication implementation.
This package contains all the code needed to interact with AWS Cognito
for authentication purposes.
"""

from backend.auth.providers.cognito.base import CognitoAuthBase
from backend.auth.providers.cognito.participant import ParticipantAuth, init_participant_oauth_client
from backend.auth.providers.cognito.researcher import ResearcherAuth, init_researcher_oauth_client
from backend.auth.providers.cognito.constants import AUTH_ERROR_MESSAGES

__all__ = ["CognitoAuthBase", "ParticipantAuth", "init_participant_oauth_client",
           "ResearcherAuth", "AUTH_ERROR_MESSAGES", "init_researcher_oauth_client"]
