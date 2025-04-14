import sys
import traceback

from install_scripts.utils import Logger, Env
from install_scripts.aws import (
    AwsAccountProvider,
    AwsCloudformationCreator,
    AwsEcrProvider,
)
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.python_env_provider import PythonEnvProvider
from install_scripts.docker_provider import DockerProvider
from install_scripts.env_provider import EnvProvider
from install_scripts.frontend_provider import FrontendProvider

def main(env: Env = "dev"):
    """Main installation function."""
    suffix = ""
    match env:
        case "dev":
            suffix = "dev"
        case "staging":
            suffix = "staging"
        case _:
            pass

    logger = Logger()
    aws_account_provider = AwsAccountProvider(logger=logger)
    project_settings_provider = ProjectSettingsProvider(
        logger=logger,
        project_suffix=suffix,
    )
    aws_ecr_provider = AwsEcrProvider(
        logger=logger,
        settings=project_settings_provider,
        aws_account_provider=aws_account_provider,
    )
    aws_resources_provider = AwsCloudformationCreator(
        logger=logger,
        settings=project_settings_provider,
    )
    python_env_provider = PythonEnvProvider(
        logger=logger,
        settings=project_settings_provider,
    )
    docker_provider = DockerProvider(
        logger=logger,
        settings=project_settings_provider,
        aws_ecr_provider=aws_ecr_provider,
    )
    env_provider = EnvProvider(
        logger=logger,
        settings=project_settings_provider,
        aws_account_handler=aws_account_provider,
    )
    frontend_provider = FrontendProvider(
        logger=logger,
        settings=project_settings_provider,
    )

    try:
        aws_account_provider.run()
        project_settings_provider.run()
        # aws_resources_handler.run()
        python_env_provider.run()
        docker_provider.run()
        env_provider.run()
        frontend_provider.run()

        logger.green("\n[Installation complete]")
        logger.cyan(
            "Check your email for a temporary password for the researcher "
            "admin user"
        )
        logger.blue(
            "You can now start the development server with npm run start and "
            "flask run"
        )

    except Exception:
        traceback.print_exc()
        logger.red("Installation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
