"""add round_number and metadata_json to order_items

Revision ID: manual_001
Revises:
Create Date: 2024-05-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'manual_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Manual migration file for environment reference
    op.add_column('order_items', sa.Column('round_number', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('order_items', sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('order_items', 'metadata_json')
    op.drop_column('order_items', 'round_number')
