# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import shutil
import time
import traceback

import docker
from docker.models.containers import Container
from docker.models.networks import Network

from install.local_providers.env_file_provider import EnvFileProvider
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.enums import Postgres
from install.utils.exceptions import DockerSDKError, LocalProviderError


class DockerProvider:
    def __init__(
        self,
        *,
        logger: Logger,
        config: ProjectConfigProvider,
        env_file_provider: EnvFileProvider,
    ):
        self.logger = logger
        self.config = config
        self.docker_client = docker.from_env()
        self.env_file_provider = env_file_provider

    def create_network(self) -> None:
        """Create Docker network."""
        # Create Docker network
        try:
            self.docker_client.networks.create(self.config.network_name)
            self.logger(
                f"Created docker network {Colorizer.blue(self.config.network_name)}"
            )
        except docker.errors.APIError as e:
            traceback.print_exc()
            self.logger.error(
                f"Error creating docker network due to APIError: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error creating docker network due to unexpected error: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)

    def run_postgres_container(self) -> None:
        """Set up Postgres container."""
        # Create Postgres container
        try:
            self.docker_client.containers.run(
                image="postgres",
                name=self.config.postgres_container_name,
                environment={
                    "POSTGRES_USER": Postgres.USER.value,
                    "POSTGRES_PASSWORD": Postgres.PASSWORD.value,
                    "POSTGRES_DB": Postgres.DB.value,
                },
                ports={Postgres.PORT.value: Postgres.PORT.value},
                network=self.config.network_name,
                detach=True,
            )
        except docker.errors.ContainerError as e:
            traceback.print_exc()
            self.logger.error(
                f"Error creating postgres container due to ContainerError: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error creating postgres container due to unexpected error: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)

        # Wait for Postgres to be ready
        while True:
            try:
                response = self.get_container(
                    self.config.postgres_container_name
                ).exec_run(
                    [
                        "pg_isready",
                        "-U",
                        Postgres.USER.value,
                        "-d",
                        Postgres.DB.value,
                    ]
                )
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
                self.logger.error(
                    f"Error waiting for postgres container due to unexpected error: {Colorizer.white(e)}"
                )
                raise DockerSDKError(e)

        self.logger(
            f"Created postgres container "
            f"{Colorizer.blue(self.config.postgres_container_name)}"
        )

    def build_wearable_data_retrieval_container(self) -> None:
        """Build wearable data retrieval container."""
        try:
            shutil.copytree("shared", "functions/wearable_data_retrieval/shared")
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error copying shared files due to unexpected error: {Colorizer.white(e)}"
            )
            raise LocalProviderError(e)

        try:
            self.docker_client.images.build(
                path="functions/wearable_data_retrieval",
                tag=self.config.wearable_data_retrieval_container_name,
                platform="linux/amd64",
            )
        except docker.errors.BuildError as e:
            traceback.print_exc()
            self.logger.error(
                f"Wearable data retrieval container creation failed due to BuildError: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Wearable data retrieval container creation failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)

        try:
            shutil.rmtree("functions/wearable_data_retrieval/shared")
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error removing shared files due to unexpected error: {Colorizer.white(e)}"
            )
            raise LocalProviderError(e)

        self.logger(
            f"Wearable data retrieval image "
            f"{Colorizer.blue(self.config.wearable_data_retrieval_container_name)} created"
        )

    def run_wearable_data_retrieval_container(self) -> None:
        """Run wearable data retrieval container."""
        try:
            self.docker_client.containers.run(
                image=self.config.wearable_data_retrieval_container_name,
                name=self.config.wearable_data_retrieval_container_name,
                platform="linux/amd64",
                network=self.config.network_name,
                ports={"8080": 9000},
                environment=self.env_file_provider.get_wearable_data_retrieval_env(),
                detach=True,
            )
        except docker.errors.ContainerError as e:
            traceback.print_exc()
            self.logger.error(
                f"Wearable data retrieval container creation failed due to ContainerError: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Wearable data retrieval container creation failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise DockerSDKError(e)

        self.logger(
            f"Wearable data retrieval container "
            f"{Colorizer.blue(self.config.wearable_data_retrieval_container_name)} created"
        )

    def get_container(self, container_name: str) -> Container:
        """Get a container by name."""
        try:
            return self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            self.logger.warning(
                f"Docker container {Colorizer.blue(container_name)} not found"
            )
            raise DockerSDKError(
                f"Container {Colorizer.blue(container_name)} not found"
            )

    def get_network(self) -> Network:
        """Get a network by name."""
        try:
            return self.docker_client.networks.get(self.config.network_name)
        except docker.errors.NotFound:
            self.logger.warning(
                f"Docker network {Colorizer.blue(self.config.network_name)} not found"
            )
            raise DockerSDKError(
                f"Network {Colorizer.blue(self.config.network_name)} not found"
            )

    def uninstall(self) -> None:
        """Uninstall the Docker containers."""
        try:
            container = self.get_container(self.config.postgres_container_name)
            container.stop()
            container.remove()
            self.logger(
                f"Postgres container {Colorizer.blue(self.config.postgres_container_name)} removed"
            )
        except DockerSDKError:
            self.logger.warning(
                f"Unable to stop and remove postgres container {Colorizer.blue(self.config.postgres_container_name)}"
            )

        try:
            container = self.get_container(
                self.config.wearable_data_retrieval_container_name
            )
            container.stop()
            container.remove()
            self.logger(
                f"Wearable data retrieval container {Colorizer.blue(self.config.wearable_data_retrieval_container_name)} removed"
            )
        except DockerSDKError:
            self.logger.warning(
                f"Unable to stop and remove wearable data retrieval container {Colorizer.blue(self.config.wearable_data_retrieval_container_name)}"
            )

        try:
            network = self.get_network()
            network.remove()
            self.logger(
                f"Docker network {Colorizer.blue(self.config.network_name)} removed"
            )
        except DockerSDKError:
            self.logger.warning(
                f"Unable to remove docker network {Colorizer.blue(self.config.network_name)}"
            )
