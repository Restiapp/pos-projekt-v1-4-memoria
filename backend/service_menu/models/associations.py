"""
Association Tables - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

Many-to-Many kapcsolati tábla a termékek és módosító csoportok között.
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
