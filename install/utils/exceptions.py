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


class AwsProviderError(Exception):
    """
    Exception raised for errors in AWS provider operations.

    Indicates failures when interacting with AWS services.
    """


class LocalProviderError(Exception):
    """
    Exception raised for errors in local provider operations.

    Indicates failures when interacting with local resources.
    """


class ProjectConfigError(Exception):
    """
    Exception raised for errors in project configuration.

    Indicates failures when loading, parsing, or validating project settings.
    """


class ResourceManagerError(Exception):
    """
    Exception raised for errors in resource manager operations.

    Indicates failures when managing application resources.
    """


class CancelInstallation(Exception):
    """
    Exception raised to cancel the installation process.

    Indicates a user-initiated cancellation of the installation.
    """


class UninstallError(Exception):
    """
    Exception raised for errors in uninstallation process.

    Indicates failures when removing application resources.
    """


class SubprocessError(Exception):
    """
    Exception raised for errors in subprocess execution.

    Indicates failures when running external commands.
    """


class DockerSDKError(Exception):
    """
    Exception raised for errors in Docker SDK operations.

    Indicates failures when interacting with Docker API.
    """
