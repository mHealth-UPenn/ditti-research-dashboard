"""remove password and public_id fields, update phone number format

Revision ID: 1ea7fa443990
Revises: 65a966f12056
Create Date: 2025-03-13 10:40:56.374645

"""

import re
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "1ea7fa443990"
down_revision = "65a966f12056"
branch_labels = None
depends_on = None


def upgrade():
    # Create a temp table reference for the update
    account_table = table(
        "account", column("phone_number", sa.String), column("id", sa.Integer)
    )

    with op.batch_alter_table("account", schema=None) as batch_op:
        # Drop constraints and columns we don't need anymore
        batch_op.drop_constraint("account_public_id_key", type_="unique")
        batch_op.drop_column("_password")
        batch_op.drop_column("public_id")

    # Connect to the database
    conn = op.get_bind()

    # Get all phone numbers that need to be processed
    result = conn.execute(
        sa.select([account_table.c.id, account_table.c.phone_number]).where(
            account_table.c.phone_number.isnot(None)
        )
    )

    for row in result:
        account_id = row[0]
        phone = row[1]

        # Skip if already in valid E.164 format
        if phone and re.match(r"^\+[1-9]\d{1,14}$", phone):
            continue

        # Process the phone number
        if phone:
            # Strip all non-digit characters
            digits_only = re.sub(r"\D", "", phone)

            # For US/Canada, if exactly 10 digits, add +1 prefix
            if len(digits_only) == 10:
                conn.execute(
                    account_table.update()
                    .where(account_table.c.id == account_id)
                    .values(phone_number=f"+1{digits_only}")
                )
            else:
                # If not a valid format, set to NULL
                conn.execute(
                    account_table.update()
                    .where(account_table.c.id == account_id)
                    .values(phone_number=None)
                )


def downgrade():
    # Create a temp table reference for the update
    account_table = table(
        "account",
        column("phone_number", sa.String),
        column("public_id", sa.String),
        column("_password", sa.String),
        column("id", sa.Integer),
    )

    # First, add the columns as nullable
    with op.batch_alter_table("account", schema=None) as batch_op:
        batch_op.add_column(sa.Column("public_id", sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column("_password", sa.VARCHAR(), nullable=True))

    # Connect to the database
    conn = op.get_bind()

    # Fetch all account ids
    result = conn.execute(sa.select([account_table.c.id]))
    account_ids = [row[0] for row in result]

    # Set a dummy password hash (this is a placeholder, real passwords can't be restored)
    dummy_password = (
        "$2b$12$c6AqbeZ4OLQVbzL.DF9dleOxDf6Y3QDrVJPdCZ3m0U8xdWtxRHAuW"
    )

    # Update each account individually with a unique UUID
    for account_id in account_ids:
        conn.execute(
            account_table.update()
            .where(account_table.c.id == account_id)
            .values(public_id=str(uuid.uuid4()), _password=dummy_password)
        )

    # Now make the columns NOT NULL
    with op.batch_alter_table("account", schema=None) as batch_op:
        batch_op.alter_column("public_id", nullable=False)
        batch_op.alter_column("_password", nullable=False)
        batch_op.create_unique_constraint(
            "account_public_id_key", ["public_id"]
        )

    # Get phone numbers and process them individually
    result = conn.execute(
        sa.select([account_table.c.id, account_table.c.phone_number]).where(
            account_table.c.phone_number.isnot(None)
        )
    )

    for row in result:
        account_id = row[0]
        phone = row[1]

        # Remove the +1 prefix if it exists (for US/Canada numbers)
        if phone and phone.startswith("+1"):
            conn.execute(
                account_table.update()
                .where(account_table.c.id == account_id)
                .values(phone_number=phone[2:])
            )
