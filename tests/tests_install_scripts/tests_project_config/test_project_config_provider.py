import json
import os
import sys
from unittest.mock import patch, MagicMock, mock_open

import pytest

from install_scripts.project_config.project_config_provider import ProjectConfigProvider
from install_scripts.utils.enums import FString


class TestProjectConfigProvider:
    def test_init(self, logger_mock):
        """Test initialization of ProjectConfigProvider"""
        project_config_provider = ProjectConfigProvider(
            logger=logger_mock,
            project_suffix="test-project-suffix",
        )

        assert project_config_provider.logger == logger_mock
        assert project_config_provider.project_suffix == "test-project-suffix"
        assert project_config_provider.project_config is None
        assert project_config_provider.user_input is None

    def test_load_existing_config_success(self, project_config_provider_mock: ProjectConfigProvider):
        """Test loading existing config file successfully"""
        mock_config = {"project_name": "test-project"}

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=json.dumps(mock_config)))
        ):
            project_config_provider_mock.load_existing_config("test-project")

        assert project_config_provider_mock.project_config == mock_config

    def test_load_existing_config_file_not_found(self, project_config_provider_mock: ProjectConfigProvider):
        """Test loading config when file doesn't exist"""
        with (
            patch("os.path.exists", return_value=False),
            patch("sys.exit") as mock_exit
        ):
            project_config_provider_mock.load_existing_config("test-project")
            mock_exit.assert_called_once_with(1)

    def test_get_user_input_continue(self, project_config_provider_mock: ProjectConfigProvider):
        """Test get_user_input when user continues"""
        with (
            patch("builtins.input", side_effect=["y", "valid-project", "test@example.com"]),
            patch("getpass.getpass", side_effect=["client-id", "client-secret"])
        ):
            project_config_provider_mock.get_user_input()

        assert project_config_provider_mock.user_input is not None
        assert project_config_provider_mock.user_input["project_name"] == "valid-project-test-project-suffix"
        assert project_config_provider_mock.user_input["fitbit_client_id"] == "client-id"
        assert project_config_provider_mock.user_input["fitbit_client_secret"] == "client-secret"
        assert project_config_provider_mock.user_input["admin_email"] == "test@example.com"

    def test_get_user_input_cancel(self, project_config_provider_mock: ProjectConfigProvider):
        """Test get_user_input when user cancels"""
        with (
            patch("builtins.input", return_value="n"),
            patch("sys.exit") as mock_exit
        ):
            project_config_provider_mock.get_user_input()
            mock_exit.assert_called_once_with(1)

    def test_get_user_input_invalid_project_name(self, project_config_provider_mock: ProjectConfigProvider):
        """Test get_user_input with invalid project name"""
        with (
            patch("builtins.input", side_effect=["y", "", "valid-project", "test@example.com"]),
            patch("getpass.getpass", side_effect=["client-id", "client-secret"])
        ):
            project_config_provider_mock.get_user_input()

        assert project_config_provider_mock.user_input["project_name"] == "valid-project-test-project-suffix"

    def test_get_user_input_invalid_email(self, project_config_provider_mock: ProjectConfigProvider):
        """Test get_user_input with invalid email"""
        with (
            patch("builtins.input", side_effect=["y", "valid-project", "", "test@example.com"]),
            patch("getpass.getpass", side_effect=["client-id", "client-secret"])
        ):
            project_config_provider_mock.get_user_input()

        assert project_config_provider_mock.user_input["admin_email"] == "test@example.com"

    def test_setup_project_config(self, project_config_provider_mock: ProjectConfigProvider):
        """Test setup_project_config"""
        # Set up user_input first
        project_config_provider_mock.user_input = {
            "project_name": "test-project",
            "admin_email": "test@example.com"
        }

        project_config_provider_mock.setup_project_config()

        assert project_config_provider_mock.project_config is not None
        assert project_config_provider_mock.project_config["project_name"] == "test-project"
        assert project_config_provider_mock.project_config["admin_email"] == "test@example.com"
        assert "aws" in project_config_provider_mock.project_config
        assert "docker" in project_config_provider_mock.project_config

    def test_format_string(self, project_config_provider_mock: ProjectConfigProvider):
        """Test format_string method"""
        project_config_provider_mock.user_input = {
            "project_name": "test-project"
        }

        result = project_config_provider_mock.format_string("prefix-{project_name}-suffix")
        assert result == "prefix-test-project-suffix"

    def test_write_project_config(self, project_config_provider_mock: ProjectConfigProvider):
        """Test write_project_config method"""
        project_config_provider_mock.user_input = {
            "project_name": "test-project"
        }
        project_config_provider_mock.project_config = {"test": "data"}

        with patch("builtins.open", mock_open()) as mock_file:
            project_config_provider_mock.write_project_config()

        mock_file.assert_called_once()
        # Check that json.dump was called with the correct arguments
        with patch("json.dump") as mock_json_dump:
            project_config_provider_mock.write_project_config()
            mock_json_dump.assert_called_once_with(
                {"test": "data"},
                mock_file.return_value.__enter__.return_value,
                indent=4
            )

    def test_uninstall(self, project_config_provider_mock: ProjectConfigProvider):
        """Test uninstall method"""
        project_config_provider_mock.user_input = {
            "project_name": "test-project"
        }

        with patch("os.remove") as mock_remove:
            project_config_provider_mock.uninstall()

        mock_remove.assert_called_once()

    def test_property_getters_and_setters(self, project_config_provider_mock: ProjectConfigProvider):
        """Test property getters and setters"""
        # Set up project_config
        project_config_provider_mock.project_config = {
            "project_name": "test-project",
            "aws": {
                "cognito": {
                    "participant_user_pool_name": "participant-pool",
                    "participant_user_pool_domain": "participant-domain",
                    "participant_user_pool_id": "participant-id",
                    "participant_client_id": "participant-client",
                    "researcher_user_pool_name": "researcher-pool",
                    "researcher_user_pool_domain": "researcher-domain",
                    "researcher_user_pool_id": "researcher-id",
                    "researcher_client_id": "researcher-client"
                },
                "s3": {
                    "logs_bucket_name": "logs-bucket",
                    "audio_bucket_name": "audio-bucket"
                },
                "secrets_manager": {
                    "secret_name": "secret",
                    "tokens_secret_name": "tokens-secret"
                },
                "stack_name": "stack"
            },
            "docker": {
                "network_name": "network",
                "postgres_container_name": "postgres",
                "wearable_data_retrieval_container_name": "wearable"
            }
        }

        # Set up user_input
        project_config_provider_mock.user_input = {
            "admin_email": "admin@example.com",
            "fitbit_client_id": "fitbit-id",
            "fitbit_client_secret": "fitbit-secret"
        }

        # Test getters
        assert project_config_provider_mock.admin_email == "admin@example.com"
        assert project_config_provider_mock.fitbit_client_id == "fitbit-id"
        assert project_config_provider_mock.fitbit_client_secret == "fitbit-secret"
        assert project_config_provider_mock.project_name == "test-project"
        assert project_config_provider_mock.participant_user_pool_name == "participant-pool"
        assert project_config_provider_mock.participant_user_pool_domain == "participant-domain"
        assert project_config_provider_mock.participant_user_pool_id == "participant-id"
        assert project_config_provider_mock.participant_client_id == "participant-client"
        assert project_config_provider_mock.researcher_user_pool_name == "researcher-pool"
        assert project_config_provider_mock.researcher_user_pool_domain == "researcher-domain"
        assert project_config_provider_mock.researcher_user_pool_id == "researcher-id"
        assert project_config_provider_mock.researcher_client_id == "researcher-client"
        assert project_config_provider_mock.logs_bucket_name == "logs-bucket"
        assert project_config_provider_mock.audio_bucket_name == "audio-bucket"
        assert project_config_provider_mock.secret_name == "secret"
        assert project_config_provider_mock.tokens_secret_name == "tokens-secret"
        assert project_config_provider_mock.stack_name == "stack"
        assert project_config_provider_mock.network_name == "network"
        assert project_config_provider_mock.postgres_container_name == "postgres"
        assert project_config_provider_mock.wearable_data_retrieval_container_name == "wearable"

        # Test setters with write_project_config mocked
        with patch.object(project_config_provider_mock, 'write_project_config') as mock_write:
            project_config_provider_mock.project_name = "new-project"
            assert project_config_provider_mock.project_config["project_name"] == "new-project"
            mock_write.assert_called_once()

            mock_write.reset_mock()
            project_config_provider_mock.participant_user_pool_name = "new-pool"
            assert project_config_provider_mock.project_config["aws"]["cognito"]["participant_user_pool_name"] == "new-pool"
            mock_write.assert_called_once()

            # Test more setters...
            mock_write.reset_mock()
            project_config_provider_mock.logs_bucket_name = "new-bucket"
            assert project_config_provider_mock.project_config["aws"]["s3"]["logs_bucket_name"] == "new-bucket"
            mock_write.assert_called_once()
