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

    def on_start(self) -> None:
        """Run before resource creation."""
        pass

    def on_end(self) -> None:
        """Run after resource creation."""
        pass

    def dev(self) -> None:
        """Create resources in development mode."""
        pass

    def staging(self) -> None:
        """Create resources in staging mode."""
        pass

    def prod(self) -> None:
        """Create resources in production mode."""
        pass
