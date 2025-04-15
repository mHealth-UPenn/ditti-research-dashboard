import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys
from pathlib import Path

from install_scripts.local_providers.python_env_provider import PythonEnvProvider
from install_scripts.utils.exceptions import SubprocessError
from tests.tests_install_scripts.tests_local_providers.mock_python_env_provider import python_env_provider


@pytest.fixture
def python_env_provider_mock():
    return python_env_provider()


@pytest.fixture
def mock_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def mock_exists():
    with patch("os.path.exists") as mock_exists:
        yield mock_exists


def test_init_linux():
    """Test initialization of PythonEnvProvider."""
    python_env_provider_mock = python_env_provider()
    assert python_env_provider_mock.requirements_filename == "requirements.txt"
    assert python_env_provider_mock.python_version == "python3.13"
    assert python_env_provider_mock.env_name == "env"

    assert python_env_provider_mock.activate_script == Path("env/bin/activate")
    assert python_env_provider_mock.bin_path == Path("env/bin")


def test_initialize_python_env_new_env(mock_run: MagicMock, mock_exists: MagicMock, python_env_provider_mock: PythonEnvProvider):
    """Test initializing a new Python virtual environment."""
    mock_exists.return_value = False

    python_env_provider_mock.initialize_python_env()

    mock_run.assert_any_call(
        [python_env_provider_mock.python_version, "-m", "venv", python_env_provider_mock.env_name],
        check=True
    )
    mock_run.assert_any_call(python_env_provider_mock.activate_script, check=True)


def test_initialize_python_env_existing_env(mock_run: MagicMock, mock_exists: MagicMock, python_env_provider_mock: PythonEnvProvider):
    """Test initializing when virtual environment already exists."""
    mock_exists.return_value = True

    python_env_provider_mock.initialize_python_env()

    mock_run.assert_called_once_with(python_env_provider_mock.activate_script, check=True)


def test_install_requirements(mock_run: MagicMock, python_env_provider_mock: PythonEnvProvider):
    """Test installing requirements."""
    python_env_provider_mock.install_requirements()

    mock_run.assert_called_once_with(
        f"{python_env_provider_mock.bin_path / "pip"} install -qr {python_env_provider_mock.requirements_filename}",
        shell=True,
        check=True
    )


def test_install_requirements_error(mock_run: MagicMock, python_env_provider_mock: PythonEnvProvider):
    """Test handling of errors during requirements installation."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "pip install")

    with pytest.raises(SubprocessError, match="returned non-zero exit status 1"):
        python_env_provider_mock.install_requirements()


def test_install_requirements_unexpected_error(mock_run: MagicMock, python_env_provider_mock: PythonEnvProvider):
    """Test handling of unexpected errors during requirements installation."""
    mock_run.side_effect = Exception("Unexpected error")

    with pytest.raises(SubprocessError, match="Unexpected error"):
        python_env_provider_mock.install_requirements()
