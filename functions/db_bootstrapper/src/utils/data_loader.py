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


from flask import Flask
from sqlalchemy import MetaData, Table

from functions.db_bootstrapper.src.utils.messages import DataLoaderMessage
from src.backend.extensions import db
from src.utils.data_processor import DataProcessor
from src.utils.database_session_manager import DatabaseSessionManager
from src.utils.file_reader import FileReader
from src.utils.sequence_manager import SequenceManager


class DataLoader:
    """Main class for loading data into the database."""

    def __init__(self, app: Flask):
        self.app = app
        self.file_reader = FileReader()
        self.session_manager = DatabaseSessionManager(app)

    def load_data(self, json_file: str) -> list[str]:
        """
        Load data from a JSON file into the database.

        Args:
            json_file: The path to the JSON file containing the data.

        Returns
        -------
            List of status messages from the loading process.
        """
        status_messages = []

        # Load JSON data
        data = self.file_reader.read_json(json_file)
        data.pop("alembic_version", None)

        with self.app.app_context():
            session = self.session_manager.get_session()
            meta = MetaData()
            meta.reflect(bind=db.engine)

            # Insert data for each table
            for table_name, rows in data.items():
                if table_name not in meta.tables:
                    status_messages.append(
                        DataLoaderMessage.table_not_found(table_name)
                    )
                    continue

                table = Table(table_name, meta)
                rows_inserted = 0

                for row in rows:
                    cleaned_row = DataProcessor.clean_row_data(row)
                    stmt = table.insert().values(**cleaned_row)
                    session.execute(stmt)
                    rows_inserted += 1

                status_messages.append(
                    DataLoaderMessage.rows_inserted(rows_inserted, table_name)
                )

            # Commit all changes
            session.commit()
            status_messages.append(DataLoaderMessage.data_committed())

            # Fix sequences after data insertion
            sequence_manager = SequenceManager(session)
            sequence_messages = sequence_manager.fix_sequences()
            status_messages.extend(sequence_messages)

            self.session_manager.close_session()

        return status_messages
