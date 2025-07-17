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

from collections.abc import Generator
from unittest.mock import Mock

import boto3
import pytest
from moto import mock_aws
from src.utils import SecretManager


@pytest.fixture
def with_mock_secret() -> Generator[None, None, None]:
    with mock_aws():
        client = boto3.client("secretsmanager")
        client.create_secret(
            Name="test_secret", SecretString='{"password": "test123"}'
        )
        yield


class TestAWSSecretManager:
    """Test the AWSSecretManager implementation."""

    def test_get_secret_success(self, with_mock_secret: None):
        """Test successful secret retrieval."""
        # Arrange
        secret_manager = SecretManager()

        # Act
        result = secret_manager.get_secret("test_secret")

        # Assert
        assert result == {"password": "test123"}

    def test_get_secret_with_error(self):
        """Test secret retrieval with error."""
        # Arrange
        secret_manager = SecretManager()
        secret_manager.client.get_secret_value = Mock(
            side_effect=Exception("AWS Error")
        )

        # Act & Assert
        with pytest.raises(Exception, match="AWS Error"):
            secret_manager.get_secret("test_secret")
