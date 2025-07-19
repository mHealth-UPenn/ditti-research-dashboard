class DBBootstrapperAgentMessage:
    """Message types for the database bootstrapper agent."""

    CREATE_SUCCESS = "Database upgraded and configured successfully."
    CREATE_ERROR = "Error in Create request: {error}"
    UPDATE_SUCCESS = "Database upgraded."
    UPDATE_ERROR = "Error in Update request: {error}"
    DELETE_SUCCESS = "Skipping bootstrap on delete."

    @classmethod
    def create_success(cls) -> str:
        return cls.CREATE_SUCCESS

    @classmethod
    def create_error(cls, error: str) -> str:
        return cls.CREATE_ERROR.format(error=error)

    @classmethod
    def update_success(cls) -> str:
        return cls.UPDATE_SUCCESS

    @classmethod
    def update_error(cls, error: str) -> str:
        return cls.UPDATE_ERROR.format(error=error)

    @classmethod
    def delete_success(cls) -> str:
        return cls.DELETE_SUCCESS


class DataLoaderMessage:
    """Messages for the data loader."""

    TABLE_NOT_FOUND = "Table {table_name} not found"
    ROWS_INSERTED = "Inserted {rows_inserted} rows into {table_name}."
    DATA_COMMITTED = "All data has been committed successfully!"

    @classmethod
    def table_not_found(cls, table_name: str) -> str:
        return cls.TABLE_NOT_FOUND.format(table_name=table_name)

    @classmethod
    def rows_inserted(cls, rows_inserted: int, table_name: str) -> str:
        return cls.ROWS_INSERTED.format(
            rows_inserted=rows_inserted, table_name=table_name
        )

    @classmethod
    def data_committed(cls) -> str:
        return cls.DATA_COMMITTED


class DatabaseManagerTextClause:
    GET_USER_EXISTS = "SELECT 1 FROM pg_roles WHERE rolname = :iam_username"
    GET_CURRENT_DATABASE = "SELECT current_database()"
    CREATE_USER = "CREATE USER {iam_username} WITH LOGIN"
    GRANT_IAM_TO_USER = "GRANT rds_iam TO {iam_username}"
    GRANT_CONNECT_TO_DATABASE = (
        "GRANT CONNECT ON DATABASE {database} TO {iam_username}"
    )
    GRANT_USAGE_TO_SCHEMA = "GRANT USAGE ON SCHEMA public TO {iam_username}"
    GRANT_ALL_PRIVILEGES_TO_TABLES = (
        "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {iam_username}"
    )
    GRANT_ALL_PRIVILEGES_TO_SEQUENCES = (
        "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {iam_username}"
    )
    ALTER_DEFAULT_PRIVILEGES_TO_TABLES = "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {iam_username}"
    TEST_IAM_CONNECTION = (
        "SELECT 1 as test, current_user as user, current_database() as db"
    )

    @classmethod
    def get_user_exists(cls) -> str:
        return cls.GET_USER_EXISTS

    @classmethod
    def get_current_database(cls) -> str:
        return cls.GET_CURRENT_DATABASE

    @classmethod
    def create_user(cls, iam_username: str) -> str:
        return cls.CREATE_USER.format(iam_username=iam_username)

    @classmethod
    def grant_iam_to_user(cls, iam_username: str) -> str:
        return cls.GRANT_IAM_TO_USER.format(iam_username=iam_username)

    @classmethod
    def grant_connect_to_database(cls, database: str, iam_username: str) -> str:
        return cls.GRANT_CONNECT_TO_DATABASE.format(
            database=database, iam_username=iam_username
        )

    @classmethod
    def grant_usage_to_schema(cls, iam_username: str) -> str:
        return cls.GRANT_USAGE_TO_SCHEMA.format(iam_username=iam_username)

    @classmethod
    def grant_all_privileges_to_tables(cls, iam_username: str) -> str:
        return cls.GRANT_ALL_PRIVILEGES_TO_TABLES.format(
            iam_username=iam_username
        )

    @classmethod
    def grant_all_privileges_to_sequences(cls, iam_username: str) -> str:
        return cls.GRANT_ALL_PRIVILEGES_TO_SEQUENCES.format(
            iam_username=iam_username
        )

    @classmethod
    def alter_default_privileges_to_tables(cls, iam_username: str) -> str:
        return cls.ALTER_DEFAULT_PRIVILEGES_TO_TABLES.format(
            iam_username=iam_username
        )

    @classmethod
    def test_iam_connection(cls) -> str:
        return cls.TEST_IAM_CONNECTION


class SequenceManagerMessage:
    """Messages for the sequence manager."""

    SEQUENCE_RESET = "Reset sequence for {table_name} to {max_id}."
    SEQUENCE_NOT_FOUND = "No sequence found for {table_name}."
    SEQUENCE_RESET_SUCCESS = "All sequences have been reset successfully!"

    @classmethod
    def sequence_reset(cls, table_name: str, max_id: int) -> str:
        return cls.SEQUENCE_RESET.format(table_name=table_name, max_id=max_id)

    @classmethod
    def sequence_not_found(cls, table_name: str) -> str:
        return cls.SEQUENCE_NOT_FOUND.format(table_name=table_name)

    @classmethod
    def sequence_reset_success(cls) -> str:
        return cls.SEQUENCE_RESET_SUCCESS
