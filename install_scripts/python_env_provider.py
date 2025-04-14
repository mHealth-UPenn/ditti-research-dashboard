import os
import subprocess
import sys

from install_scripts.utils import Logger, BaseResourceManager
from install_scripts.project_settings_provider import ProjectSettingsProvider


class PythonEnvProvider(BaseResourceManager):
    python_version: str = "python3.13"
    env_name: str = "env"

    def __init__(self, *, logger: Logger, settings: ProjectSettingsProvider):
        self.logger = logger
        self.settings = settings

    def on_start(self) -> None:
        self.logger.cyan("\n[Python Setup]")

    def on_end(self) -> None:
        pass

    def dev(self) -> None:
        self.setup_python_env()

    def staging(self) -> None:
        pass

    def prod(self) -> None:
        pass

    def setup_python_env(self) -> None:
        """Set up Python virtual environment and install packages."""
        if not os.path.exists("env/bin/activate"):
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

        subprocess.run(
            f"{activate_script} && pip install -qr "
            f"{self.requirements_filename}",
            shell=True,
            check=True
        )
