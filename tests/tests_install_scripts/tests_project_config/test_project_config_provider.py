import json
from unittest.mock import patch, MagicMock, mock_open

import pytest

from install_scripts.project_config.project_config_provider import ProjectConfigProvider
from install_scripts.project_config.project_config_types import UserInput, ProjectConfig
from install_scripts.utils.exceptions import ProjectConfigError, CancelInstallation
from tests.tests_install_scripts.tests_utils.mock_logger import logger
from tests.tests_install_scripts.tests_project_config.mock_project_config_provider import project_config_provider, user_input, project_config


@pytest.fixture
def logger_mock():
    return logger()


@pytest.fixture
def user_input_mock():
    return user_input()


@pytest.fixture
def project_config_mock():
    return project_config()


@pytest.fixture
def project_config_provider_mock():
    return project_config_provider()


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
            pytest.raises(ProjectConfigError)
        ):
            project_config_provider_mock.load_existing_config("test-project")

    def test_get_user_input_continue(self, project_config_provider_mock: ProjectConfigProvider):
        """Test get_user_input when user continues"""
        with (
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_continue_input", return_value="y"),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_project_name_input", return_value="valid-project"),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_fitbit_credentials_input", return_value=("client-id", "client-secret")),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_admin_email_input", return_value="test@example.com")
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
            pytest.raises(CancelInstallation)
        ):
            project_config_provider_mock.get_user_input()


    def test_get_user_input_invalid_project_name(self, project_config_provider_mock: ProjectConfigProvider):
        """Test get_user_input with invalid project name"""
        with (
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_continue_input", return_value="y"),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_project_name_input", side_effect=["", "valid-project"]),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_fitbit_credentials_input", return_value=("client-id", "client-secret")),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_admin_email_input", return_value="test@example.com")
        ):
            project_config_provider_mock.get_user_input()

        assert project_config_provider_mock.user_input["project_name"] == "valid-project-test-project-suffix"

    def test_get_user_input_invalid_email(self, project_config_provider_mock: ProjectConfigProvider):
        """Test get_user_input with invalid email"""
        with (
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_continue_input", return_value="y"),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_project_name_input", return_value="valid-project"),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_fitbit_credentials_input", return_value=("client-id", "client-secret")),
            patch("install_scripts.project_config.project_config_provider.ProjectConfigProvider.get_admin_email_input", side_effect=["", "test@example.com"])
        ):
            project_config_provider_mock.get_user_input()

        assert project_config_provider_mock.user_input["admin_email"] == "test@example.com"

    def test_setup_project_config(self, user_input_mock: UserInput, project_config_mock: ProjectConfig):
        """Test setup_project_config"""
        # Create a mock project config provider
        project_config_provider_mock = ProjectConfigProvider(
            logger=MagicMock(),
            project_suffix="test-project-suffix",
        )

        project_config_provider_mock.user_input = user_input_mock
        project_config_provider_mock.setup_project_config()

        assert project_config_provider_mock.project_config is not None
        assert project_config_provider_mock.project_config == project_config_mock

    def test_format_string(self, project_config_provider_mock: ProjectConfigProvider):
        """Test format_string method"""
        result = project_config_provider_mock.format_string("prefix-{project_name}-suffix")
        assert result == f"prefix-{project_config_provider_mock.project_name}-suffix"

    def test_write_project_config(self, project_config_provider_mock: ProjectConfigProvider):
        """Test write_project_config method"""
        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("json.dump") as mock_json_dump
        ):
            project_config_provider_mock.write_project_config()

            mock_file.assert_called_once_with(
                f"project-config-{project_config_provider_mock.project_name}.json",
                "w"
            )
            mock_json_dump.assert_called_once_with(
                project_config_provider_mock.project_config,
                mock_file.return_value.__enter__.return_value,
                indent=4
            )

    def test_uninstall(self, project_config_provider_mock: ProjectConfigProvider):
        """Test uninstall method"""
        with (
            patch("os.remove") as mock_remove,
            patch("os.path.exists", return_value=True)
        ):
            project_config_provider_mock.uninstall()

            mock_remove.assert_called_once_with(
                f"project-config-{project_config_provider_mock.project_name}.json"
            )

    def test_property_getters_and_setters(self, project_config_provider_mock: ProjectConfigProvider, project_config_mock: ProjectConfig, user_input_mock: UserInput):
        """Test property getters and setters"""

        # Test getters
        assert project_config_provider_mock.admin_email == user_input_mock["admin_email"]
        assert project_config_provider_mock.fitbit_client_id == user_input_mock["fitbit_client_id"]
        assert project_config_provider_mock.fitbit_client_secret == user_input_mock["fitbit_client_secret"]
        assert project_config_provider_mock.project_name == user_input_mock["project_name"]
        assert project_config_provider_mock.participant_user_pool_name == project_config_mock["aws"]["cognito"]["participant_user_pool_name"]
        assert project_config_provider_mock.participant_user_pool_domain == project_config_mock["aws"]["cognito"]["participant_user_pool_domain"]
        assert project_config_provider_mock.participant_user_pool_id == project_config_mock["aws"]["cognito"]["participant_user_pool_id"]
        assert project_config_provider_mock.participant_client_id == project_config_mock["aws"]["cognito"]["participant_client_id"]
        assert project_config_provider_mock.researcher_user_pool_name == project_config_mock["aws"]["cognito"]["researcher_user_pool_name"]
        assert project_config_provider_mock.researcher_user_pool_domain == project_config_mock["aws"]["cognito"]["researcher_user_pool_domain"]
        assert project_config_provider_mock.researcher_user_pool_id == project_config_mock["aws"]["cognito"]["researcher_user_pool_id"]
        assert project_config_provider_mock.researcher_client_id == project_config_mock["aws"]["cognito"]["researcher_client_id"]
        assert project_config_provider_mock.logs_bucket_name == project_config_mock["aws"]["s3"]["logs_bucket_name"]
        assert project_config_provider_mock.audio_bucket_name == project_config_mock["aws"]["s3"]["audio_bucket_name"]
        assert project_config_provider_mock.secret_name == project_config_mock["aws"]["secrets_manager"]["secret_name"]
        assert project_config_provider_mock.tokens_secret_name == project_config_mock["aws"]["secrets_manager"]["tokens_secret_name"]
        assert project_config_provider_mock.stack_name == project_config_mock["aws"]["stack_name"]
        assert project_config_provider_mock.network_name == project_config_mock["docker"]["network_name"]
        assert project_config_provider_mock.postgres_container_name == project_config_mock["docker"]["postgres_container_name"]
        assert project_config_provider_mock.wearable_data_retrieval_container_name == project_config_mock["docker"]["wearable_data_retrieval_container_name"]

        # Test setters with write_project_config mocked
        with patch.object(project_config_provider_mock, "write_project_config") as mock_write:
            project_config_provider_mock.project_name = "new-project"
            assert project_config_provider_mock.project_config["project_name"] == "new-project"
            mock_write.assert_called_once()

            mock_write.reset_mock()
            project_config_provider_mock.participant_user_pool_name = "new-pool"
            assert project_config_provider_mock.project_config["aws"]["cognito"]["participant_user_pool_name"] == "new-pool"
            mock_write.assert_called_once()

            mock_write.reset_mock()
            project_config_provider_mock.logs_bucket_name = "new-bucket"
            assert project_config_provider_mock.project_config["aws"]["s3"]["logs_bucket_name"] == "new-bucket"
            mock_write.assert_called_once()
