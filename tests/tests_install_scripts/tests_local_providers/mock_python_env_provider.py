from install_scripts.local_providers import PythonEnvProvider
from tests.tests_install_scripts.tests_project_config.mock_project_config_provider import project_config_provider
from tests.tests_install_scripts.tests_utils.mock_logger import logger


def python_env_provider():
    return PythonEnvProvider(
        logger=logger(),
        settings=project_config_provider()
    )
