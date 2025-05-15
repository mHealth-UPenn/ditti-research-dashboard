# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Cognito-specific authentication implementation.

This package contains all the code needed to interact with AWS Cognito
for authentication purposes.
"""

from backend.auth.providers.cognito.base import CognitoAuthBase
from backend.auth.providers.cognito.constants import AUTH_ERROR_MESSAGES
from backend.auth.providers.cognito.participant import (
    ParticipantAuth,
    init_participant_oauth_client,
)
from backend.auth.providers.cognito.researcher import (
    ResearcherAuth,
    init_researcher_oauth_client,
)

__all__ = [
    "AUTH_ERROR_MESSAGES",
    "CognitoAuthBase",
    "ParticipantAuth",
    "ResearcherAuth",
    "init_participant_oauth_client",
    "init_researcher_oauth_client",
]
