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

from backend.views.auth.participant.auth import (
    blueprint as participant_auth_blueprint,
)
from backend.views.auth.researcher.auth import (
    blueprint as researcher_auth_blueprint,
)

__all__ = ["participant_auth_blueprint", "researcher_auth_blueprint"]
