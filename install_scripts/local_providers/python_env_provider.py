import os
from pathlib import Path
import subprocess

from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import SubprocessError

class PythonEnvProvider:
    requirements_filename: str = "requirements.txt"
    python_version: str = "python3.13"
    env_name: str = "env"
    bin_path: Path
    activate_script: Path

    def __init__(self, *, logger: Logger, settings: ProjectConfigProvider):
        self.logger = logger
        self.settings = settings
        self.activate_script = Path(self.env_name) / "bin" / "activate"
        self.bin_path = Path(self.env_name) / "bin"

    def initialize_python_env(self) -> None:
        """Set up Python virtual environment and install packages."""
        self.logger.cyan("\n[Python Setup]")
        if not os.path.exists(self.env_name):
            self.logger.cyan("Initializing Python virtual environment...")
            subprocess.run(
                [self.python_version, "-m", "venv", self.env_name],
                check=True
            )

        subprocess.run(self.activate_script, check=True)

    def install_requirements(self) -> None:
        """Install requirements."""
        try:
            subprocess.run(
                f"{self.bin_path / "pip"} install -qr {self.requirements_filename}",
                shell=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            self.logger.red(f"Error installing requirements due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            self.logger.red(f"Error installing requirements due to unexpected error: {e}")
            raise SubprocessError(e)

