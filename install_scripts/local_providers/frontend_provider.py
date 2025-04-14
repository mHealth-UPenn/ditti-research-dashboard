import os
import subprocess

from install_scripts.utils import Logger
from install_scripts.project_config.project_config_provider import ProjectConfigProvider


class FrontendProvider:
    frontend_dir = "frontend"

    def __init__(self, *, logger: Logger, settings: ProjectConfigProvider):
        self.logger = logger
        self.settings = settings

    def initialize_frontend(self) -> None:
        """Set up frontend dependencies and Tailwind CSS."""
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
