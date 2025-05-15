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

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from install.local_providers.frontend_provider import FrontendProvider
from install.utils.exceptions import SubprocessError
from tests.tests_install.tests_local_providers.mock_frontend_provider import (
    frontend_provider,
)


@pytest.fixture
def frontend_provider_mock():
    return frontend_provider()


@pytest.fixture
def subprocess_mock():
    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def os_chdir_mock():
    with patch("os.chdir") as mock:
        yield mock


@pytest.fixture
def shutil_rmtree_mock():
    with patch("shutil.rmtree") as mock:
        yield mock


@pytest.fixture
def shutil_which_mock():
    with patch("shutil.which") as mock_which:
        # Return the input command name to simulate simple path
        mock_which.side_effect = lambda x: x
        yield mock_which


def test_initialize_frontend(
    frontend_provider_mock: FrontendProvider,
    subprocess_mock: MagicMock,
    os_chdir_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    frontend_provider_mock.initialize_frontend()
    subprocess_mock.assert_any_call(["npm", "install"], check=True)
    subprocess_mock.assert_any_call(["npm", "run", "tailwind"], check=True)
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)
    os_chdir_mock.assert_any_call("..")
    assert os_chdir_mock.call_count == 2


def test_initialize_frontend_subprocess_error(
    frontend_provider_mock: FrontendProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    subprocess_mock.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["npm", "install"]
    )
    with pytest.raises(SubprocessError):
        frontend_provider_mock.initialize_frontend()


def test_build_frontend(
    frontend_provider_mock: FrontendProvider,
    subprocess_mock: MagicMock,
    os_chdir_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    frontend_provider_mock.build_frontend()
    subprocess_mock.assert_any_call(["npm", "run", "build"], check=True)
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)
    os_chdir_mock.assert_any_call("..")


def test_build_frontend_subprocess_error(
    frontend_provider_mock: FrontendProvider,
    subprocess_mock: MagicMock,
    os_chdir_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    subprocess_mock.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["npm", "run", "build"]
    )
    with pytest.raises(SubprocessError):
        frontend_provider_mock.build_frontend()
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)


def test_uninstall(
    frontend_provider_mock: FrontendProvider,
    shutil_rmtree_mock: MagicMock,
    os_chdir_mock: MagicMock,
):
    frontend_provider_mock.uninstall()
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)
    shutil_rmtree_mock.assert_called_once_with("node_modules")
    os_chdir_mock.assert_any_call("..")


def test_uninstall_not_found(
    frontend_provider_mock: FrontendProvider, shutil_rmtree_mock: MagicMock
):
    shutil_rmtree_mock.side_effect = FileNotFoundError
    frontend_provider_mock.uninstall()
    frontend_provider_mock.logger.warning.assert_called_once()
