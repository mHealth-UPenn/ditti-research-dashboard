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

# Disable linter warnings for print statements (quick fix for logging issues with alembic)
# ruff: noqa: T201

from enum import Enum

from flask import Flask
from flask_migrate import upgrade
from sqlalchemy import Connection, text

from src.backend.extensions import db


class DatabaseManagerTextClause(Enum):
    GET_USER_EXISTS = "SELECT 1 FROM pg_roles WHERE rolname = :iam_username"
    GET_CURRENT_DATABASE = "SELECT current_database()"
    CREATE_USER = "CREATE USER :iam_username WITH LOGIN"
    GRANT_IAM_TO_USER = "GRANT rds_iam TO :iam_username"
    GRANT_CONNECT_TO_DATABASE = (
        "GRANT CONNECT ON DATABASE {database} TO :iam_username"
    )
    GRANT_USAGE_TO_SCHEMA = "GRANT USAGE ON SCHEMA public TO :iam_username"
    GRANT_ALL_PRIVILEGES_TO_TABLES = (
        "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO :iam_username"
    )
    GRANT_ALL_PRIVILEGES_TO_SEQUENCES = (
        "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO :iam_username"
    )
    ALTER_DEFAULT_PRIVILEGES_TO_TABLES = "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO :iam_username"
    TEST_IAM_CONNECTION = (
        "SELECT 1 as test, current_user as user, current_database() as db"
    )


class DatabaseManager:
    """Manages database operations."""

    def __init__(self, app: Flask):
        """
        Initialize the database manager.

        Args:
            app: The Flask application with configured database.
        """
        self.app = app

    def upgrade_database(self) -> None:
        """Upgrade the database using Flask-Migrate."""
        with self.app.app_context():
            upgrade()

    def _get_connection(self) -> Connection:
        """Get a connection to the database."""
        return db.engine.connect()

    def setup_iam_database_user(self, iam_username: str) -> None:
        """
        Set up a database user for IAM authentication using master credentials.

        Args:
            iam_username: The username to create for IAM authentication.
        """
        try:
            with self.app.app_context():
                connection = self._get_connection()

                try:
                    # Check if user already exists
                    result = connection.execute(
                        text(DatabaseManagerTextClause.GET_USER_EXISTS.value),
                        {"iam_username": iam_username},
                    )

                    if not result.fetchone():
                        print(
                            f"Creating new user {iam_username} with IAM authentication"
                        )
                        connection.execute(
                            text(DatabaseManagerTextClause.CREATE_USER.value),
                            {"iam_username": iam_username},
                        )
                    else:
                        print(
                            f"User {iam_username} already exists, updating IAM permissions"
                        )

                    connection.execute(
                        text(DatabaseManagerTextClause.GRANT_IAM_TO_USER.value),
                        {"iam_username": iam_username},
                    )

                    # Get the current database name from the connection
                    db_result = connection.execute(
                        text(
                            DatabaseManagerTextClause.GET_CURRENT_DATABASE.value
                        ),
                    )
                    current_db = db_result.fetchone()[0]
                    print(f"Setting up permissions for database: {current_db}")

                    # Grant necessary permissions
                    self._grant_database_permissions(
                        connection, iam_username, current_db
                    )

                    connection.commit()

                finally:
                    connection.close()

        except Exception as e:
            print(f"Error setting up IAM database user {iam_username}: {e}")
            raise

    def _grant_database_permissions(
        self, connection: Connection, iam_username: str, database: str
    ) -> None:
        """Grant necessary permissions to the IAM user."""
        permissions = [
            DatabaseManagerTextClause.GRANT_CONNECT_TO_DATABASE.value.format(
                database=database
            ),
            DatabaseManagerTextClause.GRANT_USAGE_TO_SCHEMA.value,
            DatabaseManagerTextClause.GRANT_ALL_PRIVILEGES_TO_TABLES.value,
            DatabaseManagerTextClause.GRANT_ALL_PRIVILEGES_TO_SEQUENCES.value,
            DatabaseManagerTextClause.ALTER_DEFAULT_PRIVILEGES_TO_TABLES.value,
        ]

        for permission in permissions:
            connection.execute(text(permission), {"iam_username": iam_username})

    def test_iam_connection(self) -> None:
        """Test the IAM database connection."""
        with self.app.app_context():
            connection = self._get_connection()
            try:
                result = connection.execute(
                    text(DatabaseManagerTextClause.TEST_IAM_CONNECTION.value)
                )
                result.fetchone()
            except Exception as e:
                print(f"Error testing IAM database connection: {e}")
                raise
            finally:
                connection.close()
