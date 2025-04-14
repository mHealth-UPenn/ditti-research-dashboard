import os
import subprocess

from install_scripts.utils import (
    Logger,
    BaseCreator
)
from install_scripts.project_settings_provider import ProjectSettingsProvider


class FrontendProvider(BaseCreator):
    frontend_dir = "frontend"

    def __init__(self, *, logger: Logger, settings: ProjectSettingsProvider):
        self.logger = logger
        self.settings = settings

    def on_start(self) -> None:
        """Run when the script starts."""
        self.logger.cyan("\n[Frontend Setup]")
        os.chdir(self.frontend_dir)

    def on_end(self) -> None:
        """Run when the script ends."""
        os.chdir("..")

    def dev(self) -> None:
        self.setup_frontend()

    def prod(self) -> None:
        self.build_frontend()

    def staging(self) -> None:
        pass

    def setup_frontend(self) -> None:
        """Set up frontend dependencies."""
        os.chdir(self.frontend_dir)
        subprocess.run(["npm", "install"], check=True)
        subprocess.run([
            "npx", "tailwindcss",
            "-i", "./src/index.css",
            "-o", "./src/output.css"
        ], check=True)
        os.chdir("..")

    def build_frontend(self) -> None:
        """Build the frontend"""
        os.chdir(self.frontend_dir)
        subprocess.run(["npm", "run", "build"], check=True)
        os.chdir("..")
