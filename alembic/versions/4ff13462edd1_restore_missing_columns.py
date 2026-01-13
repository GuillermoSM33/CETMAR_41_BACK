"""restore missing columns

Revision ID: 4ff13462edd1
Revises: 6801b9fe5ccb
Create Date: 2026-01-12 20:44:56.460415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ff13462edd1'
down_revision: Union[str, Sequence[str], None] = '6801b9fe5ccb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This migration is intentionally idempotent.
    # Some environments may have schema drift where models reference columns
    # that were previously dropped.

    # --- uacs ---
    op.execute(
        """
IF COL_LENGTH('dbo.uacs', 'Creditos') IS NULL
    ALTER TABLE dbo.uacs ADD Creditos INT NULL;

IF COL_LENGTH('dbo.uacs', 'Horas_Sem') IS NULL
    ALTER TABLE dbo.uacs ADD Horas_Sem INT NULL;
"""
    )

    # --- report_card_items (legacy columns referenced by some model variants) ---
    op.execute(
        """
IF COL_LENGTH('dbo.report_card_items', 'Tipo_UAC') IS NULL
    ALTER TABLE dbo.report_card_items ADD Tipo_UAC VARCHAR(32) NULL;

IF COL_LENGTH('dbo.report_card_items', 'Horas_Sem') IS NULL
    ALTER TABLE dbo.report_card_items ADD Horas_Sem INT NULL;

IF COL_LENGTH('dbo.report_card_items', 'Creditos') IS NULL
    ALTER TABLE dbo.report_card_items ADD Creditos INT NULL;

IF COL_LENGTH('dbo.report_card_items', 'Periodo_Item') IS NULL
    ALTER TABLE dbo.report_card_items ADD Periodo_Item VARCHAR(64) NULL;
"""
    )

    # --- report_card_raw (legacy columns referenced by earlier migrations) ---
    op.execute(
        """
IF COL_LENGTH('dbo.report_card_raw', 'Periodo') IS NULL
    ALTER TABLE dbo.report_card_raw ADD Periodo VARCHAR(64) NULL;

IF COL_LENGTH('dbo.report_card_raw', 'Periodo_Item') IS NULL
    ALTER TABLE dbo.report_card_raw ADD Periodo_Item VARCHAR(64) NULL;

IF COL_LENGTH('dbo.report_card_raw', 'Stored_URI') IS NULL
    ALTER TABLE dbo.report_card_raw ADD Stored_URI VARCHAR(400) NULL;
"""
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Best-effort rollback (guarded).
    op.execute(
        """
IF COL_LENGTH('dbo.report_card_raw', 'Stored_URI') IS NOT NULL
    ALTER TABLE dbo.report_card_raw DROP COLUMN Stored_URI;
IF COL_LENGTH('dbo.report_card_raw', 'Periodo_Item') IS NOT NULL
    ALTER TABLE dbo.report_card_raw DROP COLUMN Periodo_Item;
IF COL_LENGTH('dbo.report_card_raw', 'Periodo') IS NOT NULL
    ALTER TABLE dbo.report_card_raw DROP COLUMN Periodo;

IF COL_LENGTH('dbo.report_card_items', 'Periodo_Item') IS NOT NULL
    ALTER TABLE dbo.report_card_items DROP COLUMN Periodo_Item;
IF COL_LENGTH('dbo.report_card_items', 'Creditos') IS NOT NULL
    ALTER TABLE dbo.report_card_items DROP COLUMN Creditos;
IF COL_LENGTH('dbo.report_card_items', 'Horas_Sem') IS NOT NULL
    ALTER TABLE dbo.report_card_items DROP COLUMN Horas_Sem;
IF COL_LENGTH('dbo.report_card_items', 'Tipo_UAC') IS NOT NULL
    ALTER TABLE dbo.report_card_items DROP COLUMN Tipo_UAC;

IF COL_LENGTH('dbo.uacs', 'Horas_Sem') IS NOT NULL
    ALTER TABLE dbo.uacs DROP COLUMN Horas_Sem;
IF COL_LENGTH('dbo.uacs', 'Creditos') IS NOT NULL
    ALTER TABLE dbo.uacs DROP COLUMN Creditos;
"""
    )
