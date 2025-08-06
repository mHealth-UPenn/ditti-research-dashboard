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
from src.utils import DatabaseManager, DbConnectionExecuter

from tests_db_bootstrapper.conftest import (
    IAM_USERNAME,
    POSTGRES_DB,
    MockConnection,
)


@pytest.fixture
def mock_database_manager(test_client: Flask) -> DatabaseManager:
    database_manager = DatabaseManager(test_client)
    return database_manager


@pytest.fixture
def expected_calls() -> list[str]:
    return [
        (
            DbConnectionExecuter.GET_USER_EXISTS,
            {"iam_username": IAM_USERNAME},
            {},
        ),
        (
            DbConnectionExecuter.GRANT_IAM_TO_USER.format(
                iam_username=IAM_USERNAME
            ),
            None,
            {},
        ),
        (
            DbConnectionExecuter.GRANT_CONNECT_TO_DATABASE.format(
                database=POSTGRES_DB, iam_username=IAM_USERNAME
            ),
            None,
            {},
        ),
        (
            DbConnectionExecuter.GRANT_USAGE_TO_SCHEMA.format(
                iam_username=IAM_USERNAME
            ),
            None,
            {},
        ),
        (
            DbConnectionExecuter.GRANT_ALL_PRIVILEGES_TO_TABLES.format(
                iam_username=IAM_USERNAME
            ),
            None,
            {},
        ),
        (
            DbConnectionExecuter.GRANT_ALL_PRIVILEGES_TO_SEQUENCES.format(
                iam_username=IAM_USERNAME
            ),
            None,
            {},
        ),
        (
            DbConnectionExecuter.ALTER_DEFAULT_PRIVILEGES_TO_TABLES.format(
                iam_username=IAM_USERNAME
            ),
            None,
            {},
        ),
        (DbConnectionExecuter.GET_CURRENT_DATABASE, None, {}),
    ]


class TestDatabaseManager:
    """Test the DatabaseManager class."""

    def test_setup_iam_database_user_new_user(
        self, mock_database_manager: DatabaseManager, expected_calls: list[str]
    ):
        """Test setting up IAM database user for new user."""
        mock_connection = MockConnection(user_exists=False)
        mock_database_manager._get_connection = Mock(return_value=mock_connection)
        mock_database_manager.setup_iam_database_user(IAM_USERNAME)

        expected_calls.append(
            (
                DbConnectionExecuter.CREATE_USER.format(
                    iam_username=IAM_USERNAME
                ),
                None,
                {},
            )
        )

        # Verify user creation commands were executed
        assert set(mock_connection.call_args_list) == {
            str(call) for call in expected_calls
        }

    def test_setup_iam_database_user_existing_user(
        self, mock_database_manager: DatabaseManager, expected_calls: list[str]
    ):
        """Test setting up IAM database user for new user."""
        mock_connection = MockConnection(user_exists=True)
        mock_database_manager._get_connection = Mock(return_value=mock_connection)
        mock_database_manager.setup_iam_database_user(IAM_USERNAME)

        # Verify user creation commands were executed
        assert set(mock_connection.call_args_list) == {
            str(call) for call in expected_calls
        }

    def test_test_iam_connection(self, mock_database_manager: DatabaseManager):
        """Test IAM connection testing."""
        # Arrange
        mock_connection = MockConnection(user_exists=True)
        mock_database_manager._get_connection = Mock(return_value=mock_connection)

        # Act
        mock_database_manager.test_iam_connection()

        # Assert
        mock_connection.call_args_list = [
            (
                DbConnectionExecuter.TEST_IAM_CONNECTION,
                None,
                {},
            )
        ]
