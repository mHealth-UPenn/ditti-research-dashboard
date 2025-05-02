# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from install.utils.types import Env


class BaseResourceManager:
    """
    Base class for resource managers in the installation system.

    Provides common functionality and interface for managing different
    types of resources during installation and uninstallation.
    """

    def run(self, env: Env = "dev") -> None:
        """Run the provider."""
        self.on_start()

        match env:
            case "dev":
                self.dev()
            case "staging":
                self.staging()
            case "prod":
                self.prod()
            case _:
                raise ValueError(f"Invalid environment: {env}")

        self.on_end()

    def on_start(self) -> None:
        """Run before resource creation."""

    def on_end(self) -> None:
        """Run after resource creation."""

    def dev(self) -> None:
        """Create resources in development mode."""

    def staging(self) -> None:
        """Create resources in staging mode."""

    def prod(self) -> None:
        """Create resources in production mode."""

    def uninstall(self, env: Env = "dev") -> None:
        """Uninstall the resources."""
        self.on_start_uninstall()

        match env:
            case "dev":
                self.dev_uninstall()
            case "staging":
                self.staging_uninstall()
            case "prod":
                self.prod_uninstall()
            case _:
                raise ValueError(f"Invalid environment: {env}")

        self.on_end_uninstall()

    def on_start_uninstall(self) -> None:
        """Run before resource deletion."""

    def on_end_uninstall(self) -> None:
        """Run after resource deletion."""

    def dev_uninstall(self) -> None:
        """Uninstall the resources in development mode."""

    def staging_uninstall(self) -> None:
        """Uninstall the resources in staging mode."""

    def prod_uninstall(self) -> None:
        """Uninstall the resources in production mode."""
