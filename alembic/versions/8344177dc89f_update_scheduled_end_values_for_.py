"""Update scheduled_end values for existing appointments

Revision ID: 8344177dc89f
Revises: ab5a81696f90
Create Date: 2025-07-07 13:50:33.520661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8344177dc89f'
down_revision: Union[str, None] = 'ab5a81696f90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
            UPDATE appointments
            SET scheduled_end = scheduled_time + (total_duration * interval '1 minute')
            WHERE scheduled_end = scheduled_time
        """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
