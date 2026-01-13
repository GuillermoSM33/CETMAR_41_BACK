"""add missing uacs columns

Revision ID: ff82e1a76907
Revises: 4ff13462edd1
Create Date: 2026-01-12 21:20:17.279339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff82e1a76907'
down_revision: Union[str, Sequence[str], None] = '4ff13462edd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        IF COL_LENGTH('dbo.uacs', 'Creditos') IS NULL
        BEGIN
            ALTER TABLE dbo.uacs ADD Creditos INT NULL;
        END

        IF COL_LENGTH('dbo.uacs', 'Horas_Sem') IS NULL
        BEGIN
            ALTER TABLE dbo.uacs ADD Horas_Sem INT NULL;
        END
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        IF COL_LENGTH('dbo.uacs', 'Horas_Sem') IS NOT NULL
        BEGIN
            ALTER TABLE dbo.uacs DROP COLUMN Horas_Sem;
        END

        IF COL_LENGTH('dbo.uacs', 'Creditos') IS NOT NULL
        BEGIN
            ALTER TABLE dbo.uacs DROP COLUMN Creditos;
        END
        """
    )
