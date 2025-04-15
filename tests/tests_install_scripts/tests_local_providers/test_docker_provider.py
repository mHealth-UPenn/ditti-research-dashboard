import subprocess
from unittest.mock import patch, MagicMock

import docker
import pytest

from tests.tests_install_scripts.tests_local_providers.mock_docker_provider import docker_provider
from install_scripts.utils.exceptions import DockerSDKError, SubprocessError
from install_scripts.local_providers.docker_provider import DockerProvider
from install_scripts.utils.enums import Postgres


@pytest.fixture
def docker_provider_mock():
    return docker_provider()


@pytest.fixture
def shutil_mock():
    with (
        patch("shutil.copytree") as mock_copytree,
        patch("shutil.rmtree") as mock_rmtree,
    ):
        yield mock_copytree, mock_rmtree


@pytest.fixture
def subprocess_mock():
    with patch("subprocess.run") as mock_run:
        yield mock_run


class TestDockerProvider:
    def test_setup(self, docker_provider_mock: DockerProvider):
        """Test the setup method calls all required methods."""
        docker_provider_mock.create_network = MagicMock()
        docker_provider_mock.run_postgres_container = MagicMock()
        docker_provider_mock.initialize_database = MagicMock()
        docker_provider_mock.build_wearable_data_retrieval_container = MagicMock()
        docker_provider_mock.run_wearable_data_retrieval_container = MagicMock()

        docker_provider_mock.setup()

        docker_provider_mock.create_network.assert_called_once()
        docker_provider_mock.run_postgres_container.assert_called_once()
        docker_provider_mock.initialize_database.assert_called_once()
        docker_provider_mock.build_wearable_data_retrieval_container.assert_called_once()
        docker_provider_mock.run_wearable_data_retrieval_container.assert_called_once()

    def test_create_network_success(self, docker_provider_mock: DockerProvider):
        """Test successful creation of Docker network."""
        docker_provider_mock.create_network()
        docker_provider_mock.docker_client.networks.create.assert_called_once_with(
            docker_provider_mock.settings.network_name
        )

    def test_create_network_api_error(self, docker_provider_mock: DockerProvider):
        """Test handling of APIError when creating Docker network."""
        docker_provider_mock.docker_client.networks.create.side_effect = docker.errors.APIError("API Error")

        with pytest.raises(DockerSDKError):
            docker_provider_mock.create_network()

    def test_run_postgres_container_success(self, docker_provider_mock: DockerProvider):
        """Test successful creation of Postgres container."""
        # Mock the container's exec_run method to return a successful response
        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(
            exit_code=0,
            output=b"accepting connections"
        )
        docker_provider_mock.get_container = MagicMock(return_value=mock_container)

        docker_provider_mock.run_postgres_container()

        docker_provider_mock.docker_client.containers.run.assert_called_once()

        # Verify the container is created with the correct parameters
        call_args = docker_provider_mock.docker_client.containers.run.call_args[1]
        assert call_args["image"] == "postgres"
        assert call_args["name"] == docker_provider_mock.settings.postgres_container_name
        assert "POSTGRES_USER" in call_args["environment"]
        assert "POSTGRES_PASSWORD" in call_args["environment"]
        assert "POSTGRES_DB" in call_args["environment"]
        assert call_args["network"] == docker_provider_mock.settings.network_name

        # Verify that get_container was called
        docker_provider_mock.get_container.assert_called_with(
            docker_provider_mock.settings.postgres_container_name
        )

        # Verify that exec_run was called with the correct arguments
        mock_container.exec_run.assert_called_with([
            "pg_isready",
            "-U", Postgres.USER,
            "-d", Postgres.DB
        ])

    def test_run_postgres_container_error(self, docker_provider_mock: DockerProvider):
        """Test handling of error when creating Postgres container."""
        docker_provider_mock.docker_client.containers.run.side_effect = docker.errors.ContainerError("Container Error", "exit_status", "command", "image", "stderr")

        with pytest.raises(DockerSDKError):
            docker_provider_mock.run_postgres_container()

    def test_initialize_database_success(self, docker_provider_mock: DockerProvider, subprocess_mock: MagicMock):
        """Test successful database initialization."""
        subprocess_mock.return_value = MagicMock(returncode=0)

        docker_provider_mock.initialize_database()

        # Verify that subprocess.run was called three times with the correct arguments
        assert subprocess_mock.call_count == 3

        # Check first call (db upgrade)
        first_call = subprocess_mock.call_args_list[0]
        assert first_call[0][0] == ["flask", "--app", "run.py", "db", "upgrade"]
        assert first_call[1]["check"] is True

        # Check second call (init-integration-testing-db)
        second_call = subprocess_mock.call_args_list[1]
        assert second_call[0][0] == ["flask", "--app", "run.py", "init-integration-testing-db"]
        assert second_call[1]["check"] is True

        # Check third call (create-researcher-account)
        third_call = subprocess_mock.call_args_list[2]
        assert third_call[0][0] == ["flask", "--app", "run.py", "create-researcher-account", "--email", docker_provider_mock.settings.admin_email]
        assert third_call[1]["check"] is True

    def test_initialize_database_subprocess_error(self, docker_provider_mock: DockerProvider, subprocess_mock: MagicMock):
        """Test handling of subprocess error during database initialization."""
        subprocess_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["flask", "--app", "run.py", "db", "upgrade"], output=b"Subprocess Error")

        with pytest.raises(SubprocessError):
            docker_provider_mock.initialize_database()

    def test_initialize_database_unexpected_error(self, docker_provider_mock: DockerProvider, subprocess_mock: MagicMock):
        """Test handling of unexpected error during database initialization."""
        subprocess_mock.side_effect = Exception("Unexpected Error")

        with pytest.raises(Exception):
            docker_provider_mock.initialize_database()

    def test_build_wearable_data_retrieval_container_success(self, docker_provider_mock: DockerProvider, shutil_mock: MagicMock):
        """Test successful building of wearable data retrieval container."""
        mock_copytree, mock_rmtree = shutil_mock

        docker_provider_mock.build_wearable_data_retrieval_container()

        # Verify that copytree was called with the correct arguments
        mock_copytree.assert_called_once_with("shared", "functions/wearable_data_retrieval/shared")

        # Verify that docker_client.images.build was called with the correct arguments
        docker_provider_mock.docker_client.images.build.assert_called_once()
        call_args = docker_provider_mock.docker_client.images.build.call_args[1]
        assert call_args["path"] == "functions/wearable_data_retrieval"
        assert call_args["tag"] == docker_provider_mock.settings.wearable_data_retrieval_container_name
        assert call_args["platform"] == "linux/amd64"

        # Verify that rmtree was called with the correct arguments
        mock_rmtree.assert_called_once_with("functions/wearable_data_retrieval/shared")

    def test_build_wearable_data_retrieval_build_error(self, docker_provider_mock: DockerProvider, shutil_mock: MagicMock):
        """Test handling of error when building wearable data retrieval container."""
        mock_copytree, _ = shutil_mock
        mock_copytree.side_effect = docker.errors.BuildError("Build Error", "stderr")

        with pytest.raises(Exception):
            docker_provider_mock.build_wearable_data_retrieval_container()

    def test_build_wearable_data_retrieval_unexpected_error(self, docker_provider_mock: DockerProvider, shutil_mock: MagicMock):
        """Test handling of unexpected error when building wearable data retrieval container."""
        mock_copytree, _ = shutil_mock
        mock_copytree.side_effect = Exception("Unexpected Error")

        with pytest.raises(Exception):
            docker_provider_mock.build_wearable_data_retrieval_container()

    def test_run_wearable_data_retrieval_container_success(self, docker_provider_mock: DockerProvider):
        """Test successful running of wearable data retrieval container."""
        docker_provider_mock.run_wearable_data_retrieval_container()

        docker_provider_mock.docker_client.containers.run.assert_called_once()
        call_args = docker_provider_mock.docker_client.containers.run.call_args[1]
        assert call_args["image"] == docker_provider_mock.settings.wearable_data_retrieval_container_name
        assert call_args["name"] == docker_provider_mock.settings.wearable_data_retrieval_container_name
        assert call_args["platform"] == "linux/amd64"
        assert call_args["network"] == docker_provider_mock.settings.network_name
        assert call_args["ports"] == {"9000": 8080}
        assert call_args["environment"] == {"TESTING": "true"}
        assert call_args["detach"] is True

    def test_run_wearable_data_retrieval_container_error(self, docker_provider_mock: DockerProvider):
        """Test handling of error when running wearable data retrieval container."""
        docker_provider_mock.docker_client.containers.run.side_effect = docker.errors.ContainerError("Container Error", "exit_status", "command", "image", "stderr")

        with pytest.raises(DockerSDKError):
            docker_provider_mock.run_wearable_data_retrieval_container()

    def test_run_wearable_data_retrieval_unexpected_error(self, docker_provider_mock: DockerProvider):
        """Test handling of unexpected error when running wearable data retrieval container."""
        docker_provider_mock.docker_client.containers.run.side_effect = Exception("Unexpected Error")

        with pytest.raises(Exception):
            docker_provider_mock.run_wearable_data_retrieval_container()

    def test_get_container_success(self, docker_provider_mock: DockerProvider):
        """Test successful retrieval of a container."""
        result = docker_provider_mock.get_container("test-container")

        assert result == docker_provider_mock.docker_client.containers.get.return_value
        docker_provider_mock.docker_client.containers.get.assert_called_once_with("test-container")

    def test_get_container_not_found(self, docker_provider_mock: DockerProvider):
        """Test handling of NotFoundError when getting a container."""
        docker_provider_mock.docker_client.containers.get.side_effect = docker.errors.NotFound("Container not found")

        with pytest.raises(DockerSDKError) as excinfo:
            docker_provider_mock.get_container("test-container")

    def test_get_network_success(self, docker_provider_mock: DockerProvider):
        """Test successful retrieval of a network."""
        result = docker_provider_mock.get_network()

        assert result == docker_provider_mock.docker_client.networks.get.return_value
        docker_provider_mock.docker_client.networks.get.assert_called_once_with(
            docker_provider_mock.settings.network_name
        )

    def test_get_network_not_found(self, docker_provider_mock: DockerProvider):
        """Test handling of NotFoundError when getting a network."""
        docker_provider_mock.docker_client.networks.get.side_effect = docker.errors.NotFound("Network not found")

        with pytest.raises(DockerSDKError):
            docker_provider_mock.get_network()

    def test_uninstall_success(self, docker_provider_mock: DockerProvider):
        """Test successful uninstallation of Docker containers."""
        # Mock the get_container and get_network methods
        mock_postgres_container = MagicMock()
        mock_wearable_container = MagicMock()
        mock_network = MagicMock()

        docker_provider_mock.get_container = MagicMock(side_effect=[mock_postgres_container, mock_wearable_container])
        docker_provider_mock.get_network = MagicMock(return_value=mock_network)

        docker_provider_mock.uninstall()

        # Verify that get_container was called for both containers
        docker_provider_mock.get_container.assert_any_call(docker_provider_mock.settings.postgres_container_name)
        docker_provider_mock.get_container.assert_any_call(docker_provider_mock.settings.wearable_data_retrieval_container_name)

        # Verify that containers were stopped and removed
        mock_postgres_container.stop.assert_called_once()
        mock_postgres_container.remove.assert_called_once()
        mock_wearable_container.stop.assert_called_once()
        mock_wearable_container.remove.assert_called_once()

        # Verify that get_network was called
        docker_provider_mock.get_network.assert_called_once()

        # Verify that network was removed
        mock_network.remove.assert_called_once()

    def test_uninstall_not_found(self, docker_provider_mock: DockerProvider):
        """Test handling of NotFoundError during uninstallation of containers."""
        docker_provider_mock.get_container = MagicMock(side_effect=[DockerSDKError("Container not found"), DockerSDKError("Container not found")])
        docker_provider_mock.get_network = MagicMock(side_effect=DockerSDKError("Network not found"))

        docker_provider_mock.uninstall()

        # Verify that all containers and network were attempted to be removed
        docker_provider_mock.get_container.assert_any_call(docker_provider_mock.settings.postgres_container_name)
        docker_provider_mock.get_container.assert_any_call(docker_provider_mock.settings.wearable_data_retrieval_container_name)
        docker_provider_mock.get_network.assert_called_once()
