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
                f"Database upgrade failed due to subprocess error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Database upgrade failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)

    def initialize_database(self) -> None:
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
                f"Integration testing database initialization failed due to subprocess error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Integration testing database initialization failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)

    def create_researcher_account(self) -> None:
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
                f"Researcher account creation failed due to subprocess error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Researcher account creation failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)
