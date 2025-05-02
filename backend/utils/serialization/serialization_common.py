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

import re

from pydantic import ConfigDict


def snake_to_camel(string: str) -> str:
    """Convert a snake_case string to camelCase."""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def camel_to_snake(name: str) -> str:
    """Convert a camelCase string to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


common_config = ConfigDict(
    from_attributes=True,
    extra="forbid",  # Disallow extra fields
    alias_generator=snake_to_camel,
    populate_by_name=True,
    use_enum_values=True,
)
