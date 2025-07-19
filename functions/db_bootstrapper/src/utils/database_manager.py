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


from flask import Flask
from flask_migrate import upgrade
from sqlalchemy import Connection, text

from src.backend.extensions import db
from src.utils.enums import DatabaseManagerTextClause


class DatabaseManager:
    """Manages database operations."""

    MIGRATION_DIR = "./migrations"

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
            upgrade(self.MIGRATION_DIR)

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
                        text(
                            DatabaseManagerTextClause.get_user_exists(),
                        ),
                        {"iam_username": iam_username},
                    )

                    if not result.fetchone():
                        print(
                            f"Creating new user {iam_username} with IAM authentication"
                        )
                        connection.execute(
                            text(
                                DatabaseManagerTextClause.create_user(
                                    iam_username
                                )
                            ),
                        )
                    else:
                        print(
                            f"User {iam_username} already exists, updating IAM permissions"
                        )

                    connection.execute(
                        text(
                            DatabaseManagerTextClause.grant_iam_to_user(
                                iam_username
                            )
                        ),
                    )

                    # Get the current database name from the connection
                    db_result = connection.execute(
                        text(DatabaseManagerTextClause.get_current_database()),
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
            DatabaseManagerTextClause.grant_connect_to_database(
                database, iam_username
            ),
            DatabaseManagerTextClause.grant_usage_to_schema(iam_username),
            DatabaseManagerTextClause.grant_all_privileges_to_tables(
                iam_username
            ),
            DatabaseManagerTextClause.grant_all_privileges_to_sequences(
                iam_username
            ),
            DatabaseManagerTextClause.alter_default_privileges_to_tables(
                iam_username
            ),
        ]

        for permission in permissions:
            connection.execute(text(permission))

    def test_iam_connection(self) -> None:
        """Test the IAM database connection."""
        with self.app.app_context():
            connection = self._get_connection()
            try:
                result = connection.execute(
                    text(DatabaseManagerTextClause.test_iam_connection())
                )
                result.fetchone()
            except Exception as e:
                print(f"Error testing IAM database connection: {e}")
                raise
            finally:
                connection.close()
