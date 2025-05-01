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
