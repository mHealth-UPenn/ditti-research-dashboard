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
