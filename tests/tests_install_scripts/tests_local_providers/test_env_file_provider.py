import pytest
from unittest.mock import patch, MagicMock, mock_open

from moto import mock_aws

from install_scripts.local_providers.local_provider_types import WearableDataRetrievalEnv, RootEnv
from install_scripts.local_providers.env_file_provider import EnvFileProvider
from tests.tests_install_scripts.tests_local_providers.mock_env_file_provider import wearable_data_retrieval_env, root_env, env_file_provider


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


def test_get_wearable_data_retrieval_env(wearable_data_retrieval_mock: WearableDataRetrievalEnv, env_file_provider_mock: EnvFileProvider):
    assert wearable_data_retrieval_mock == env_file_provider_mock.get_wearable_data_retrieval_env()


def test_get_root_env(root_mock: RootEnv, env_file_provider_mock: EnvFileProvider):
    assert root_mock == env_file_provider_mock.get_root_env()


def test_write_env_files(env_file_provider_mock: EnvFileProvider, open_mock: MagicMock):
    env_file_provider_mock.write_env_files({}, {})
    open_mock.assert_any_call(env_file_provider_mock.wearable_data_retrieval_filename, "w")
    open_mock.assert_any_call(env_file_provider_mock.root_filename, "w")
    assert open_mock.call_count == 2


def test_uninstall(env_file_provider_mock: EnvFileProvider, remove_mock: MagicMock):
    env_file_provider_mock.uninstall()
    remove_mock.assert_any_call(env_file_provider_mock.wearable_data_retrieval_filename)
    remove_mock.assert_any_call(env_file_provider_mock.root_filename)
    assert remove_mock.call_count == 2


def test_uninstall_not_found(env_file_provider_mock: EnvFileProvider, remove_mock: MagicMock):
    remove_mock.side_effect = FileNotFoundError
    env_file_provider_mock.uninstall()
    remove_mock.assert_any_call(env_file_provider_mock.wearable_data_retrieval_filename)
    remove_mock.assert_any_call(env_file_provider_mock.root_filename)
    assert remove_mock.call_count == 2
    assert env_file_provider_mock.logger.warning.call_count == 2
