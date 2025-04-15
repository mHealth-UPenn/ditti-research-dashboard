import os
import shutil
import subprocess
import traceback

from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import SubprocessError


class FrontendProvider:
    frontend_dir = "frontend"

    def __init__(self, *, logger: Logger, settings: ProjectConfigProvider):
        self.logger = logger
        self.settings = settings

    def initialize_frontend(self) -> None:
        """Set up frontend dependencies and Tailwind CSS."""
        try:
            os.chdir(self.frontend_dir)
            subprocess.run(["npm", "install"], check=True)
            self.logger.blue(f"Frontend dependencies installed")
            subprocess.run([
                "npx", "tailwindcss",
                "-i", "./src/index.css",
                "-o", "./src/output.css"
            ], check=True)
            self.logger.blue(f"Tailwind CSS compiled")
            os.chdir("..")
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"Frontend initialization failed due to subprocess error: {e}")
            raise SubprocessError(e)

    def build_frontend(self) -> None:
        """Build the frontend"""
        try:
            os.chdir(self.frontend_dir)
            subprocess.run(["npm", "run", "build"], check=True)
            os.chdir("..")
            self.logger.blue(f"Frontend built")
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"Frontend build failed due to subprocess error: {e}")
            raise SubprocessError(e)

    def uninstall(self) -> None:
        """Uninstall the frontend."""
        try:
            os.chdir(self.frontend_dir)
            shutil.rmtree("node_modules")
            shutil.rmtree("build")
            self.logger.blue(f"Frontend uninstalled")
        except FileNotFoundError:
            self.logger.yellow("Frontend directory not found")
        finally:
            os.chdir("..")
