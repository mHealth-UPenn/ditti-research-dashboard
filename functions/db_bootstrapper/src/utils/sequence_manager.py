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


from sqlalchemy import text
from sqlalchemy.orm import Session

from src.utils.enums import SequenceManagerMessage


class SequenceManager:
    """Manages database sequence operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_tables_with_id_columns(self) -> list[str]:
        """Get all tables that have an 'id' column."""
        result = self.session.execute(
            text("""
            SELECT DISTINCT t.table_name
            FROM information_schema.tables t
            JOIN information_schema.columns c ON t.table_name = c.table_name
            WHERE t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
            AND c.column_name = 'id'
        """)
        )
        return [row[0] for row in result]

    def get_max_id_for_table(self, table_name: str) -> int:
        """Get the maximum ID value for a given table."""
        result = self.session.execute(
            text(f"SELECT MAX(id) FROM {table_name}")  # noqa: S608
        )
        max_id = result.fetchone()[0]
        return max_id if max_id is not None else 0

    def sequence_exists(self, sequence_name: str) -> bool:
        """Check if a sequence exists."""
        result = self.session.execute(
            text(f"""
            SELECT sequence_name
            FROM information_schema.sequences
            WHERE sequence_name = '{sequence_name}'
        """)  # noqa: S608
        )
        return result.fetchone() is not None

    def reset_sequence(self, sequence_name: str, value: int):
        """Reset a sequence to a specific value."""
        self.session.execute(text(f"SELECT setval('{sequence_name}', {value})"))

    def fix_sequences(self) -> list[str]:
        """
        Reset database sequences to the maximum ID value + 1 for each table.

        Returns
        -------
            List of status messages for each table processed.
        """
        status_messages = []

        tables = self.get_tables_with_id_columns()

        for table_name in tables:
            max_id = self.get_max_id_for_table(table_name)
            sequence_name = f"{table_name}_id_seq"

            if self.sequence_exists(sequence_name):
                self.reset_sequence(sequence_name, max_id + 1)
                status_messages.append(
                    SequenceManagerMessage.sequence_reset(table_name, max_id + 1)
                )
            else:
                status_messages.append(
                    SequenceManagerMessage.sequence_not_found(table_name)
                )

        self.session.commit()
        status_messages.append(SequenceManagerMessage.sequence_reset_success())

        return status_messages
