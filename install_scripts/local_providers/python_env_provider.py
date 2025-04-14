import os
import subprocess
import sys

from install_scripts.utils import Logger
from install_scripts.project_settings_provider import ProjectSettingsProvider


class PythonEnvProvider:
    requirements_filename: str = "requirements.txt"
    python_version: str = "python3.13"
    env_name: str = "env"

    def __init__(self, *, logger: Logger, settings: ProjectSettingsProvider):
        self.logger = logger
        self.settings = settings

    def initialize_python_env(self) -> None:
        """Set up Python virtual environment and install packages."""
        self.logger.cyan("\n[Python Setup]")
        if not os.path.exists(self.env_name):
            self.logger.cyan("Initializing Python virtual environment...")
            subprocess.run(
                [self.python_version, "-m", "venv", self.env_name],
                check=True
            )

        # Activate virtual environment and install packages
        if sys.platform == "win32":
            activate_script = f"{self.env_name}\\Scripts\\activate"
        else:
            activate_script = f"source {self.env_name}/bin/activate"

        subprocess.run(activate_script, check=True)

    def install_requirements(self) -> None:
        """Install requirements."""
        subprocess.run(
            f"{self.env_name}/bin/pip install -qr {self.requirements_filename}",
            shell=True,
            check=True
        )