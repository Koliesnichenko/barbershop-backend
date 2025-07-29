"""Rename appointments_addons to appointment_addon

Revision ID: 4ebfc26fbbc9
Revises: d057f569f3fc
Create Date: 2025-05-28 17:02:17.695430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ebfc26fbbc9'
down_revision: Union[str, None] = 'd057f569f3fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('appointments_addons', 'appointment_addon')


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('appointment_addon', 'appointments_addons')
