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

from unittest.mock import MagicMock, mock_open, patch

import pytest
from moto import mock_aws

from install.local_providers.env_file_provider import EnvFileProvider
from install.local_providers.local_provider_types import (
    RootEnv,
    WearableDataRetrievalEnv,
)
from tests.tests_install.tests_local_providers.mock_env_file_provider import (
    env_file_provider,
    root_env,
    wearable_data_retrieval_env,
)


@pytest.fixture
def env_file_provider_mock():
    with mock_aws():
        yield env_file_provider()


@pytest.fixture
def wearable_data_retrieval_mock(env_file_provider_mock: EnvFileProvider):
    return wearable_data_retrieval_env(env_file_provider_mock.config)


@pytest.fixture
def root_mock(env_file_provider_mock: EnvFileProvider):
    return root_env(env_file_provider_mock.config)


@pytest.fixture
def open_mock():
    with patch("builtins.open", new_callable=mock_open) as mock:
        yield mock


@pytest.fixture
def remove_mock():
    with patch("os.remove") as mock:
        yield mock


def test_get_wearable_data_retrieval_env(
    wearable_data_retrieval_mock: WearableDataRetrievalEnv,
    env_file_provider_mock: EnvFileProvider,
):
    assert (
        wearable_data_retrieval_mock
        == env_file_provider_mock.get_wearable_data_retrieval_env()
    )


def test_get_root_env(
    root_mock: RootEnv, env_file_provider_mock: EnvFileProvider
):
    assert root_mock == env_file_provider_mock.get_root_env()


def test_write_root_env(
    env_file_provider_mock: EnvFileProvider, open_mock: MagicMock
):
    env_file_provider_mock.write_root_env()
    open_mock.assert_called_once_with(env_file_provider_mock.root_filename, "w")


def test_uninstall(
    env_file_provider_mock: EnvFileProvider, remove_mock: MagicMock
):
    env_file_provider_mock.uninstall()
    remove_mock.assert_called_once_with(env_file_provider_mock.root_filename)


def test_uninstall_not_found(
    env_file_provider_mock: EnvFileProvider, remove_mock: MagicMock
):
    remove_mock.side_effect = FileNotFoundError
    env_file_provider_mock.uninstall()
    remove_mock.assert_called_once_with(env_file_provider_mock.root_filename)
    assert env_file_provider_mock.logger.warning.call_count == 1
