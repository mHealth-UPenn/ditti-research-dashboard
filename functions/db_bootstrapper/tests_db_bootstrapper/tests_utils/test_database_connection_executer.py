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
from sqlalchemy import text
from src.utils.database_connection_executer import DbConnectionExecuter

from tests_db_bootstrapper.conftest import MockConnection


@pytest.fixture
def db_executer(mock_connection: Mock) -> DbConnectionExecuter:
    """Create a DbConnectionExecuter instance with a mock connection."""
    return DbConnectionExecuter(mock_connection)


@pytest.fixture
def mock_connection() -> MockConnection:
    """Create a mock SQLAlchemy Connection."""
    return MockConnection(user_exists=True)


class TestDbConnectionExecuter:
    """Test the DbConnectionExecuter class."""

    def test_init(self, mock_connection: Mock):
        """Test DbConnectionExecuter initialization."""
        executer = DbConnectionExecuter(mock_connection)
        assert executer.connection is mock_connection

    def test_get_user_exists(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test get_user_exists method."""
        iam_username = "test_user"

        db_executer.get_user_exists(iam_username)

        assert len(mock_connection.call_args_list) == 1
        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GET_USER_EXISTS,
                {"iam_username": iam_username},
                {},
            )
        )

    def test_get_current_database(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test get_current_database method."""
        db_executer.get_current_database()

        assert len(mock_connection.call_args_list) == 1
        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GET_CURRENT_DATABASE,
                None,
                {},
            )
        )

    def test_create_user(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test create_user method."""
        iam_username = "new_user"

        db_executer.create_user(iam_username)

        assert len(mock_connection.call_args_list) == 1
        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.CREATE_USER.format(
                    iam_username=iam_username
                ),
                None,
                {},
            )
        )

    def test_grant_iam_to_user(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test grant_iam_to_user method."""
        iam_username = "test_user"

        db_executer.grant_iam_to_user(iam_username)

        assert len(mock_connection.call_args_list) == 1
        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GRANT_IAM_TO_USER.format(
                    iam_username=iam_username
                ),
                None,
                {},
            )
        )

    def test_grant_connect_to_database(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test grant_connect_to_database method."""
        database = "test_db"
        iam_username = "test_user"

        db_executer.grant_connect_to_database(database, iam_username)

        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GRANT_CONNECT_TO_DATABASE.format(
                    database=database, iam_username=iam_username
                ),
                None,
                {},
            )
        )

    def test_grant_usage_to_schema(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test grant_usage_to_schema method."""
        iam_username = "test_user"

        db_executer.grant_usage_to_schema(iam_username)

        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GRANT_USAGE_TO_SCHEMA.format(
                    iam_username=iam_username
                ),
                None,
                {},
            )
        )

    def test_grant_all_privileges_to_tables(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test grant_all_privileges_to_tables method."""
        iam_username = "test_user"

        db_executer.grant_all_privileges_to_tables(iam_username)

        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GRANT_ALL_PRIVILEGES_TO_TABLES.format(
                    iam_username=iam_username
                ),
                None,
                {},
            )
        )

    def test_grant_all_privileges_to_sequences(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test grant_all_privileges_to_sequences method."""
        iam_username = "test_user"

        db_executer.grant_all_privileges_to_sequences(iam_username)

        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GRANT_ALL_PRIVILEGES_TO_SEQUENCES.format(
                    iam_username=iam_username
                ),
                None,
                {},
            )
        )

    def test_alter_default_privileges_to_tables(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test alter_default_privileges_to_tables method."""
        iam_username = "test_user"

        db_executer.alter_default_privileges_to_tables(iam_username)

        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.ALTER_DEFAULT_PRIVILEGES_TO_TABLES.format(
                    iam_username=iam_username
                ),
                None,
                {},
            )
        )

    def test_test_iam_connection(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test test_iam_connection method."""
        db_executer.test_iam_connection()

        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.TEST_IAM_CONNECTION,
                None,
                {},
            )
        )

    def test_sql_queries_are_valid_sql(self):
        """Test that SQL queries are valid SQL statements."""
        # Test that queries can be parsed as valid SQL
        queries = [
            DbConnectionExecuter.GET_USER_EXISTS,
            DbConnectionExecuter.GET_CURRENT_DATABASE,
            DbConnectionExecuter.CREATE_USER,
            DbConnectionExecuter.GRANT_IAM_TO_USER,
            DbConnectionExecuter.GRANT_CONNECT_TO_DATABASE,
            DbConnectionExecuter.GRANT_USAGE_TO_SCHEMA,
            DbConnectionExecuter.GRANT_ALL_PRIVILEGES_TO_TABLES,
            DbConnectionExecuter.GRANT_ALL_PRIVILEGES_TO_SEQUENCES,
            DbConnectionExecuter.ALTER_DEFAULT_PRIVILEGES_TO_TABLES,
            DbConnectionExecuter.TEST_IAM_CONNECTION,
        ]

        for query in queries:
            # This will raise an exception if the SQL is invalid
            text(query)

    def test_methods_handle_special_characters_in_usernames(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test that methods handle special characters in usernames correctly."""
        special_username = "user_with_underscores_and-dashes"

        # Test a few methods with special characters
        db_executer.get_user_exists(special_username)
        db_executer.create_user(special_username)
        db_executer.grant_iam_to_user(special_username)

        # Verify the calls were made with the correct username
        assert len(mock_connection.call_args_list) == 3

        # Check that the username is properly passed in the parameters
        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GET_USER_EXISTS,
                {"iam_username": special_username},
                {},
            )
        )

        assert mock_connection.call_args_list[1] == str(
            (
                DbConnectionExecuter.CREATE_USER.format(
                    iam_username=special_username
                ),
                None,
                {},
            )
        )

        assert mock_connection.call_args_list[2] == str(
            (
                DbConnectionExecuter.GRANT_IAM_TO_USER.format(
                    iam_username=special_username
                ),
                None,
                {},
            )
        )

    def test_methods_handle_empty_strings(
        self,
        db_executer: DbConnectionExecuter,
        mock_connection: MockConnection,
    ):
        """Test that methods handle empty strings correctly."""
        empty_username = ""
        empty_database = ""

        # Test methods with empty strings
        db_executer.get_user_exists(empty_username)
        db_executer.create_user(empty_username)
        db_executer.grant_connect_to_database(empty_database, empty_username)

        # Verify the calls were made
        assert len(mock_connection.call_args_list) == 3

        assert mock_connection.call_args_list[0] == str(
            (
                DbConnectionExecuter.GET_USER_EXISTS,
                {"iam_username": empty_username},
                {},
            )
        )

        assert mock_connection.call_args_list[1] == str(
            (
                DbConnectionExecuter.CREATE_USER.format(
                    iam_username=empty_username
                ),
                None,
                {},
            )
        )

        assert mock_connection.call_args_list[2] == str(
            (
                DbConnectionExecuter.GRANT_CONNECT_TO_DATABASE.format(
                    database=empty_database, iam_username=empty_username
                ),
                None,
                {},
            )
        )
