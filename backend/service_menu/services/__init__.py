"""
Services Package - Business Logic Layer
Module 0: Terméktörzs és Menü

Ez a package tartalmazza az összes szolgáltatást a menu service-hez.

Importálás:
    from backend.service_menu.services import CategoryService
"""

from backend.service_menu.services.category_service import CategoryService

__all__ = [
    'CategoryService',
]
