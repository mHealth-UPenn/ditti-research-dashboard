from collections import abc

from install_scripts.utils.types import Env


class BaseResourceManager:
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

    @abc.abstractmethod
    def on_start(self) -> None:
        """Run before resource creation."""
        ...

    @abc.abstractmethod
    def on_end(self) -> None:
        """Run after resource creation."""
        ...

    @abc.abstractmethod
    def dev(self) -> None:
        """Create resources in development mode."""
        ...

    @abc.abstractmethod
    def staging(self) -> None:
        """Create resources in staging mode."""
        ...

    @abc.abstractmethod
    def prod(self) -> None:
        """Create resources in production mode."""
        ...
