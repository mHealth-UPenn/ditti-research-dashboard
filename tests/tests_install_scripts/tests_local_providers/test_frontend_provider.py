import subprocess
from unittest.mock import patch, MagicMock

import pytest

from install_scripts.local_providers.frontend_provider import FrontendProvider
from install_scripts.utils.exceptions import SubprocessError
from tests.tests_install_scripts.tests_local_providers.mock_frontend_provider import frontend_provider


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


def test_initialize_frontend(frontend_provider_mock: FrontendProvider, subprocess_mock: MagicMock, os_chdir_mock: MagicMock):
    frontend_provider_mock.initialize_frontend()
    subprocess_mock.assert_any_call(["npm", "install"], check=True)
    subprocess_mock.assert_any_call(["npx", "tailwindcss", "-i", "./src/index.css", "-o", "./src/output.css"], check=True)
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)
    os_chdir_mock.assert_any_call("..")
    assert os_chdir_mock.call_count == 2


def test_initialize_frontend_subprocess_error(frontend_provider_mock: FrontendProvider, subprocess_mock: MagicMock):
    subprocess_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["npm", "install"])
    with pytest.raises(SubprocessError):
        frontend_provider_mock.initialize_frontend()


def test_build_frontend(frontend_provider_mock: FrontendProvider, subprocess_mock: MagicMock, os_chdir_mock: MagicMock):
    frontend_provider_mock.build_frontend()
    subprocess_mock.assert_any_call(["npm", "run", "build"], check=True)
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)
    os_chdir_mock.assert_any_call("..")


def test_build_frontend_subprocess_error(frontend_provider_mock: FrontendProvider, subprocess_mock: MagicMock, os_chdir_mock: MagicMock):
    subprocess_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["npm", "run", "build"])
    with pytest.raises(SubprocessError):
        frontend_provider_mock.build_frontend()
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)


def test_uninstall(frontend_provider_mock: FrontendProvider, shutil_rmtree_mock: MagicMock, os_chdir_mock: MagicMock):
    frontend_provider_mock.uninstall()
    os_chdir_mock.assert_any_call(frontend_provider_mock.frontend_dir)
    shutil_rmtree_mock.assert_called_once_with("node_modules")
    os_chdir_mock.assert_any_call("..")


def test_uninstall_not_found(frontend_provider_mock: FrontendProvider, shutil_rmtree_mock: MagicMock):
    shutil_rmtree_mock.side_effect = FileNotFoundError
    frontend_provider_mock.uninstall()
    frontend_provider_mock.logger.warning.assert_called_once()
