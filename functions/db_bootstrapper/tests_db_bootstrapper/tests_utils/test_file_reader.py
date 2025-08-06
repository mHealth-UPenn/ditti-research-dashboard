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

import json

import pytest
from src.utils import FileReader


class TestFileReader:
    """Test the FileReader implementation."""

    def test_read_json_success(self, tmp_path):
        """Test successful JSON file reading."""
        test_data = {"table1": [{"id": 1, "name": "test"}]}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(test_data))

        reader = FileReader()

        result = reader.read_json(str(json_file))

        assert result == test_data

    def test_read_json_file_not_found(self):
        """Test reading non-existent file raises FileNotFoundError."""
        reader = FileReader()

        with pytest.raises(FileNotFoundError):
            reader.read_json("nonexistent.json")

    def test_read_json_invalid_json(self, tmp_path):
        """Test reading invalid JSON raises JSONDecodeError."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("invalid json content")

        reader = FileReader()

        with pytest.raises(json.JSONDecodeError):
            reader.read_json(str(json_file))
