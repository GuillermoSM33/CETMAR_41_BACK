"""add missing fields in IM2

Revision ID: cc5934b59208
Revises: 962195c1bc36
Create Date: 2026-01-18 19:03:57.736713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc5934b59208'
down_revision: Union[str, Sequence[str], None] = '962195c1bc36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTE:
    # This revision was generated with --autogenerate and included a large set of
    # destructive operations on report_card_* tables (dropping columns, indexes,
    # and foreign keys). Those operations are intentionally NOT applied here to
    # avoid accidental data loss and environment-specific FK name issues in MSSQL.
    #
    # Keep only the identity-related cleanup detected by autogenerate.
    op.execute(
        """
        IF COL_LENGTH('dbo.identities', 'Student_Identity') IS NOT NULL
        BEGIN
            ALTER TABLE dbo.identities DROP COLUMN Student_Identity;
        END
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        IF COL_LENGTH('dbo.identities', 'Student_Identity') IS NULL
        BEGIN
            ALTER TABLE dbo.identities ADD Student_Identity INT NULL;
        END
        """
    )
