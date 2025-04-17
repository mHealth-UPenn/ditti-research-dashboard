import subprocess
import traceback

from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import SubprocessError


class DatabaseProvider:
    def __init__(self, logger: Logger, settings: ProjectConfigProvider):
        self.logger = logger
        self.settings = settings

    def upgrade_database(self) -> None:
        """Initialize the database."""
        try:
            subprocess.run(
                ["flask", "--app", "run.py", "db", "upgrade"],
                check=True
            )
            self.logger.blue(f"Database upgraded")
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"Database upgrade failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Database upgrade failed due to unexpected error: {e}")
            raise SubprocessError(e)

    def initialize_database(self) -> None:
        try:
            subprocess.run(
                ["flask", "--app", "run.py", "init-integration-testing-db"],
                check=True
            )
            self.logger.blue(f"Integration testing database initialized")
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger \
                .red(f"Integration testing database initialization failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Integration testing database initialization failed due to unexpected error: {e}")
            raise SubprocessError(e)

    def create_researcher_account(self) -> None:
        try:
            subprocess.run([
                "flask",
                "--app", "run.py",
                "create-researcher-account",
                "--email", self.settings.admin_email
            ], check=True)
            self.logger.blue(f"Researcher account created")
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"Researcher account creation failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Researcher account creation failed due to unexpected error: {e}")
            raise SubprocessError(e)
