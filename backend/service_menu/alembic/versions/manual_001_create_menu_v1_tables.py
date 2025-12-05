"""create menu v1 tables

Revision ID: manual_001
Revises:
Create Date: 2025-12-05 10:00:00.000000

Sprint D6: Menu Model V1 Implementation
Creates all 6 new menu tables:
- menu_categories
- menu_items
- menu_item_variants
- modifier_groups
- modifier_options
- modifier_assignments
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
    """Create all Menu V1 tables"""

    # 1. Create SelectionType enum
    selection_type_enum = postgresql.ENUM(
        'REQUIRED_SINGLE',
        'OPTIONAL_SINGLE',
        'OPTIONAL_MULTIPLE',
        name='selectiontype',
        create_type=True
    )
    selection_type_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create menu_categories table
    op.create_table(
        'menu_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['menu_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_menu_categories_parent_id', 'menu_categories', ['parent_id'])
    op.create_index('ix_menu_categories_is_active', 'menu_categories', ['is_active'])

    # 3. Create menu_items table
    op.create_table(
        'menu_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_price_gross', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('vat_rate_dine_in', sa.Numeric(precision=5, scale=2), server_default='5.00', nullable=True),
        sa.Column('vat_rate_takeaway', sa.Numeric(precision=5, scale=2), server_default='27.00', nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('channel_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['menu_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_menu_items_category_id', 'menu_items', ['category_id'])
    op.create_index('ix_menu_items_is_active', 'menu_items', ['is_active'])

    # 4. Create menu_item_variants table
    op.create_table(
        'menu_item_variants',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price_delta', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['menu_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_menu_item_variants_item_id', 'menu_item_variants', ['item_id'])
    op.create_index('ix_menu_item_variants_is_active', 'menu_item_variants', ['is_active'])

    # 5. Create modifier_groups table
    op.create_table(
        'modifier_groups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('selection_type', selection_type_enum, nullable=False, server_default='OPTIONAL_MULTIPLE'),
        sa.Column('min_select', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_select', sa.Integer(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_modifier_groups_is_active', 'modifier_groups', ['is_active'])

    # 6. Create modifier_options table
    op.create_table(
        'modifier_options',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price_delta_gross', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['modifier_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_modifier_options_group_id', 'modifier_options', ['group_id'])
    op.create_index('ix_modifier_options_is_active', 'modifier_options', ['is_active'])

    # 7. Create modifier_assignments table
    op.create_table(
        'modifier_assignments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('applies_to_variants', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_required_override', sa.Boolean(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['modifier_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['menu_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['menu_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            '(item_id IS NOT NULL AND category_id IS NULL) OR (item_id IS NULL AND category_id IS NOT NULL)',
            name='check_either_item_or_category'
        )
    )
    op.create_index('ix_modifier_assignments_group_id', 'modifier_assignments', ['group_id'])
    op.create_index('ix_modifier_assignments_item_id', 'modifier_assignments', ['item_id'])
    op.create_index('ix_modifier_assignments_category_id', 'modifier_assignments', ['category_id'])


def downgrade() -> None:
    """Drop all Menu V1 tables"""
    op.drop_index('ix_modifier_assignments_category_id', table_name='modifier_assignments')
    op.drop_index('ix_modifier_assignments_item_id', table_name='modifier_assignments')
    op.drop_index('ix_modifier_assignments_group_id', table_name='modifier_assignments')
    op.drop_table('modifier_assignments')

    op.drop_index('ix_modifier_options_is_active', table_name='modifier_options')
    op.drop_index('ix_modifier_options_group_id', table_name='modifier_options')
    op.drop_table('modifier_options')

    op.drop_index('ix_modifier_groups_is_active', table_name='modifier_groups')
    op.drop_table('modifier_groups')

    op.drop_index('ix_menu_item_variants_is_active', table_name='menu_item_variants')
    op.drop_index('ix_menu_item_variants_item_id', table_name='menu_item_variants')
    op.drop_table('menu_item_variants')

    op.drop_index('ix_menu_items_is_active', table_name='menu_items')
    op.drop_index('ix_menu_items_category_id', table_name='menu_items')
    op.drop_table('menu_items')

    op.drop_index('ix_menu_categories_is_active', table_name='menu_categories')
    op.drop_index('ix_menu_categories_parent_id', table_name='menu_categories')
    op.drop_table('menu_categories')

    # Drop enum type
    sa.Enum(name='selectiontype').drop(op.get_bind(), checkfirst=True)
