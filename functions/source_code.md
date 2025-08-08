# Source Code Organization and Structure

## Source Code File and Folder Structure

All Lambda functions should follow a consistent source code organization pattern:

```plaintext
src/
├── __init__.py                   # Package initialization
├── config.py                     # Configuration handling
├── lambda_handler.py             # AWS Lambda entry point
├── {function_name}_agent.py      # Main business logic agent class
├── backend/                      # Backend framework integration
└── utils/                        # Utility modules and helpers
    ├── __init__.py               # Utils package with clean exports
    ├── {utility_name}.py         # Individual utility modules
    └── exceptions.py             # Centralized custom exceptions
    └── messages.py               # Centralized message definitions
```

**Key Requirements:**

- Use descriptive, snake_case naming for all files and directories
- Separate concerns: configuration, handler, agent, utilities, and backend integrations
- Maintain clean package boundaries with proper `__init__.py` exports

## Configuration Handling

- Each function implements a `config.py` file that validates the environment and loads the agent config
- A module-level constant `LOCAL` determines whether the function is running locally or in Lambda:

   ```py
   LOCAL = os.getenv("LOCAL", "false") == "true"
   ```

- Module-level checks all required environment variables in local or Lambda environments raise a `ValueError` if the environment is not properly configured.
- Configuration is defined as `TypedDict`s:

    ```py
    class DBConfig(TypedDict):
        uri: str
        use_iam: bool


    class S3Config(TypedDict):
        bucket_name: str


    class AgentConfig(TypedDict):
        db: DBConfig
        s3: S3Config
        log_level: str
    ```

- `config.py` includes one function `load_config` that returns an `AgentConfig` typed dictionary.
- Secrets are stored in AWS Secrets Manager and retrieved using `*_SECRET_NAME` environment variables and the `SecretProvider` generic class:

    ```py
    class FitbitSecret(TypedDict):
        CLIENT_ID: str
        CLIENT_SECRET_KEY: str


    def load_config() -> AgentConfig:
        fitbit_secret = None
        if fitbit_secret_name := os.getenv("FITBIT_SECRET_NAME"):
            fitbit_secret = SecretProvider[FitbitConfig](fitbit_secret_name).get_secret()
    ```

## Agent

- Each function implements a main agent class (`{FunctionName}Agent`)
- The agent initializes all providers and utilities in `__init__`.
- Depending on the use case, it may have a single `run` entrypoint or CRUD endpoints
- The agent follows test-driven development principles with separate functions for each workflow step for simplified mocking:

    ```py
    class Agent:
        def __init__(self, config: AgentConfig):
            # Loads all providers and configuration

        # Define individual steps in the workflow

        def run(self) -> AgentResponse:
            # Orchestrates the workflow
    ```

## Utilities

- Organize utilities by responsibility (e.g., `SecretManager`, `S3FileManager`)
- Each utility class has a single, well-defined purpose
- Utilities are stateless and thread-safe
- Utilities use custom exceptions for error handling

    ```py
    # exceptions.py
    class S3FileManagerError(Exception):
        def __init__(self, message: str):
            self.message = message
            super().__init__(message)

        def __str__(self):
            return f"Error in S3 File Manager: {self.message}"

    # s3_file_manager.py
    class S3FileManager:
        def do_something(self) -> None:
            try:
                ...
            except SomeError as e:
                raise S3FileManagerError("Some error.") from e
            except Exception as e:
                raise S3FileManagerError("Unknown error.") from e
    ```

- Export utilities through a clean `utils/__init__.py` interface

## Messages

- Centralize all user-facing messages in `utils/messages.py`
- Use message classes with class methods for formatting
- Support parameterized messages with consistent formatting
- Separate messages by component/context, for example:

    ```py
    class S3FileManagerMessage:
        DOWNLOAD_SUCCESSFUL = "Successfully downloaded object {object_key} to {location}."

        @classmethod
        def download_successful(cls, object_key: str, location: str) -> str:
            return cls.DOWNLOAD_SUCCESSFUL.format(object_key=object_key, location=location)
    ```

## Handler (`lambda_handler.py`)

- The handler focuses only on Lambda integration and error handling
- Agent contains all business logic and orchestration
- Clear separation between request routing and implementation
- The handler logs exceptions and uploads logs to S3:

    ```python
    def lambda_handler(event: dict[str, Any], context: Any) -> None:
        logger.info(f"Received event: {event}")

        try:
            # Load config
            # Run the agent/route to relevant CRUD handlers
            # Return a successful response

        except Exception as e:
            # Log the error
            # Return a failed response

        finally:
            try:
                # Upload logs to S3
            except Exception:
                # Log the error
    ```
