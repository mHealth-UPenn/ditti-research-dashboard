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

import shutil
import subprocess
import traceback

from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import SubprocessError


class DatabaseProvider:
    """
    Provider for database operations during installation.

    Manages database initialization, migrations, and account setup
    for the application.
    """

    def __init__(self, logger: Logger, config: ProjectConfigProvider):
        self.logger = logger
        self.config = config

    def upgrade_database(self) -> None:
        """Initialize the database."""
        try:
            flask_executable = shutil.which("flask")
            if flask_executable is None:
                raise FileNotFoundError("Flask CLI executable not found")

            subprocess.run(
                [flask_executable, "--app", "run.py", "db", "upgrade"], check=True
            )
            self.logger(Colorizer.blue("Database upgraded"))
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(
                "Database upgrade failed due to subprocess error: "
                f"{Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Database upgrade failed due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e

    def initialize_database(self) -> None:
        """
        Initialize the database with required tables and seed data.

        Runs database migrations and initial setup commands to prepare
        the database for application use.

        Returns
        -------
        None

        Raises
        ------
        SubprocessError
            If database initialization fails.
        """
        try:
            flask_executable = shutil.which("flask")
            if flask_executable is None:
                raise FileNotFoundError("Flask CLI executable not found")

            subprocess.run(
                [
                    flask_executable,
                    "--app",
                    "run.py",
                    "init-integration-testing-db",
                ],
                check=True,
            )
            self.logger(
                Colorizer.blue("Integration testing database initialized")
            )
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(
                "Integration testing database initialization failed due to "
                f"subprocess error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Integration testing database initialization failed due to "
                f"unexpected error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e

    def create_researcher_account(self) -> None:
        """
        Create an initial researcher account in the database.

        Creates a researcher account with administrative privileges
        for initial application access.

        Returns
        -------
        None

        Raises
        ------
        SubprocessError
            If account creation fails.
        """
        try:
            flask_executable = shutil.which("flask")
            if flask_executable is None:
                raise FileNotFoundError("Flask CLI executable not found")

            subprocess.run(
                [
                    flask_executable,
                    "--app",
                    "run.py",
                    "create-researcher-account",
                    "--email",
                    self.config.admin_email,
                ],
                check=True,
            )
            self.logger(Colorizer.blue("Researcher account created"))
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(
                "Researcher account creation failed due to subprocess error: "
                f"{Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Researcher account creation failed due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e
