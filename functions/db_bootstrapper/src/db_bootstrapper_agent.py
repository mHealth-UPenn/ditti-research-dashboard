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

import os
import traceback
from enum import Enum
from typing import Any

from flask import Flask

from src.utils import (
    AppFactory,
    DatabaseManager,
    DataLoader,
    DbUri,
    S3FileManager,
    SecretManager,
)


class DBBootstrapperAgentMessage(Enum):
    """Message types for the database bootstrapper agent."""

    CREATE_SUCCESS = "Database upgraded and configured successfully."
    CREATE_ERROR = "Error in Create request: {error}"
    UPDATE_SUCCESS = "Database upgraded."
    UPDATE_ERROR = "Error in Update request: {error}"
    DELETE_SUCCESS = "Skipping bootstrap on delete."


class DBBootstrapperAgent:
    """Main agent class for database bootstrapping operations."""

    data_file = "/tmp/data.json"  # noqa: S108

    def __init__(
        self,
        local_db: bool = False,
    ):
        """
        Initialize the database bootstrapper agent.

        Args:
            secret_manager: Secret manager implementation.
            s3_file_manager: S3 file manager implementation.
            data_loader: Data loader implementation.
            app_factory: Application factory implementation.
            local_db: Whether to use local database (disables IAM).
        """
        self.secret_manager = SecretManager()
        self.s3_file_manager = S3FileManager()
        self.app_factory = AppFactory()
        self.local_db = local_db

        # Environment variables
        self.secret_arn = os.getenv("DB_SECRET_ARN")
        self.username = os.getenv("DB_USER")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.database = os.getenv("DB_NAME")
        self.iam_username = os.getenv("DB_IAM_USER")
        self.data_arn = os.getenv("DB_BOOTSTRAP_DATA_ARN")

    def validate_environment(self) -> None:
        """Validate that all required environment variables are set."""
        if not self.secret_arn:
            raise ValueError("DB_SECRET_ARN is not set")

        if not all([self.username, self.host, self.port, self.database]):
            raise ValueError("DB credentials are not set")

        if not self.iam_username:
            raise ValueError("DB_IAM_USER is not set")

    def get_database_secret(self) -> dict[str, Any]:
        """
        Retrieve the database secret.

        Returns
        -------
            The database secret as a dictionary.
        """
        secret = self.secret_manager.get_secret(self.secret_arn)

        if not secret or "password" not in secret:
            raise ValueError("DB secret does not contain password")

        return secret

    def create_master_app(self, password: str) -> Flask:
        """
        Create a Flask app with master database credentials.

        Args:
            password: The master database password.

        Returns
        -------
            Configured Flask application.
        """
        db_uri = DbUri(
            hostname=self.host,
            port=self.port,
            database=self.database,
            username=self.username,
            password=password,
        )
        return self.app_factory.create_app(db_uri, use_iam=False)

    def create_iam_app(self, iam_username: str) -> Flask:
        """
        Create a Flask app with IAM authentication.

        Args:
            iam_username: The IAM username.

        Returns
        -------
            Configured Flask application.
        """
        if self.local_db:
            # Use master credentials for local development
            secret = self.get_database_secret()
            db_uri = DbUri(
                hostname=self.host,
                port=self.port,
                database=self.database,
                username=self.username,
                password=secret["password"],
            )
            return self.app_factory.create_app(db_uri, use_iam=False)
        else:
            # Use IAM authentication
            db_uri = DbUri(
                hostname=self.host,
                port=self.port,
                database=self.database,
                username=iam_username,
            )
            return self.app_factory.create_app(db_uri, use_iam=True)

    def create_db_manager(self, app: Flask) -> DatabaseManager:
        """Create a database manager."""
        return DatabaseManager(app)

    def create_data_loader(self, app: Flask) -> DataLoader:
        """Create a data loader."""
        return DataLoader(app)

    def handle_create_request(self, event: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """
        Handle CloudFormation Create request.

        Args:
            event: The CloudFormation event.

        Returns
        -------
            Response dictionary.
        """
        try:
            # Validate environment
            self.validate_environment()

            # Get database secret
            secret = self.get_database_secret()
            print("Retrieved database secret")

            # Create master app for initial setup
            master_app = self.create_master_app(secret["password"])

            # Upgrade database
            print("Upgrading database")
            db_manager = self.create_db_manager(master_app)
            db_manager.upgrade_database()
            print("Database upgraded successfully")

            # Setup IAM database user
            print("Setting up IAM database authentication")
            db_manager.setup_iam_database_user(self.iam_username)
            print("IAM database authentication setup")

            # Create IAM app for testing and data loading
            iam_app = self.create_iam_app(self.iam_username)
            iam_db_manager = self.create_db_manager(iam_app)

            # Test IAM connection
            print("Testing IAM database connection")
            iam_db_manager.test_iam_connection()
            print("IAM database connection test successful")

            # Load data if provided
            if self.data_arn:
                print(f"DB_BOOTSTRAP_DATA_ARN: {self.data_arn}")
                print(f"Saving data file from {self.data_arn}")
                filename = self.s3_file_manager.download_file(
                    self.data_arn, self.data_file
                )
                print(f"Data file saved to {filename}")

                print(f"Loading data from file: {filename}")
                data_loader = self.create_data_loader(iam_app)
                data_loader.load_data(filename)
                print("Data loaded successfully")
            else:
                print("No data to load")

            return {"Data": DBBootstrapperAgentMessage.CREATE_SUCCESS.value}

        except Exception as e:
            print(f"Error in Create request: {e}")
            traceback.print_exc()
            return {
                "Data": DBBootstrapperAgentMessage.CREATE_ERROR.value.format(
                    error=e
                )
            }

    def handle_update_request(self, event: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """
        Handle CloudFormation Update request.

        Args:
            event: The CloudFormation event.

        Returns
        -------
            Response dictionary.
        """
        try:
            # Validate environment
            self.validate_environment()

            # Get database secret
            secret = self.get_database_secret()
            print("Retrieved database secret")

            # Create master app for database upgrade
            master_app = self.create_master_app(secret["password"])

            # Upgrade database
            print("Upgrading database")
            db_manager = self.create_db_manager(master_app)
            db_manager.upgrade_database()
            print("Database upgraded successfully")

            return {"Data": DBBootstrapperAgentMessage.UPDATE_SUCCESS.value}

        except Exception as e:
            print(f"Error in Update request: {e}")
            traceback.print_exc()
            return {
                "Data": DBBootstrapperAgentMessage.UPDATE_ERROR.value.format(
                    error=e
                )
            }

    def handle_delete_request(self, event: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """
        Handle CloudFormation Delete request.

        Args:
            event: The CloudFormation event.

        Returns
        -------
            Response dictionary.
        """
        return {"Data": DBBootstrapperAgentMessage.DELETE_SUCCESS.value}

    def handle_request(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle CloudFormation request based on request type.

        Args:
            event: The CloudFormation event.

        Returns
        -------
            Response dictionary.
        """
        request_type = event.get("RequestType")

        if request_type == "Create":
            return self.handle_create_request(event)
        elif request_type == "Update":
            return self.handle_update_request(event)
        elif request_type == "Delete":
            return self.handle_delete_request(event)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
