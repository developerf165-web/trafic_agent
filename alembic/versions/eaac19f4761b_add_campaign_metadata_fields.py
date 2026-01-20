"""add_campaign_metadata_fields

Revision ID: eaac19f4761b
Revises: 113e8aa25ef0
Create Date: 2026-01-16 22:29:23.784870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eaac19f4761b'
down_revision: Union[str, Sequence[str], None] = '113e8aa25ef0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
