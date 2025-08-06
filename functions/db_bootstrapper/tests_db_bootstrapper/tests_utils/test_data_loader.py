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

from unittest.mock import Mock

import pytest
from flask import Flask
from src.utils import DataLoader, FileReader
from src.utils.data_loader import DataLoaderMessage
from src.utils.sequence_manager import SequenceManagerMessage

from tests_db_bootstrapper.conftest import MOCK_EMPTY_TABLE_NAME, MOCK_TABLE_NAME
from tests_db_bootstrapper.tests_utils.mock_file_reader import (
    create_mock_file_reader,
    load_mock_data,
)


@pytest.fixture
def mock_data_loader(test_client: Flask) -> DataLoader:
    data_loader = DataLoader(test_client)
    data_loader.file_reader = create_mock_file_reader()
    return data_loader


@pytest.fixture
def expected_messages() -> set[str]:
    mock_data = load_mock_data()
    num_rows = len(mock_data[MOCK_TABLE_NAME])
    max_id = max(row["id"] for row in mock_data[MOCK_TABLE_NAME])
    return {
        DataLoaderMessage.rows_inserted(num_rows, MOCK_TABLE_NAME),
        SequenceManagerMessage.sequence_reset(MOCK_TABLE_NAME, max_id + 1),
        SequenceManagerMessage.sequence_reset(MOCK_EMPTY_TABLE_NAME, 1),
        DataLoaderMessage.data_committed(),
        SequenceManagerMessage.sequence_reset_success(),
    }


class TestDataLoader:
    """Test the DataLoader class."""

    def test_init_with_default_file_reader(self, test_client: Flask):
        """Test DataLoader initialization with default file reader."""
        loader = DataLoader(test_client)

        assert isinstance(loader.file_reader, FileReader)
        assert loader.app is test_client

    def test_load_data_success(
        self,
        with_mock_tables: None,
        mock_data_loader: DataLoader,
        expected_messages: set[str],
    ):
        """Test successful data loading."""
        result = mock_data_loader.load_data("test.json")

        assert set(result) == expected_messages

    def test_load_data_table_not_found(self, mock_data_loader: DataLoader):
        """Test data loading when table is not found."""
        # Arrange
        test_data = {"nonexistent_table": [{"id": 1}]}
        mock_data_loader.file_reader.read_json = Mock(return_value=test_data)

        result = mock_data_loader.load_data("test.json")

        expected_messages = {
            DataLoaderMessage.table_not_found("nonexistent_table"),
            SequenceManagerMessage.sequence_reset_success(),
            DataLoaderMessage.data_committed(),
        }

        # Assert
        assert set(result) == expected_messages
