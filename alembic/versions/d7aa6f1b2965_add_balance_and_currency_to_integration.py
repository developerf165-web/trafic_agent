"""add_balance_and_currency_to_integration

Revision ID: d7aa6f1b2965
Revises: f0531eaadde1
Create Date: 2026-01-17 01:22:28.371061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7aa6f1b2965'
down_revision: Union[str, Sequence[str], None] = 'f0531eaadde1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
