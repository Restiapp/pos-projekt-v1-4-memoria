"""increase background_image_url length for gradient patterns

Revision ID: manual_002
Revises: manual_001
Create Date: 2025-11-23 06:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'manual_002'
down_revision: Union[str, None] = 'manual_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Increase background_image_url column length from 255 to 1000
    # This is needed to support long gradient pattern strings
    op.alter_column('rooms', 'background_image_url',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=True)


def downgrade() -> None:
    # Revert to original length
    op.alter_column('rooms', 'background_image_url',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=True)
