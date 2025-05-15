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

from install.local_providers.database_provider import DatabaseProvider
from install.utils.exceptions import SubprocessError
from tests.tests_install.tests_local_providers.mock_database_provider import (
    database_provider,
)


@pytest.fixture
def database_provider_mock():
    return database_provider()


@pytest.fixture
def subprocess_mock():
    with patch("subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def shutil_which_mock():
    with patch("shutil.which") as mock_which:
        # Return the input command name to simulate simple path
        mock_which.side_effect = lambda x: x
        yield mock_which


def test_upgrade_database_success(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    subprocess_mock.return_value = MagicMock(returncode=0)

    database_provider_mock.upgrade_database()

    subprocess_mock.assert_called_once_with(
        ["flask", "--app", "run.py", "db", "upgrade"], check=True
    )


def test_initialize_database_subprocess_error(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    """Test handling of subprocess error during database initialization."""
    subprocess_mock.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["flask", "--app", "run.py", "db", "upgrade"],
        output=b"Subprocess Error",
    )

    with pytest.raises(SubprocessError, match="returned non-zero exit status 1"):
        database_provider_mock.upgrade_database()


def test_initialize_database_unexpected_error(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    """Test handling of unexpected error during database initialization."""
    subprocess_mock.side_effect = Exception("Unexpected Error")

    with pytest.raises(SubprocessError, match="Unexpected Error"):
        database_provider_mock.upgrade_database()


def test_initialize_database_success(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    subprocess_mock.return_value = MagicMock(returncode=0)

    database_provider_mock.initialize_database()

    subprocess_mock.assert_called_once_with(
        ["flask", "--app", "run.py", "init-integration-testing-db"], check=True
    )


def test_initialize_database_subprocess_error(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    """Test handling of subprocess error during database initialization."""
    subprocess_mock.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["flask", "--app", "run.py", "init-integration-testing-db"],
        output=b"Subprocess Error",
    )

    with pytest.raises(SubprocessError, match="returned non-zero exit status 1"):
        database_provider_mock.initialize_database()


def test_initialize_database_unexpected_error(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    """Test handling of unexpected error during database initialization."""
    subprocess_mock.side_effect = Exception("Unexpected Error")

    with pytest.raises(SubprocessError, match="Unexpected Error"):
        database_provider_mock.initialize_database()


def test_create_researcher_account_success(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    subprocess_mock.return_value = MagicMock(returncode=0)

    database_provider_mock.create_researcher_account()

    subprocess_mock.assert_called_once_with(
        [
            "flask",
            "--app",
            "run.py",
            "create-researcher-account",
            "--email",
            database_provider_mock.config.admin_email,
        ],
        check=True,
    )


def test_create_researcher_account_subprocess_error(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    subprocess_mock.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=[
            "flask",
            "--app",
            "run.py",
            "create-researcher-account",
            "--email",
            database_provider_mock.config.admin_email,
        ],
        output=b"Subprocess Error",
    )

    with pytest.raises(SubprocessError, match="returned non-zero exit status 1"):
        database_provider_mock.create_researcher_account()


def test_researcher_account_unexpected_error(
    database_provider_mock: DatabaseProvider,
    subprocess_mock: MagicMock,
    shutil_which_mock: MagicMock,
):
    subprocess_mock.side_effect = Exception("Unexpected Error")

    with pytest.raises(SubprocessError, match="Unexpected Error"):
        database_provider_mock.create_researcher_account()
