"""Initial migration

Revision ID: 0f488fdf6de2
Revises: 
Create Date: 2024-12-26 12:35:08.351831
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f488fdf6de2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "CURRENCIES",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("input", sa.Float(), nullable=True),
        sa.Column("output", sa.Float(), nullable=True),
        sa.Column("balance", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "CUSTOMER",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("name", sa.Unicode(length=255), nullable=False),
        sa.Column("identite", sa.Unicode(length=255), nullable=True),
        sa.Column("telephone", sa.Unicode(length=20), nullable=True),
        sa.Column("date_naisse", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "EMPLOYEE",
        sa.Column(
            "employee_id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("carte_ident", sa.String(length=255), nullable=True),
        sa.Column("telephone", sa.String(length=20), nullable=True),
        sa.Column("date_naiss", sa.Date(), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("permission_role", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("employee_id"),
    )

    op.create_table(
        "TREASURY_OPERATIONS",
        sa.Column(
            "treasury_operations_id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("input", sa.Float(), nullable=True),
        sa.Column("output", sa.Float(), nullable=True),
        sa.Column("balance", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("treasury_operations_id"),
    )

    op.create_table(
        "DEBTS",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("debt_date", sa.Date(), nullable=False),
        sa.Column("paid_debt", sa.Float(), nullable=True),
        sa.Column("current_debt", sa.Float(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Date(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["CUSTOMER.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "DEPOSITS",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("person_name", sa.Unicode(length=255), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("deposit_date", sa.Date(), nullable=False),
        sa.Column("released_deposit", sa.Float(), nullable=True),
        sa.Column("current_debt", sa.Float(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["CUSTOMER.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("DEPOSITS")
    op.drop_table("DEBTS")
    op.drop_table("TREASURY_OPERATIONS")
    op.drop_table("EMPLOYEE")
    op.drop_table("CUSTOMER")
    op.drop_table("CURRENCIES")
    # ### end Alembic commands ###
