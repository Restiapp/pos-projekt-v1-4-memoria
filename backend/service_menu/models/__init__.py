"""
Models Package - SQLAlchemy ORM Models
Module 0: Terméktörzs és Menü

Ez a package tartalmazza az összes adatbázis modellt a menu service-hez.

Importálás:
    from backend.service_menu.models import Category, Product, ModifierGroup, ...
"""

# Import Base first
from backend.service_menu.models.base import Base

# Import all models
from backend.service_menu.models.category import Category
from backend.service_menu.models.product import Product
from backend.service_menu.models.image_asset import ImageAsset
from backend.service_menu.models.modifier_group import ModifierGroup
from backend.service_menu.models.modifier import Modifier
from backend.service_menu.models.associations import product_modifier_group_associations
from backend.service_menu.models.channel_visibility import ChannelVisibility

# Export all models
__all__ = [
    'Base',
    'Category',
    'Product',
    'ImageAsset',
    'ModifierGroup',
    'Modifier',
    'product_modifier_group_associations',
    'ChannelVisibility',
]
