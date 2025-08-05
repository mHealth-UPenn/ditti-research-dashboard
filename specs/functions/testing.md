# Testing

Lambda functions must include comprehensive test suites that cover unit tests, integration tests, and end-to-end testing scenarios. The testing framework uses pytest with extensive mocking and container-based testing.

## Test File and Folder Structure

```plaintext
functions/{function_name}/tests_{function_name}/
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── mock_data.json                 # Mock data for testing (if any)
├── test_{function_name}_agent.py  # Agent class tests
├── test_lambda_handler.py         # Lambda handler tests
└── tests_utils/                   # Utility test modules
    ├── __init__.py                # Utils package initialization
    ├── test_{utility_name}.py     # Individual utility tests
    └── ...                        # Additional utility tests
```

## Test Configuration (`conftest.py`)

- Add parent directories to the Python path to allow for imports from `shared`:

    ```python
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))
    ```

- Define any shared testing constants, for example:

    ```python
    POSTGRES_PASSWORD = "password"
    POSTGRES_USER = "username"
    POSTGRES_DB = "db"
    POSTGRES_PORT = 5433
    ```

## Mocking Strategy

- Define any mocks and fixtures that must be shared across multiple tests in `conftest.py`.
  - Session-scoped fixtures, like test containers:

    ```py
    @pytest.fixture(scope="session", autouse=True)
    def mock_postgres_container() -> Generator[MockPostgresContainer]:
        with MockPostgresContainer() as container:
            yield container
    ```

  - Function-scoped fixtures that are commonly reused, like test Flask clients:

    ```py
    @pytest.fixture
    def test_client() -> Generator[Flask]:
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_CONTAINER_URI
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["TESTING"] = True

        db.init_app(app)
        migrate.init_app(app, db)

        with app.app_context():
            yield app
    ```

- When a fixture is used in one module only, define it in that module only:

    ```py
    @pytest.fixture
    def db_executer(mock_connection: Mock) -> DbConnectionExecuter:
        """Create a DbConnectionExecuter instance with a mock connection."""
        return DbConnectionExecuter(mock_connection)
    ```

- Create mock modules in separate `mock_{module_name}.py` files and import them when needed:

    ```py
    # mock_file_reader.py
    def create_mock_file_reader() -> FileReader:
        """Create a mock file reader that returns the given data."""
        file_reader = FileReader()
        file_reader.read_json = Mock(return_value=load_mock_data())
        return file_reader

    # test_data_loader.py
    @pytest.fixture
    def mock_data_loader() -> DataLoader:
        data_loader = DataLoader()
        data_loader.file_reader = create_mock_file_reader()
        return data_loader
    ```

- Prefix fixtures that set up resources but yield or return `None` with `with_`:

    ```py
    @pytest.fixture
    def with_mock_tables(test_client: Flask) -> None:
        create_mock_tables()
    ```

- Always use `mock_aws` when creating mock AWS resources and use a one-resource-one-fixture pattern:

    ```py
    @pytest.fixture
    def with_mock_secret() -> Generator[str]:
        with mock_aws():
            client = boto3.client("secretsmanager")
            client.create_secret(
                Name=MOCK_SECRET_NAME,
                SecretString=json.dumps(
                    {
                        "password": POSTGRES_PASSWORD,
                        "username": POSTGRES_USER,
                    }
                ),
            )
            yield
    ```

- **Always** enforce cleanup in fixtures by using with `with` or `try`/`yield`/`finally` blocks:

    ```py
    @pytest.fixture
    def with_mock_tables(test_client: Flask) -> Generator[None]:
        db.create_all()
        try:
            yield
        finally:
            db.drop_all()
    ```
