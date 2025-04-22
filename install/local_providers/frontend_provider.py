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

import os
import shutil
import subprocess
import traceback

from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import SubprocessError


class FrontendProvider:
    frontend_dir = "frontend"

    def __init__(self, *, logger: Logger, config: ProjectConfigProvider):
        self.logger = logger
        self.config = config

    def initialize_frontend(self) -> None:
        """Set up frontend dependencies and Tailwind CSS."""
        try:
            os.chdir(self.frontend_dir)
            subprocess.run(["npm", "install"], check=True)  # noqa: S603
            self.logger(Colorizer.blue("Frontend dependencies installed"))
            subprocess.run(["npm", "run", "tailwind"], check=True)  # noqa: S603
            self.logger(Colorizer.blue("Tailwind CSS compiled"))
            os.chdir("..")
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(
                "Frontend initialization failed due to subprocess error: "
                f"{Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e

    def build_frontend(self) -> None:
        """Build the frontend."""
        try:
            os.chdir(self.frontend_dir)
            subprocess.run(["npm", "run", "build"], check=True)  # noqa: S603
            os.chdir("..")
            self.logger(Colorizer.blue("Frontend built"))
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(
                "Frontend build failed due to subprocess error: "
                f"{Colorizer.white(e)}"
            )
            raise SubprocessError(e) from e

    def uninstall(self) -> None:
        """Uninstall the frontend."""
        try:
            os.chdir(self.frontend_dir)
            shutil.rmtree("node_modules")
            self.logger(Colorizer.blue("Frontend uninstalled"))
        except (FileNotFoundError, OSError):
            self.logger.warning(
                "Frontend node_modules directory "
                f"{Colorizer.blue('node_modules')} not found"
            )
        finally:
            os.chdir("..")
