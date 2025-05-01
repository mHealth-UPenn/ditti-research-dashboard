import os
import shutil
import subprocess
import traceback

from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import SubprocessError


class FrontendProvider:
    """
    Provider for frontend application setup and configuration.

    Manages frontend environment configuration, dependency installation,
    and build processes for the application user interface.
    """

    frontend_dir = "frontend"

    def __init__(self, *, logger: Logger, config: ProjectConfigProvider):
        self.logger = logger
        self.config = config

    def initialize_frontend(self) -> None:
        """Set up frontend dependencies and Tailwind CSS."""
        try:
            os.chdir(self.frontend_dir)
            npm_executable = shutil.which("npm")
            if npm_executable is None:
                raise FileNotFoundError("npm executable not found")

            subprocess.run([npm_executable, "install"], check=True)
            self.logger(Colorizer.blue("Frontend dependencies installed"))
            subprocess.run([npm_executable, "run", "tailwind"], check=True)
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
            npm_executable = shutil.which("npm")
            if npm_executable is None:
                raise FileNotFoundError("npm executable not found")

            subprocess.run([npm_executable, "run", "build"], check=True)
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
