from unittest.mock import patch, MagicMock

import docker
import pytest

from tests.tests_install.tests_local_providers.mock_docker_provider import docker_provider
from install.utils.exceptions import DockerSDKError, LocalProviderError
from install.local_providers.docker_provider import DockerProvider
from install.utils.enums import Postgres


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


def test_create_network_success(docker_provider_mock: DockerProvider):
    """Test successful creation of Docker network."""
    docker_provider_mock.create_network()
    docker_provider_mock.docker_client.networks.create.assert_called_once_with(
        docker_provider_mock.config.network_name
    )


def test_create_network_api_error(docker_provider_mock: DockerProvider):
    """Test handling of APIError when creating Docker network."""
    docker_provider_mock.docker_client.networks.create.side_effect = docker.errors.APIError("API Error")

    with pytest.raises(DockerSDKError, match="API Error"):
        docker_provider_mock.create_network()


def test_run_postgres_container_success(docker_provider_mock: DockerProvider):
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
    assert call_args["name"] == docker_provider_mock.config.postgres_container_name
    assert "POSTGRES_USER" in call_args["environment"]
    assert "POSTGRES_PASSWORD" in call_args["environment"]
    assert "POSTGRES_DB" in call_args["environment"]
    assert call_args["network"] == docker_provider_mock.config.network_name

    # Verify that get_container was called
    docker_provider_mock.get_container.assert_called_with(
        docker_provider_mock.config.postgres_container_name
    )

    # Verify that exec_run was called with the correct arguments
    mock_container.exec_run.assert_called_with([
        "pg_isready",
        "-U", Postgres.USER.value,
        "-d", Postgres.DB.value,
    ])


def test_run_postgres_container_error(docker_provider_mock: DockerProvider):
    """Test handling of error when creating Postgres container."""
    docker_provider_mock.docker_client.containers.run.side_effect = docker.errors.ContainerError("Container Error", "exit_status", "command", "image", "stderr")

    with pytest.raises(DockerSDKError, match="stderr"):
        docker_provider_mock.run_postgres_container()


def test_build_wearable_data_retrieval_container_success(docker_provider_mock: DockerProvider, shutil_mock: MagicMock):
    """Test successful building of wearable data retrieval container."""
    mock_copytree, mock_rmtree = shutil_mock

    docker_provider_mock.build_wearable_data_retrieval_container()

    # Verify that copytree was called with the correct arguments
    mock_copytree.assert_called_once_with("shared", "functions/wearable_data_retrieval/shared")

    # Verify that docker_client.images.build was called with the correct arguments
    docker_provider_mock.docker_client.images.build.assert_called_once()
    call_args = docker_provider_mock.docker_client.images.build.call_args[1]
    assert call_args["path"] == "functions/wearable_data_retrieval"
    assert call_args["tag"] == docker_provider_mock.config.wearable_data_retrieval_container_name
    assert call_args["platform"] == "linux/amd64"

    # Verify that rmtree was called with the correct arguments
    mock_rmtree.assert_called_once_with("functions/wearable_data_retrieval/shared")


def test_build_wearable_data_retrieval_copy_error(docker_provider_mock: DockerProvider, shutil_mock: MagicMock):
    """Test handling of error when building wearable data retrieval container."""
    mock_copytree, _ = shutil_mock
    mock_copytree.side_effect = Exception("Copy Error")

    with pytest.raises(LocalProviderError, match="Copy Error"):
        docker_provider_mock.build_wearable_data_retrieval_container()


def test_build_wearable_data_retrieval_build_error(docker_provider_mock: DockerProvider, shutil_mock: MagicMock):  # Mock shutil to avoid copying shared files
    """Test handling of unexpected error when building wearable data retrieval container."""
    docker_provider_mock.docker_client.images.build.side_effect = docker.errors.BuildError("Build Error", "stderr")

    with pytest.raises(DockerSDKError, match="Build Error"):
        docker_provider_mock.build_wearable_data_retrieval_container()


def test_build_wearable_data_retrieval_unexpected_error(docker_provider_mock: DockerProvider, shutil_mock: MagicMock):  # Mock shutil to avoid copying shared files
    """Test handling of unexpected error when building wearable data retrieval container."""
    docker_provider_mock.docker_client.images.build.side_effect = Exception("Unexpected Error")

    with pytest.raises(DockerSDKError, match="Unexpected Error"):
        docker_provider_mock.build_wearable_data_retrieval_container()


def test_run_wearable_data_retrieval_container_success(docker_provider_mock: DockerProvider):
    """Test successful running of wearable data retrieval container."""
    docker_provider_mock.run_wearable_data_retrieval_container()

    docker_provider_mock.docker_client.containers.run.assert_called_once()
    call_args = docker_provider_mock.docker_client.containers.run.call_args[1]
    assert call_args["image"] == docker_provider_mock.config.wearable_data_retrieval_container_name
    assert call_args["name"] == docker_provider_mock.config.wearable_data_retrieval_container_name
    assert call_args["platform"] == "linux/amd64"
    assert call_args["network"] == docker_provider_mock.config.network_name
    assert call_args["ports"] == {"9000": 8080}
    assert call_args["environment"] == docker_provider_mock.env_file_provider.get_wearable_data_retrieval_env()
    assert call_args["detach"] is True


def test_run_wearable_data_retrieval_container_error(docker_provider_mock: DockerProvider):
    """Test handling of error when running wearable data retrieval container."""
    docker_provider_mock.docker_client.containers.run.side_effect = docker.errors.ContainerError("Container Error", "exit_status", "command", "image", "stderr")

    with pytest.raises(DockerSDKError, match="stderr"):
        docker_provider_mock.run_wearable_data_retrieval_container()


def test_run_wearable_data_retrieval_unexpected_error(docker_provider_mock: DockerProvider):
    """Test handling of unexpected error when running wearable data retrieval container."""
    docker_provider_mock.docker_client.containers.run.side_effect = Exception("Unexpected Error")

    with pytest.raises(DockerSDKError, match="Unexpected Error"):
        docker_provider_mock.run_wearable_data_retrieval_container()


def test_get_container_success(docker_provider_mock: DockerProvider):
    """Test successful retrieval of a container."""
    result = docker_provider_mock.get_container("test-container")

    assert result == docker_provider_mock.docker_client.containers.get.return_value
    docker_provider_mock.docker_client.containers.get.assert_called_once_with("test-container")


def test_get_container_not_found(docker_provider_mock: DockerProvider):
    """Test handling of NotFoundError when getting a container."""
    docker_provider_mock.docker_client.containers.get.side_effect = docker.errors.NotFound("Container not found")

    with pytest.raises(DockerSDKError, match=f"Container .+ not found"):
        docker_provider_mock.get_container("test-container")


def test_get_network_success(docker_provider_mock: DockerProvider):
    """Test successful retrieval of a network."""
    result = docker_provider_mock.get_network()

    assert result == docker_provider_mock.docker_client.networks.get.return_value
    docker_provider_mock.docker_client.networks.get.assert_called_once_with(
        docker_provider_mock.config.network_name
    )


def test_get_network_not_found(docker_provider_mock: DockerProvider):
    """Test handling of NotFoundError when getting a network."""
    docker_provider_mock.docker_client.networks.get.side_effect = docker.errors.NotFound("Network not found")

    with pytest.raises(DockerSDKError, match=f"Network .+ not found"):
        docker_provider_mock.get_network()


def test_uninstall_success(docker_provider_mock: DockerProvider):
    """Test successful uninstallation of Docker containers."""
    # Mock the get_container and get_network methods
    mock_postgres_container = MagicMock()
    mock_wearable_container = MagicMock()
    mock_network = MagicMock()

    docker_provider_mock.get_container = MagicMock(side_effect=[mock_postgres_container, mock_wearable_container])
    docker_provider_mock.get_network = MagicMock(return_value=mock_network)

    docker_provider_mock.uninstall()

    # Verify that get_container was called for both containers
    docker_provider_mock.get_container.assert_any_call(docker_provider_mock.config.postgres_container_name)
    docker_provider_mock.get_container.assert_any_call(docker_provider_mock.config.wearable_data_retrieval_container_name)

    # Verify that containers were stopped and removed
    mock_postgres_container.stop.assert_called_once()
    mock_postgres_container.remove.assert_called_once()
    mock_wearable_container.stop.assert_called_once()
    mock_wearable_container.remove.assert_called_once()

    # Verify that get_network was called
    docker_provider_mock.get_network.assert_called_once()

    # Verify that network was removed
    mock_network.remove.assert_called_once()


def test_uninstall_not_found(docker_provider_mock: DockerProvider):
    """Test handling of NotFoundError during uninstallation of containers."""
    docker_provider_mock.get_container = MagicMock(side_effect=[DockerSDKError("Container not found"), DockerSDKError("Container not found")])
    docker_provider_mock.get_network = MagicMock(side_effect=DockerSDKError("Network not found"))

    docker_provider_mock.uninstall()

    # Verify that all containers and network were attempted to be removed
    docker_provider_mock.get_container.assert_any_call(docker_provider_mock.config.postgres_container_name)
    docker_provider_mock.get_container.assert_any_call(docker_provider_mock.config.wearable_data_retrieval_container_name)
    docker_provider_mock.get_network.assert_called_once()
