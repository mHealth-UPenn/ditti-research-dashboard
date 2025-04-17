import subprocess
from unittest.mock import patch, MagicMock

import pytest

from tests.tests_install_scripts.tests_local_providers.mock_database_provider import database_provider
from install_scripts.utils.exceptions import SubprocessError
from install_scripts.local_providers.database_provider import DatabaseProvider


@pytest.fixture
def database_provider_mock():
    return database_provider()


@pytest.fixture
def subprocess_mock():
    with patch("subprocess.run") as mock_run:
        yield mock_run


def test_upgrade_database_success(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    subprocess_mock.return_value = MagicMock(returncode=0)

    database_provider_mock.upgrade_database()

    subprocess_mock.assert_called_once_with(["flask", "--app", "run.py", "db", "upgrade"], check=True)


def test_initialize_database_subprocess_error(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    """Test handling of subprocess error during database initialization."""
    subprocess_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["flask", "--app", "run.py", "db", "upgrade"], output=b"Subprocess Error")

    with pytest.raises(SubprocessError, match="returned non-zero exit status 1"):
        database_provider_mock.upgrade_database()


def test_initialize_database_unexpected_error(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    """Test handling of unexpected error during database initialization."""
    subprocess_mock.side_effect = Exception("Unexpected Error")

    with pytest.raises(SubprocessError, match="Unexpected Error"):
        database_provider_mock.upgrade_database()


def test_initialize_database_success(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    subprocess_mock.return_value = MagicMock(returncode=0)

    database_provider_mock.initialize_database()

    subprocess_mock.assert_called_once_with(["flask", "--app", "run.py", "init-integration-testing-db"], check=True)


def test_initialize_database_subprocess_error(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    """Test handling of subprocess error during database initialization."""
    subprocess_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["flask", "--app", "run.py", "init-integration-testing-db"], output=b"Subprocess Error")

    with pytest.raises(SubprocessError, match="returned non-zero exit status 1"):
        database_provider_mock.initialize_database()


def test_initialize_database_unexpected_error(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    """Test handling of unexpected error during database initialization."""
    subprocess_mock.side_effect = Exception("Unexpected Error")

    with pytest.raises(SubprocessError, match="Unexpected Error"):
        database_provider_mock.initialize_database()


def test_create_researcher_account_success(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    subprocess_mock.return_value = MagicMock(returncode=0)

    database_provider_mock.create_researcher_account()

    subprocess_mock.assert_called_once_with(["flask", "--app", "run.py", "create-researcher-account", "--email", database_provider_mock.config.admin_email], check=True)


def test_create_researcher_account_subprocess_error(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    subprocess_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["flask", "--app", "run.py", "create-researcher-account", "--email", database_provider_mock.config.admin_email], output=b"Subprocess Error")

    with pytest.raises(SubprocessError, match="returned non-zero exit status 1"):
        database_provider_mock.create_researcher_account()


def test_researcher_account_unexpected_error(database_provider_mock: DatabaseProvider, subprocess_mock: MagicMock):
    subprocess_mock.side_effect = Exception("Unexpected Error")

    with pytest.raises(SubprocessError, match="Unexpected Error"):
        database_provider_mock.create_researcher_account()
