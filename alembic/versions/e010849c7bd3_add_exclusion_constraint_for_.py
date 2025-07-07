"""Add exclusion constraint for appointment overlaps

Revision ID: e010849c7bd3
Revises: 8344177dc89f
Create Date: 2025-07-07 13:51:08.258322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e010849c7bd3'
down_revision: Union[str, None] = '8344177dc89f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    op.execute("""
        ALTER TABLE appointments
        ADD CONSTRAINT no_overlap_barber_time
        EXCLUDE USING gist (
            barber_id WITH =,
            tstzrange(
                scheduled_time,
                scheduled_end
            ) WITH &&
        )
        WHERE (status != 'cancelled');
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
