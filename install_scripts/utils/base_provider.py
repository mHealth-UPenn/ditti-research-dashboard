from collections import abc
from install_scripts.utils import Env


class BaseProvider:
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
        """Run when the script starts."""
        ...

    @abc.abstractmethod
    def on_end(self) -> None:
        """Run when the script ends."""
        ...

    @abc.abstractmethod
    def dev(self) -> None:
        """Run the provider in development mode."""
        ...

    @abc.abstractmethod
    def staging(self) -> None:
        """Run the provider in staging mode."""
        ...

    @abc.abstractmethod
    def prod(self) -> None:
        """Run the provider in production mode."""
        ...
