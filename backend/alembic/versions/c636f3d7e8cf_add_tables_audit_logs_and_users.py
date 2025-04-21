"""Add tables audit_logs and users

Revision ID: c636f3d7e8cf
Revises: 577d72bec3ce
Create Date: 2025-01-07 10:58:31.802148

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision: str = "c636f3d7e8cf"
down_revision: Union[str, None] = "577d72bec3ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(connection, table_name):
    """Check if a table exists"""
    return connection.execute(
        sa.text(
            """
            SELECT COUNT(*) 
            FROM user_tables 
            WHERE table_name = :table_name
            """
        ),
        {"table_name": table_name},
    ).scalar()


def upgrade() -> None:
    # Get database connection
    connection = op.get_bind()

    # Check if tables exist
    users_exists = table_exists(connection, "USERS")
    audit_logs_exists = table_exists(connection, "AUDIT_LOGS")

    if not users_exists:
        # Create USERS table
        op.create_table(
            "USERS",
            sa.Column(
                "id",
                sa.Integer(),
                sa.Identity(always=False, start=1, increment=1),
                nullable=False,
            ),
            sa.Column("username", sa.String(length=50), nullable=False),
            sa.Column("password", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
            sa.Column("role", sa.String(length=50), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("username"),
        )

    if not audit_logs_exists:
        # Create AUDIT_LOGS table
        op.create_table(
            "AUDIT_LOGS",
            sa.Column(
                "id",
                sa.Integer(),
                sa.Identity(always=False, start=1, increment=1),
                nullable=False,
            ),
            sa.Column("table_name", sa.String(length=100), nullable=False),
            sa.Column("operation", sa.String(length=50), nullable=False),
            sa.Column("record_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column(
                "timestamp",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("changes", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["USERS.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    connection = op.get_bind()

    # Check if tables exist before attempting to drop them
    audit_logs_exists = table_exists(connection, "AUDIT_LOGS")
    users_exists = table_exists(connection, "USERS")

    if audit_logs_exists:
        op.drop_table("AUDIT_LOGS")
    if users_exists:
        op.drop_table("USERS")
