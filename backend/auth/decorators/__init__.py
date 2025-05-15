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
Authentication decorators for backend.

These decorators handle the authentication and authorization of users.
"""

from backend.auth.decorators.jwt import auth_required
from backend.auth.decorators.participant import participant_auth_required
from backend.auth.decorators.researcher import researcher_auth_required

__all__ = [
    "auth_required",  # Deprecated, maintained for backward compatibility
    "participant_auth_required",
    "researcher_auth_required",
]
