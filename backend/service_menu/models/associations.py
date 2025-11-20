"""
Association Tables - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

Many-to-Many kapcsolati táblák a termékek és más entitások között.
"""

from sqlalchemy import Table, Column, Integer, ForeignKey

from backend.service_menu.models.base import Base


# Many-to-Many association table between products and modifier_groups
product_modifier_group_associations = Table(
    'product_modifier_group_associations',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('modifier_groups.id'), primary_key=True)
)


# Many-to-Many association table between products and allergens
product_allergen_associations = Table(
    'product_allergen_associations',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    Column('allergen_id', Integer, ForeignKey('allergens.id', ondelete='CASCADE'), primary_key=True)
)
