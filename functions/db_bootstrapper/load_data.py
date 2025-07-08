# Disable linter warnings for print statements (quick fix for logging issues with alembic)
# ruff: noqa: T201

import json
import re
from datetime import datetime
from typing import Any

from flask import Flask
from sqlalchemy import MetaData, Table, text
from sqlalchemy.orm import Session, sessionmaker

from backend.extensions import db


def _fix_sequences(session: Session):
    """
    Reset database sequences to the maximum ID value + 1 for each table.

    This ensures that future auto-increment inserts will use proper sequential IDs.
    """
    try:
        # Get all tables with primary keys
        result = session.execute(
            text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        )

        tables = [row[0] for row in result]

        for table_name in tables:
            # Check if the table has an id column
            result = session.execute(
                text(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                AND column_name = 'id'
            """)  # noqa: S608
            )

            if result.fetchone():
                # Get the maximum ID value for this table
                result = session.execute(
                    text(f"SELECT MAX(id) FROM {table_name}")  # noqa: S608
                )
                max_id = result.fetchone()[0]

                if max_id is not None:
                    # Reset the sequence for this table
                    sequence_name = f"{table_name}_id_seq"

                    # Check if sequence exists
                    result = session.execute(
                        text(f"""
                        SELECT sequence_name
                        FROM information_schema.sequences
                        WHERE sequence_name = '{sequence_name}'
                    """)  # noqa: S608
                    )

                    if result.fetchone():
                        # Reset the sequence to max_id + 1
                        session.execute(
                            text(
                                f"SELECT setval('{sequence_name}', {max_id + 1})"
                            )
                        )
                        print(f"Reset sequence for {table_name} to {max_id + 1}")
                    else:
                        print(f"No sequence found for {table_name}")
                else:
                    print(f"No data in table {table_name}")

        session.commit()
        print("All sequences have been reset successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error fixing sequences: {e}")
        raise


def load_data(app: Flask, json_file: str):
    """
    Load data from a JSON file into a database.

    Args:
        app: The Flask application with configured database.
        json_file: The path to the JSON file containing the data.
    """
    # Load JSON data
    with open(json_file) as f:
        data: dict[str, list[dict[str, Any]]] = json.load(f)

    data.pop("alembic_version", None)

    with app.app_context():
        session = sessionmaker(bind=db.engine)()
        meta = MetaData()
        meta.reflect(bind=db.engine)

        # Insert data for each table
        for table_name, rows in data.items():
            if table_name not in meta.tables:
                print(f"Table {table_name} not found")
                continue

            table = Table(table_name, meta)

            for row in rows:
                # Convert any None values to NULL
                cleaned_row = {
                    k: (v if v is not None else None) for k, v in row.items()
                }

                # Convert iso format to datetime
                for key, value in cleaned_row.items():
                    if isinstance(value, str) and re.match(
                        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}", value
                    ):
                        cleaned_row[key] = datetime.fromisoformat(value)

                # Insert the row
                stmt = table.insert().values(**cleaned_row)
                session.execute(stmt)

        # Commit all changes
        session.commit()

        # Fix sequences after data insertion
        print("Fixing database sequences...")
        _fix_sequences(session)

        session.close()
