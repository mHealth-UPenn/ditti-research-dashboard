# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


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
