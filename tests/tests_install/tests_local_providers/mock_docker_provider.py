# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest.mock import MagicMock

from install.local_providers import DockerProvider
from tests.tests_install.tests_local_providers.mock_env_file_provider import (
    env_file_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


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
        env_file_provider=env_file_provider(),
    )
    provider.docker_client = docker_client()
    return provider
