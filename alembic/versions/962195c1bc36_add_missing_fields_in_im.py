"""add missing fields in IM

Revision ID: 962195c1bc36
Revises: 69042d3fb7b8
Create Date: 2026-01-18 18:54:57.174754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '962195c1bc36'
down_revision: Union[str, Sequence[str], None] = '69042d3fb7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQL Server-safe / idempotent columns add (avoids failure if the column already exists)
    op.execute(
        """
        IF COL_LENGTH('dbo.identities', 'Schoolar_Control_Identity') IS NULL
        BEGIN
            ALTER TABLE dbo.identities ADD Schoolar_Control_Identity INT NULL;
        END

        IF COL_LENGTH('dbo.identities', 'Director_Identity') IS NULL
        BEGIN
            ALTER TABLE dbo.identities ADD Director_Identity INT NULL;
        END
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        IF COL_LENGTH('dbo.identities', 'Director_Identity') IS NOT NULL
        BEGIN
            ALTER TABLE dbo.identities DROP COLUMN Director_Identity;
        END

        IF COL_LENGTH('dbo.identities', 'Schoolar_Control_Identity') IS NOT NULL
        BEGIN
            ALTER TABLE dbo.identities DROP COLUMN Schoolar_Control_Identity;
        END
        """
    )
