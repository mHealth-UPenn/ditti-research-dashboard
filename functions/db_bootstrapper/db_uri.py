class DbUri:
    """A database URI.

    This class is used to store the database URI and the username and password
    and enable simplified access to URI components.

    Args
    ----
        hostname: The hostname of the database.
        port: The port of the database.
        database: The name of the database.
        username: The username to use to connect to the database.
        password: The password to use to connect to the database.
    """

    def __init__(
        self,
        *,
        hostname: str,
        port: str,
        database: str,
        username: str,
        password: str | None = None,
    ):
        if password is None:
            self.uri = f"postgresql://{username}@{hostname}:{port}/{database}"
        else:
            self.uri = (
                f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
            )
        self.has_password = password is not None
        self.hostname = hostname
        self.port = int(port)
        self.database = database
        self.username = username

    def __str__(self):
        if not self.has_password:
            return self.uri
        return f"postgresql://{self.username}:***@{self.hostname}:{self.port}/{self.database}"
