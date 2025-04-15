import shutil
import subprocess
import time
import traceback

import docker

from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.enums import Postgres
from install_scripts.utils.exceptions import DockerSDKError, SubprocessError

class DockerProvider:
    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.docker_client = docker.from_env()

    def run_postgres_container(self) -> None:
        """Set up Postgres container."""
        self.logger.cyan("\n[Docker Setup]")

        # Create Docker network
        try:
            self.docker_client.networks.create(self.settings.network_name)
            self.logger.blue(f"Created docker network {self.settings.network_name}")
        except docker.errors.APIError as e:
            traceback.print_exc()
            self.logger.red(f"Error creating docker network due to APIError: {e}")
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error creating docker network due to unexpected error: {e}")
            raise DockerSDKError(e)

        # Create Postgres container
        try:
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
        except docker.errors.ContainerError as e:
            traceback.print_exc()
            self.logger.red(f"Error creating postgres container due to ContainerError: {e}")
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error creating postgres container due to unexpected error: {e}")
            raise DockerSDKError(e)

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
            except Exception as e:
                traceback.print_exc()
                self.logger.red(f"Error waiting for postgres container due to unexpected error: {e}")
                raise DockerSDKError(e)

        self.logger.blue(
            f"Created postgres container "
            f"{self.settings.postgres_container_name}"
        )

        try:
            subprocess.run(
                ["flask", "--app", "run.py", "db", "upgrade"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"Database upgrade failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Database upgrade failed due to unexpected error: {e}")
            raise SubprocessError(e)

        try:
            subprocess.run(
                ["flask", "--app", "run.py", "init-integration-testing-db"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger \
                .red(f"Integration testing database initialization failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Integration testing database initialization failed due to unexpected error: {e}")
            raise SubprocessError(e)

        try:
            subprocess.run([
                "flask",
                "--app", "run.py",
                "create-researcher-account",
                "--email", self.settings.admin_email
            ], check=True)
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"Researcher account creation failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Researcher account creation failed due to unexpected error: {e}")
            raise SubprocessError(e)

    def build_wearable_data_retrieval_container(self) -> None:
        """Build wearable data retrieval container."""
        try:
            shutil.copytree("shared", "functions/wearable_data_retrieval/shared")
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error copying shared files due to unexpected error: {e}")
            raise SubprocessError(e)

        try:
            self.docker_client.images.build(
                path="functions/wearable_data_retrieval",
                tag=self.settings.wearable_data_retrieval_container_name,
                platform="linux/amd64"
            )
        except docker.errors.BuildError as e:
            traceback.print_exc()
            self.logger.red(f"Wearable data retrieval container creation failed due to BuildError: {e}")
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Wearable data retrieval container creation failed due to unexpected error: {e}")
            raise DockerSDKError(e)

        try:
            shutil.rmtree("functions/wearable_data_retrieval/shared")
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error removing shared files due to unexpected error: {e}")
            raise SubprocessError(e)

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
        except docker.errors.ContainerError as e:
            traceback.print_exc()
            self.logger.red(f"Wearable data retrieval container creation failed due to ContainerError: {e}")
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Wearable data retrieval container creation failed due to unexpected error: {e}")
            raise DockerSDKError(e)

    def uninstall(self) -> None:
        """Uninstall the Docker containers."""
        try:
            self.docker_client.containers.stop(self.settings.postgres_container_name)
            self.docker_client.containers.remove(self.settings.postgres_container_name)
        except docker.errors.NotFoundError:
            self.logger.yellow(f"Docker container {self.settings.postgres_container_name} not found")

        try:
            self.docker_client.containers.stop(self.settings.wearable_data_retrieval_container_name)
            self.docker_client.containers.remove(self.settings.wearable_data_retrieval_container_name)
        except docker.errors.NotFoundError:
            self.logger.yellow(f"Docker container {self.settings.wearable_data_retrieval_container_name} not found")

        try:
            self.docker_client.networks.remove(self.settings.network_name)
        except docker.errors.NotFoundError:
            self.logger.yellow(f"Docker network {self.settings.network_name} not found")
