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
import os
from typing import Any
from unittest.mock import Mock

from src.utils import FileReader


def load_mock_data() -> dict[str, list[dict[str, Any]]]:
    with open(
        os.path.join(
            os.getcwd(),
            "functions",
            "db_bootstrapper",
            "tests_db_bootstrapper",
            "mock_data.json",
        ),
    ) as f:
        return json.load(f)


def create_mock_file_reader() -> FileReader:
    """Create a mock file reader that returns the given data."""
    file_reader = FileReader()
    file_reader.read_json = Mock(return_value=load_mock_data())
    return file_reader
