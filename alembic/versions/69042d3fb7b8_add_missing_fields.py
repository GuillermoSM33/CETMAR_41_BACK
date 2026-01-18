"""add missing fields

Revision ID: 69042d3fb7b8
Revises: ff82e1a76907
Create Date: 2026-01-17 21:20:33.882833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69042d3fb7b8'
down_revision: Union[str, Sequence[str], None] = 'ff82e1a76907'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
