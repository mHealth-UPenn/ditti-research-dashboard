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

from pathlib import Path
from unittest.mock import Mock

import pytest
from src.utils import S3FileManager

from tests_db_bootstrapper.conftest import MOCK_DATA_ARN


class TestS3FileManager:
    """Test the AWSS3FileManager implementation."""

    def test_download_file_success(self, with_mock_bucket: None, tmp_path: Path):
        """Test successful file download."""
        # Arrange
        s3_manager = S3FileManager()

        # Act
        result = s3_manager.download_file(
            MOCK_DATA_ARN, str(tmp_path / "test.json")
        )

        # Assert
        assert result == str(tmp_path / "test.json")

    def test_download_file_with_error(self, tmp_path: Path):
        """Test file download with error."""
        # Arrange
        s3_manager = S3FileManager()
        s3_manager.client.download_file = Mock(side_effect=Exception("S3 Error"))

        # Act & Assert
        with pytest.raises(Exception, match="S3 Error"):
            s3_manager.download_file(MOCK_DATA_ARN, str(tmp_path / "test.json"))
