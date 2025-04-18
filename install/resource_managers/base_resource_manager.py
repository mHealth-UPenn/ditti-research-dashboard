from install.utils.types import Env


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
        pass

    def on_end_uninstall(self) -> None:
        """Run after resource deletion."""
        pass

    def dev_uninstall(self) -> None:
        """Uninstall the resources in development mode."""
        pass

    def staging_uninstall(self) -> None:
        """Uninstall the resources in staging mode."""
        pass

    def prod_uninstall(self) -> None:
        """Uninstall the resources in production mode."""
        pass
