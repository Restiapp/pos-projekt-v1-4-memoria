"""
Menu Model V1 - SQLAlchemy ORM
Sprint D6: Menu Structure Implementation

This module contains the new menu domain models:
- MenuCategory: Hierarchical category structure
- MenuItem: Core menu items with channel support
- MenuItemVariant: Product variants (e.g. gluten-free options)
- ModifierGroup: Modifier/extra groups (e.g. "Bun type", "Extra toppings")
- ModifierOption: Individual options within a group
- ModifierAssignment: Links modifier groups to items/categories

These replace the legacy Product, Category, ModifierGroup, Modifier models.
"""

import enum
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, TIMESTAMP, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import CompatibleJSON from service_orders for cross-database compatibility
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from service_orders.models.database import CompatibleJSON

from backend.service_menu.models.base import Base


class SelectionType(enum.Enum):
    """Enum for modifier group selection types"""
    REQUIRED_SINGLE = "REQUIRED_SINGLE"  # Must select exactly 1 (e.g. bun type)
    OPTIONAL_SINGLE = "OPTIONAL_SINGLE"  # Can select 0 or 1 (e.g. extra cheese)
    OPTIONAL_MULTIPLE = "OPTIONAL_MULTIPLE"  # Can select 0 to N (e.g. toppings)


class MenuCategory(Base):
    """
    Menu Category Model

    Supports hierarchical structure with parent_id for subcategories.
    Used to organize menu items (e.g. "Hamburgers", "Appetizers", "Drinks")
    """
    __tablename__ = 'menu_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('menu_categories.id', ondelete='SET NULL'), nullable=True)
    position = Column(Integer, default=0, nullable=False)  # Display order
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    parent = relationship('MenuCategory', remote_side=[id], backref='subcategories')
    items = relationship('MenuItem', back_populates='category')
    modifier_assignments = relationship('ModifierAssignment', back_populates='category')

    def __repr__(self):
        return f"<MenuCategory(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"


class MenuItem(Base):
    """
    Menu Item Model

    Core menu item with pricing, VAT rates, and channel availability.
    Supports multiple channels (dine_in, takeaway, delivery) with different VAT rates.
    """
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('menu_categories.id', ondelete='SET NULL'), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    base_price_gross = Column(Numeric(10, 2), nullable=False)  # Gross price including VAT
    vat_rate_dine_in = Column(Numeric(5, 2), default=5.00)  # 5% for dine-in (Hungary)
    vat_rate_takeaway = Column(Numeric(5, 2), default=27.00)  # 27% for takeaway (Hungary)
    is_active = Column(Boolean, default=True, nullable=False)

    # Channel availability stored as JSON: {"dine_in": true, "takeaway": true, "delivery": false}
    channel_flags = Column(CompatibleJSON, nullable=True, default={})

    # Additional metadata (images, allergens, translations, etc.)
    metadata_json = Column(CompatibleJSON, nullable=True, default={})

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship('MenuCategory', back_populates='items')
    variants = relationship('MenuItemVariant', back_populates='item', cascade='all, delete-orphan')
    modifier_assignments = relationship('ModifierAssignment', back_populates='item')

    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.base_price_gross})>"


class MenuItemVariant(Base):
    """
    Menu Item Variant Model

    Represents variants of a base item (e.g. "Gluten-free Hawaii Burger").
    Each variant has a price delta relative to the base item price.
    """
    __tablename__ = 'menu_item_variants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('menu_items.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)  # e.g. "Gluténmentes Hawaii Burger"
    price_delta = Column(Numeric(10, 2), default=0.00, nullable=False)  # +/- price relative to base
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    item = relationship('MenuItem', back_populates='variants')

    def __repr__(self):
        return f"<MenuItemVariant(id={self.id}, name='{self.name}', delta={self.price_delta})>"


class ModifierGroup(Base):
    """
    Modifier Group Model

    Groups of modifiers/extras (e.g. "Bun type", "Extra toppings").
    Defines selection rules (required single, optional multiple, etc.).
    """
    __tablename__ = 'modifier_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # e.g. "Zsemle típus"
    description = Column(Text, nullable=True)
    selection_type = Column(SQLEnum(SelectionType), nullable=False, default=SelectionType.OPTIONAL_MULTIPLE)
    min_select = Column(Integer, default=0, nullable=False)
    max_select = Column(Integer, nullable=True)  # NULL = unlimited
    position = Column(Integer, default=0, nullable=False)  # Display order
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    options = relationship('ModifierOption', back_populates='group', cascade='all, delete-orphan')
    assignments = relationship('ModifierAssignment', back_populates='group')

    def __repr__(self):
        return f"<ModifierGroup(id={self.id}, name='{self.name}', type={self.selection_type.value})>"


class ModifierOption(Base):
    """
    Modifier Option Model

    Individual options within a modifier group (e.g. "Sesame bun", "Extra bacon").
    Each option has a price delta relative to base price.
    """
    __tablename__ = 'modifier_options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('modifier_groups.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)  # e.g. "Szezámmagos zsemle"
    price_delta_gross = Column(Numeric(10, 2), default=0.00, nullable=False)  # +/- price
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Additional metadata (allergens, translations, etc.)
    metadata_json = Column(CompatibleJSON, nullable=True, default={})

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    group = relationship('ModifierGroup', back_populates='options')

    def __repr__(self):
        return f"<ModifierOption(id={self.id}, name='{self.name}', delta={self.price_delta_gross})>"


class ModifierAssignment(Base):
    """
    Modifier Assignment Model

    Links modifier groups to menu items or categories.
    Allows group-level or item-level modifier assignments.
    E.g. "Bun type" applies to all burgers in category,
    or "Extra toppings" applies to specific item.
    """
    __tablename__ = 'modifier_assignments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('modifier_groups.id', ondelete='CASCADE'), nullable=False)

    # Either item_id OR category_id must be set (not both)
    item_id = Column(Integer, ForeignKey('menu_items.id', ondelete='CASCADE'), nullable=True)
    category_id = Column(Integer, ForeignKey('menu_categories.id', ondelete='CASCADE'), nullable=True)

    applies_to_variants = Column(Boolean, default=True, nullable=False)  # Apply to item variants?
    is_required_override = Column(Boolean, nullable=True)  # Override group's selection_type requirement
    position = Column(Integer, default=0, nullable=False)  # Display order
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    group = relationship('ModifierGroup', back_populates='assignments')
    item = relationship('MenuItem', back_populates='modifier_assignments')
    category = relationship('MenuCategory', back_populates='modifier_assignments')

    def __repr__(self):
        target = f"item={self.item_id}" if self.item_id else f"category={self.category_id}"
        return f"<ModifierAssignment(id={self.id}, group={self.group_id}, {target})>"
