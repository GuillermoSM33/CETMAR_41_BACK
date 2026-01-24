"""baseline

Revision ID: df614254f386
Revises: 
Create Date: 2026-01-24 18:07:37.191319

"""
from typing import Sequence, Union

from alembic import op


def _get_metadata():
    # Alembic loads revision files without running env.py (e.g. `alembic heads`),
    # so keep project imports lazy and ensure repo root is on sys.path.
    import os
    import sys

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from infrastructure.persistence.models.base import Base
    import infrastructure.persistence.models  # noqa: F401

    return Base.metadata


# revision identifiers, used by Alembic.
revision: str = 'df614254f386'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    _get_metadata().create_all(bind=bind)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    _get_metadata().drop_all(bind=bind)
