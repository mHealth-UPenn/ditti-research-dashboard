# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
            subprocess.run(
                ["flask", "--app", "run.py", "db", "upgrade"], check=True
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
            subprocess.run(
                ["flask", "--app", "run.py", "init-integration-testing-db"],
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
            subprocess.run(
                [
                    "flask",
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
