import os
import shutil
import subprocess
import traceback

from install.project_config import ProjectConfigProvider
from install.utils import Logger, Colorizer
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
            subprocess.run(["npm", "install"], check=True)
            self.logger(Colorizer.blue("Frontend dependencies installed"))
            subprocess.run([
                "npx", "tailwindcss",
                "-i", "./src/index.css",
                "-o", "./src/output.css"
            ], check=True)
            self.logger(Colorizer.blue("Tailwind CSS compiled"))
            os.chdir("..")
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(f"Frontend initialization failed due to subprocess error: {Colorizer.white(e)}")
            raise SubprocessError(e)

    def build_frontend(self) -> None:
        """Build the frontend"""
        try:
            os.chdir(self.frontend_dir)
            subprocess.run(["npm", "run", "build"], check=True)
            os.chdir("..")
            self.logger(Colorizer.blue("Frontend built"))
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(f"Frontend build failed due to subprocess error: {Colorizer.white(e)}")
            raise SubprocessError(e)

    def uninstall(self) -> None:
        """Uninstall the frontend."""
        try:
            os.chdir(self.frontend_dir)
            shutil.rmtree("node_modules")
            self.logger(Colorizer.blue("Frontend uninstalled"))
        except FileNotFoundError:
            self.logger.warning(f"Frontend node_modules directory {Colorizer.blue('node_modules')} not found")
        finally:
            os.chdir("..")
