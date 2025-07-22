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

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from flask_migrate import init, migrate
from sqlalchemy import text
from src.backend.extensions import db
from src.db_bootstrapper_agent import (
    DBBootstrapperAgent,
    DBBootstrapperAgentMessage,
)
from src.utils import (
    AppFactory,
    DatabaseManager,
    DataLoader,
    DbUri,
    S3FileManager,
    SecretManager,
)

from tests_db_bootstrapper.conftest import (
    IAM_USERNAME,
    MOCK_DATA_ARN,
    MOCK_EMPTY_TABLE_NAME,
    MOCK_SECRET_NAME,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
    MockEmptyTable,
)


@pytest.fixture
def mock_migrations_dir(
    test_client: Flask,
    tmp_path: Path,
) -> Generator[None, None, None]:
    db.drop_all()
    try:
        migrations_dir = str(tmp_path / "migrations")
        DatabaseManager.MIGRATION_DIR = migrations_dir
        init(migrations_dir)
        migrate(migrations_dir)
        yield migrations_dir
    finally:
        DatabaseManager.MIGRATION_DIR = "./migrations"
        db.drop_all()
        db.session.execute(text("DELETE FROM alembic_version"))
        db.session.commit()


@pytest.fixture
def agent(with_mock_secret: None, with_mock_bucket: None) -> DBBootstrapperAgent:
    agent = DBBootstrapperAgent()
    agent.secret_arn = MOCK_SECRET_NAME
    agent.host = "localhost"
    agent.port = POSTGRES_PORT
    agent.database = POSTGRES_DB
    agent.username = POSTGRES_USER
    agent.iam_username = IAM_USERNAME
    return agent


class TestDBBootstrapperAgent:
    """Test the DBBootstrapperAgent class."""

    def test_init_with_defaults(self):
        """Test agent initialization with default components."""
        agent = DBBootstrapperAgent()

        assert isinstance(agent.secret_manager, SecretManager)
        assert isinstance(agent.s3_file_manager, S3FileManager)
        assert isinstance(agent.app_factory, AppFactory)
        assert agent.local_db is False

    @patch.dict(
        os.environ,
        {
            "DB_SECRET_ARN": "arn:aws:secretsmanager:region:account:secret:name",
            "DB_USER": "test_user",
            "DB_HOST": "test_host",
            "DB_PORT": "5432",
            "DB_NAME": "test_db",
            "DB_IAM_USER": "iam_user",
        },
    )
    def test_validate_environment_success(self):
        """Test successful environment validation."""
        agent = DBBootstrapperAgent()

        agent.validate_environment()  # Should not raise

    @patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True)
    def test_validate_environment_missing_secret_arn(self):
        """Test environment validation with missing secret ARN."""
        agent = DBBootstrapperAgent()

        with pytest.raises(ValueError, match="DB_SECRET_ARN is not set"):
            agent.validate_environment()

    @patch.dict(
        os.environ,
        {
            "DB_SECRET_ARN": "arn:aws:secretsmanager:region:account:secret:name",
            "DB_USER": "test_user",
            # Missing other required env vars
        },
    )
    def test_validate_environment_missing_credentials(self):
        """Test environment validation with missing credentials."""
        agent = DBBootstrapperAgent()

        with pytest.raises(ValueError, match="DB credentials are not set"):
            agent.validate_environment()

    def test_get_database_secret_success(self, agent: DBBootstrapperAgent):
        """Test successful database secret retrieval."""
        result = agent.get_database_secret()

        assert result == {
            "password": POSTGRES_PASSWORD,
            "username": POSTGRES_USER,
        }

    def test_get_database_secret_missing_password(
        self, agent: DBBootstrapperAgent
    ):
        """Test database secret retrieval with missing password."""
        agent.secret_manager.get_secret = Mock()
        agent.secret_manager.get_secret.return_value = {"username": "test"}

        with pytest.raises(
            ValueError, match="DB secret does not contain password"
        ):
            agent.get_database_secret()

    def test_create_master_app(self, agent: DBBootstrapperAgent):
        """Test master app creation."""
        # Arrange
        agent.app_factory.create_app = Mock()

        # Act
        agent.create_master_app("test_password")

        # Assert
        expected_db_uri = DbUri(
            hostname=agent.host,
            port=agent.port,
            database=agent.database,
            username=agent.username,
            password="test_password",
        )
        agent.app_factory.create_app.assert_called_once_with(
            expected_db_uri, use_iam=False
        )

    def test_create_iam_app_local_db(self, agent: DBBootstrapperAgent):
        """Test IAM app creation for local database."""
        agent.app_factory.create_app = Mock()
        agent.local_db = True

        agent.create_iam_app("iam_user")

        expected_db_uri = DbUri(
            hostname=agent.host,
            port=agent.port,
            database=agent.database,
            username=agent.username,
            password=POSTGRES_PASSWORD,
        )
        agent.app_factory.create_app.assert_called_once_with(
            expected_db_uri, use_iam=False
        )

    def test_create_iam_app_production(self, agent: DBBootstrapperAgent):
        """Test IAM app creation for production."""
        agent.local_db = False
        agent.app_factory.create_app = Mock()

        agent.create_iam_app("iam_user")

        expected_db_uri = DbUri(
            hostname=agent.host,
            port=agent.port,
            database=agent.database,
            username="iam_user",
        )
        agent.app_factory.create_app.assert_called_once_with(
            expected_db_uri, use_iam=True
        )

    def test_create_db_manager(self, agent: DBBootstrapperAgent):
        """Test database manager creation."""
        app = agent.create_master_app("test_password")
        db_manager = agent.create_db_manager(app)
        assert isinstance(db_manager, DatabaseManager)

    def test_create_data_loader(self, agent: DBBootstrapperAgent):
        """Test data loader creation."""
        app = agent.create_master_app("test_password")
        data_loader = agent.create_data_loader(app)
        assert isinstance(data_loader, DataLoader)

    def test_handle_create_request_success(self, agent: DBBootstrapperAgent):
        """Test successful Create request handling."""
        mock_app = Mock()
        mock_iam_app = Mock()
        mock_db_manager = Mock()
        mock_db_manager.s3_file_manager = Mock()
        mock_db_manager.s3_file_manager.download_file = Mock()
        mock_db_manager.upgrade_database = Mock()
        mock_db_manager.setup_iam_database_user = Mock()
        mock_db_manager.test_iam_connection = Mock()
        mock_data_loader = Mock()

        agent.validate_environment = Mock()
        agent.get_database_secret = Mock(
            return_value={"password": POSTGRES_PASSWORD}
        )
        agent.create_master_app = Mock(return_value=mock_app)
        agent.create_iam_app = Mock(return_value=mock_iam_app)
        agent.create_db_manager = Mock(return_value=mock_db_manager)
        agent.create_data_loader = Mock(return_value=mock_data_loader)

        result = agent.handle_create_request()

        # Check the return value
        assert result["Data"] == DBBootstrapperAgentMessage.create_success()

        # Check the calls
        agent.validate_environment.assert_called_once()
        agent.get_database_secret.assert_called_once()
        agent.create_master_app.assert_called_once_with(POSTGRES_PASSWORD)

        assert agent.create_db_manager.call_count == 2
        assert agent.create_db_manager.call_args_list[0][0][0] == mock_app
        assert agent.create_db_manager.call_args_list[1][0][0] == mock_iam_app

        mock_db_manager.upgrade_database.assert_called_once()
        mock_db_manager.setup_iam_database_user.assert_called_once_with(
            IAM_USERNAME
        )
        agent.create_iam_app.assert_called_once_with(IAM_USERNAME)
        mock_db_manager.test_iam_connection.assert_called_once()

        # No data loading if no data ARN is provided
        mock_db_manager.s3_file_manager.download_file.assert_not_called()
        agent.create_data_loader.assert_not_called()
        mock_data_loader.load_data.assert_not_called()

    def test_handle_create_request_with_data(
        self,
        agent: DBBootstrapperAgent,
    ):
        """Test successful Create request handling."""
        mock_app = Mock()
        mock_iam_app = Mock()
        mock_db_manager = Mock()

        mock_filename = "filename.json"
        agent.s3_file_manager = Mock()
        agent.s3_file_manager.download_file = Mock(return_value=mock_filename)
        mock_db_manager.upgrade_database = Mock()
        mock_db_manager.setup_iam_database_user = Mock()
        mock_db_manager.test_iam_connection = Mock()
        mock_data_loader = Mock()
        mock_data_loader.load_data = Mock()

        agent.data_arn = MOCK_DATA_ARN
        agent.validate_environment = Mock()
        agent.get_database_secret = Mock(
            return_value={"password": POSTGRES_PASSWORD}
        )
        agent.create_master_app = Mock(return_value=mock_app)
        agent.create_iam_app = Mock(return_value=mock_iam_app)
        agent.create_db_manager = Mock(return_value=mock_db_manager)
        agent.create_data_loader = Mock(return_value=mock_data_loader)

        result = agent.handle_create_request()

        # Check the return value
        assert result["Data"] == DBBootstrapperAgentMessage.create_success()

        # Check the calls
        agent.validate_environment.assert_called_once()
        agent.get_database_secret.assert_called_once()
        agent.create_master_app.assert_called_once_with(POSTGRES_PASSWORD)

        assert agent.create_db_manager.call_count == 2
        assert agent.create_db_manager.call_args_list[0][0][0] == mock_app
        assert agent.create_db_manager.call_args_list[1][0][0] == mock_iam_app

        mock_db_manager.upgrade_database.assert_called_once()
        mock_db_manager.setup_iam_database_user.assert_called_once_with(
            IAM_USERNAME
        )
        agent.create_iam_app.assert_called_once_with(IAM_USERNAME)
        mock_db_manager.test_iam_connection.assert_called_once()

        # Data loading if data ARN is provided
        agent.s3_file_manager.download_file.assert_called_once_with(
            MOCK_DATA_ARN, DBBootstrapperAgent.data_file
        )
        agent.create_data_loader.assert_called_once_with(mock_iam_app)
        mock_data_loader.load_data.assert_called_once_with(mock_filename)

    def test_handle_create_request_error(self, agent: DBBootstrapperAgent):
        """Test error handling for Create request."""
        agent.validate_environment = Mock(side_effect=ValueError("Test error"))
        result = agent.handle_create_request()
        assert result["Data"] == DBBootstrapperAgentMessage.create_error(
            "Test error"
        )

    def test_handle_update_request_success(self, agent: DBBootstrapperAgent):
        """Test successful Update request handling."""
        mock_app = Mock()
        mock_db_manager = Mock()
        agent.validate_environment = Mock()
        agent.get_database_secret = Mock(
            return_value={"password": POSTGRES_PASSWORD}
        )
        agent.create_master_app = Mock(return_value=mock_app)
        agent.create_db_manager = Mock(return_value=mock_db_manager)

        result = agent.handle_update_request()

        agent.validate_environment.assert_called_once()
        agent.get_database_secret.assert_called_once()
        agent.create_master_app.assert_called_once_with(POSTGRES_PASSWORD)
        agent.create_db_manager.assert_called_once_with(mock_app)
        mock_db_manager.upgrade_database.assert_called_once()
        assert result["Data"] == DBBootstrapperAgentMessage.update_success()

    def test_handle_update_request_error(self, agent: DBBootstrapperAgent):
        """Test error handling for Update request."""
        agent.validate_environment = Mock(side_effect=ValueError("Test error"))
        result = agent.handle_update_request()
        assert result["Data"] == DBBootstrapperAgentMessage.update_error(
            "Test error"
        )

    def test_handle_delete_request(self, agent: DBBootstrapperAgent):
        """Test Delete request handling."""
        result = agent.handle_delete_request()

        assert result["Data"] == DBBootstrapperAgentMessage.delete_success()

    def test_handle_request_create(self, agent: DBBootstrapperAgent):
        """Test request handling for Create type."""
        event = {"RequestType": "Create"}
        agent.handle_create_request = Mock(return_value={"Data": "Success"})

        result = agent.handle_request(event)

        assert result["Data"] == "Success"
        agent.handle_create_request.assert_called_once()

    def test_handle_request_update(self, agent: DBBootstrapperAgent):
        """Test request handling for Update type."""
        event = {"RequestType": "Update"}
        agent.handle_update_request = Mock(return_value={"Data": "Success"})

        result = agent.handle_request(event)

        assert result["Data"] == "Success"
        agent.handle_update_request.assert_called_once()

    def test_handle_request_delete(self, agent: DBBootstrapperAgent):
        """Test request handling for Delete type."""
        event = {"RequestType": "Delete"}

        result = agent.handle_request(event)

        assert result["Data"] == DBBootstrapperAgentMessage.delete_success()

    def test_handle_request_unknown_type(self, agent: DBBootstrapperAgent):
        """Test request handling for unknown type."""
        event = {"RequestType": "Unknown"}
        with pytest.raises(ValueError, match="Unknown request type: Unknown"):
            agent.handle_request(event)


class TestDBBootstrapperAgentIntegration:
    """Integration tests for DBBootstrapperAgent."""

    def test_integration_create_request(
        self,
        agent: DBBootstrapperAgent,
        mock_migrations_dir: str,
    ):
        """Test integration of Create request."""
        agent.local_db = True
        event = {"RequestType": "Create"}
        result = agent.handle_request(event)

        # Assert success message is returned
        assert result["Data"] == DBBootstrapperAgentMessage.create_success()

        # Assert tables are created
        result = db.session.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        )
        assert set(result.fetchall()) == {
            ("alembic_version",),
            ("mock_table",),
            ("empty_table",),
        }

        # Assert IAM user is created
        result = db.session.execute(
            text("SELECT rolname FROM pg_roles WHERE rolname = :iam_username"),
            {"iam_username": IAM_USERNAME},
        )
        assert result.fetchone() == (IAM_USERNAME,)

    def test_integration_update_request(
        self,
        agent: DBBootstrapperAgent,
        test_client: Flask,
        mock_migrations_dir: str,
    ):
        """Test integration of Update request."""
        agent.local_db = True
        sql = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{MOCK_EMPTY_TABLE_NAME}'"  # noqa: S608

        # Perform a create request to create the tables
        event = {"RequestType": "Create"}
        result = agent.handle_request(event)
        assert result["Data"] == DBBootstrapperAgentMessage.create_success()

        # Get column names of empty_table
        result = db.session.execute(text(sql))
        assert set(result.fetchall()) == {
            ("id",),
            ("name",),
            ("description",),
        }

        # Add a new column to the MockEmptyTable class
        MockEmptyTable.new_column = db.Column(db.String(255), nullable=True)
        migrate(mock_migrations_dir)

        # Perform an update request to add the new table
        event = {"RequestType": "Update"}
        result = agent.handle_request(event)

        # Assert success message is returned
        assert result["Data"] == DBBootstrapperAgentMessage.update_success()

        # Assert the new column is added
        result = db.session.execute(text(sql))
        assert set(result.fetchall()) == {
            ("id",),
            ("name",),
            ("description",),
            ("new_column",),
        }
