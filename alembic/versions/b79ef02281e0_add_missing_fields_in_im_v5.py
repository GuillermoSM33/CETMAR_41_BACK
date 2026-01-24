"""add missing fields in IM_v5

Revision ID: b79ef02281e0
Revises: df614254f386
Create Date: 2026-01-24 18:08:00.267450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'b79ef02281e0'
down_revision: Union[str, Sequence[str], None] = 'df614254f386'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    existing_cols = {c["name"] for c in inspector.get_columns("identities")}

    if "Midle_Name" not in existing_cols:
        op.add_column("identities", sa.Column("Midle_Name", sa.String(length=100), nullable=True))
    if "Last_Name" not in existing_cols:
        op.add_column("identities", sa.Column("Last_Name", sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    existing_cols = {c["name"] for c in inspector.get_columns("identities")}

    if "Last_Name" in existing_cols:
        op.drop_column("identities", "Last_Name")
    if "Midle_Name" in existing_cols:
        op.drop_column("identities", "Midle_Name")
