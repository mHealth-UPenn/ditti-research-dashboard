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

from typing import Any
from unittest.mock import Mock

import pytest
from flask import Flask
from sqlalchemy import Connection, Result, TextClause
from src.utils import DatabaseManager
from src.utils.database_manager import DatabaseManagerTextClause

from tests_db_bootstrapper.conftest import POSTGRES_DB


class MockResult(Result):
    def __init__(self, return_value: Any):
        self.fetchone = Mock(return_value=return_value)


class MockConnection(Connection):
    def __init__(self, *, user_exists: bool):
        self.user_exists = user_exists
        self.commit = Mock()
        self.close = Mock()
        self.call_args_list = []

    def execute(
        self, statement: TextClause, parameters=None, **kwargs
    ) -> MockResult:
        self.call_args_list.append(str((statement.text, parameters, kwargs)))
        if statement.text == DatabaseManagerTextClause.GET_USER_EXISTS.value:
            return MockResult(self.user_exists)
        if statement.text == DatabaseManagerTextClause.GET_CURRENT_DATABASE.value:
            return MockResult((POSTGRES_DB,))
        if statement.text == DatabaseManagerTextClause.TEST_IAM_CONNECTION.value:
            return MockResult((1, "test_user", POSTGRES_DB))
        return None


@pytest.fixture
def mock_database_manager(test_client: Flask) -> DatabaseManager:
    database_manager = DatabaseManager(test_client)
    return database_manager


@pytest.fixture
def expected_calls() -> list[str]:
    return [
        (
            DatabaseManagerTextClause.GET_USER_EXISTS.value,
            {"iam_username": "test_user"},
            {},
        ),
        (
            DatabaseManagerTextClause.GRANT_IAM_TO_USER.value,
            {"iam_username": "test_user"},
            {},
        ),
        (
            DatabaseManagerTextClause.GRANT_CONNECT_TO_DATABASE.value.format(
                database=POSTGRES_DB
            ),
            {"iam_username": "test_user"},
            {},
        ),
        (
            DatabaseManagerTextClause.GRANT_USAGE_TO_SCHEMA.value,
            {"iam_username": "test_user"},
            {},
        ),
        (
            DatabaseManagerTextClause.GRANT_ALL_PRIVILEGES_TO_TABLES.value,
            {"iam_username": "test_user"},
            {},
        ),
        (
            DatabaseManagerTextClause.GRANT_ALL_PRIVILEGES_TO_SEQUENCES.value,
            {"iam_username": "test_user"},
            {},
        ),
        (
            DatabaseManagerTextClause.ALTER_DEFAULT_PRIVILEGES_TO_TABLES.value,
            {"iam_username": "test_user"},
            {},
        ),
        (DatabaseManagerTextClause.GET_CURRENT_DATABASE.value, None, {}),
    ]


class TestDatabaseManager:
    """Test the DatabaseManager class."""

    def test_setup_iam_database_user_new_user(
        self, mock_database_manager: DatabaseManager, expected_calls: list[str]
    ):
        """Test setting up IAM database user for new user."""
        mock_connection = MockConnection(user_exists=False)
        mock_database_manager._get_connection = Mock(return_value=mock_connection)
        mock_database_manager.setup_iam_database_user("test_user")

        expected_calls.append(
            (
                DatabaseManagerTextClause.CREATE_USER.value,
                {"iam_username": "test_user"},
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
        mock_database_manager.setup_iam_database_user("test_user")

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
                DatabaseManagerTextClause.TEST_IAM_CONNECTION.value,
                None,
                {},
            )
        ]
