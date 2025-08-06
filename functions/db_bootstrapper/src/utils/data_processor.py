# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re
from datetime import datetime
from typing import Any


class DataProcessor:
    """Handles data processing and transformation."""

    @staticmethod
    def clean_row_data(row: dict[str, Any]) -> dict[str, Any]:
        """Clean and transform row data for database insertion."""
        # Convert iso format strings to datetime objects
        for key, value in row.items():
            if isinstance(value, str) and re.match(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}", value
            ):
                row[key] = datetime.fromisoformat(value)

        return row
