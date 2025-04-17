from unittest.mock import MagicMock

from install.local_providers import DockerProvider
from tests.tests_install.tests_utils.mock_logger import logger
from tests.tests_install.tests_project_config.mock_project_config_provider import project_config_provider


def container():
    container = MagicMock()
    container.exec_run = MagicMock()
    container.stop = MagicMock()
    container.remove = MagicMock()
    return container


def network():
    network = MagicMock()
    network.remove = MagicMock()
    return network


def docker_client():
    client = MagicMock()
    client.networks.create = MagicMock()
    client.containers.run = MagicMock()
    client.containers.get = MagicMock()
    client.containers.get.return_value = container()
    client.images.build = MagicMock()
    client.networks.get = MagicMock()
    client.networks.get.return_value = network()
    return client


def docker_provider():
    provider = DockerProvider(
        logger=logger(),
        config=project_config_provider(),
    )
    provider.docker_client = docker_client()
    return provider
