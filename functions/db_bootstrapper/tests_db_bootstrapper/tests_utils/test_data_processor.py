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

from datetime import datetime

from src.utils import DataProcessor


class TestDataProcessor:
    """Test the DataProcessor class."""

    def test_clean_row_data_with_datetime_string(self):
        """Test cleaning row data with datetime string."""
        datetime_str = "2023-01-01T12:00:00.123456"
        row = {"id": 1, "created_at": datetime_str}

        result = DataProcessor.clean_row_data(row)

        assert result["id"] == 1
        assert isinstance(result["created_at"], datetime)
        assert result["created_at"].isoformat() == datetime_str

    def test_clean_row_data_with_invalid_datetime_string(self):
        """Test cleaning row data with invalid datetime string."""
        row = {"id": 1, "created_at": "invalid-datetime"}

        result = DataProcessor.clean_row_data(row)

        # Assert
        assert result["created_at"] == "invalid-datetime"
