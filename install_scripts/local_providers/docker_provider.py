import shutil
import subprocess
import sys
import time
import traceback

import docker

from install_scripts.utils import Logger
from install_scripts.utils.enums import Postgres
from install_scripts.project_settings_provider import ProjectSettingsProvider


class DockerProvider:
    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.docker_client = docker.from_env()

    def initialize_local_docker_environment(self) -> None:
        self.logger.cyan("\n[Docker Setup]")
        self.run_postgres_container()
        self.build_wearable_data_retrieval_container()
        self.run_wearable_data_retrieval_container()

    def run_postgres_container(self) -> None:
        """Set up Postgres container."""
        self.logger.cyan("\n[Docker Setup]")

        # Create Docker network
        self.docker_client.networks.create(self.settings.network_name)
        self.logger.blue(f"Created docker network {self.settings.network_name}")

        # Create Postgres container
        self.docker_client.containers.run(
            image="postgres",
            name=self.settings.postgres_container_name,
            environment={
                "POSTGRES_USER": Postgres.USER,
                "POSTGRES_PASSWORD": Postgres.PASSWORD,
                "POSTGRES_DB": Postgres.DB,
            },
            ports={Postgres.PORT: Postgres.PORT},
            network=self.settings.network_name,
        )

        # Wait for Postgres to be ready
        while True:
            try:
                response = self.docker_client.containers \
                    .get(self.settings.postgres_container_name) \
                    .exec_run([
                        "pg_isready",
                        "-U", Postgres.USER,
                        "-d", Postgres.DB
                    ])
                if (
                    response.exit_code == 0
                    and "accepting connections"
                    in response.output.decode("utf-8").strip()
                ):
                    break
                else:
                    time.sleep(1)
            except docker.errors.NotFoundError:
                time.sleep(1)

        self.logger.blue(
            f"Created postgres container "
            f"{self.settings.postgres_container_name}"
        )

        try:
            subprocess.run(
                ["flask", "--app", "run.py", "db", "upgrade"],
                check=True
            )
        except subprocess.CalledProcessError:
            traceback.print_exc()
            self.logger.red("Database upgrade failed")
            sys.exit(1)

        try:
            subprocess.run(
                ["flask", "--app", "run.py", "init-integration-testing-db"],
                check=True
            )
        except subprocess.CalledProcessError:
            traceback.print_exc()
            self.logger \
                .red("Integration testing database initialization failed")
            sys.exit(1)

        try:
            subprocess.run([
                "flask",
                "--app", "run.py",
                "create-researcher-account",
                "--email", self.settings.admin_email
            ], check=True)
        except subprocess.CalledProcessError:
            traceback.print_exc()
            self.logger.red("Researcher account creation failed")
            sys.exit(1)

    def build_wearable_data_retrieval_container(self) -> None:
        """Build wearable data retrieval container."""
        shutil.copytree("shared", "functions/wearable_data_retrieval/shared")

        try:
            self.docker_client.images.build(
                path="functions/wearable_data_retrieval",
                tag=self.settings.wearable_data_retrieval_container_name,
                platform="linux/amd64"
            )
        except docker.errors.BuildError:
            traceback.print_exc()
            self.logger.red("Wearable data retrieval container creation failed")
            sys.exit(1)

        shutil.rmtree("functions/wearable_data_retrieval/shared")

    def run_wearable_data_retrieval_container(self) -> None:
        """Run wearable data retrieval container."""
        try:
            self.docker_client.containers.run(
                image=self.settings.wearable_data_retrieval_container_name,
                name=self.settings.wearable_data_retrieval_container_name,
                platform="linux/amd64",
                network=self.settings.network_name,
                ports={"9000": 8080},
                environment={"TESTING": "true"},
                detach=True
            )
        except docker.errors.ContainerError:
            traceback.print_exc()
            self.logger.red("Wearable data retrieval container creation failed")
            sys.exit(1)
