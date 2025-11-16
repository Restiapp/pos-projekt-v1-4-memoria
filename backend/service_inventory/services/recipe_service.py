"""
Recipe Service - Business Logic Layer
Module 5: Készletkezelés

Ez a modul tartalmazza a RecipeService osztályt, amely
a receptúrák kezelésének üzleti logikáját implementálja.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from backend.service_inventory.models.recipe import Recipe
from backend.service_inventory.models.inventory_item import InventoryItem
from backend.service_inventory.schemas.recipe import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeListResponse
)


class RecipeService:
    """
    Service osztály a receptúrák kezeléséhez.

    Tartalmazza a CRUD műveleteket és az üzleti logikát
    a termék-alapanyag kapcsolatok kezeléséhez.
    """

    def __init__(self, db: Session):
        """
        Inicializálja a RecipeService-t.

        Args:
            db: SQLAlchemy Session objektum
        """
        self.db = db

    def create_recipe(self, recipe_data: RecipeCreate) -> Recipe:
        """
        Új recept létrehozása.

        Args:
            recipe_data: RecipeCreate schema az új recept adataival

        Returns:
            Recipe: A létrehozott recept

        Raises:
            ValueError: Ha az inventory_item_id nem létezik
            ValueError: Ha már létezik ilyen product_id + inventory_item_id kombináció
        """
        # Ellenőrizzük, hogy létezik-e az inventory item
        inventory_item = self.db.query(InventoryItem).filter(
            InventoryItem.id == recipe_data.inventory_item_id
        ).first()

        if not inventory_item:
            raise ValueError(
                f"Inventory item with id {recipe_data.inventory_item_id} not found"
            )

        # Ellenőrizzük, hogy létezik-e már ilyen kombináció
        existing_recipe = self.db.query(Recipe).filter(
            Recipe.product_id == recipe_data.product_id,
            Recipe.inventory_item_id == recipe_data.inventory_item_id
        ).first()

        if existing_recipe:
            raise ValueError(
                f"Recipe for product_id={recipe_data.product_id} and "
                f"inventory_item_id={recipe_data.inventory_item_id} already exists"
            )

        # Új recept létrehozása
        db_recipe = Recipe(
            product_id=recipe_data.product_id,
            inventory_item_id=recipe_data.inventory_item_id,
            quantity_used=recipe_data.quantity_used
        )

        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)

        return db_recipe

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """
        Recept lekérdezése ID alapján.

        Args:
            recipe_id: A keresett recept azonosítója

        Returns:
            Optional[Recipe]: A megtalált recept vagy None
        """
        return self.db.query(Recipe).filter(
            Recipe.id == recipe_id
        ).first()

    def list_recipes(
        self,
        skip: int = 0,
        limit: int = 100,
        product_id: Optional[int] = None,
        inventory_item_id: Optional[int] = None
    ) -> RecipeListResponse:
        """
        Receptek listázása paginálással és szűréssel.

        Args:
            skip: Kihagyandó elemek száma (offset)
            limit: Maximum visszaadott elemek száma
            product_id: Opcionális termék ID szűrő
            inventory_item_id: Opcionális alapanyag ID szűrő

        Returns:
            RecipeListResponse: Paginált válasz a receptekkel
        """
        query = self.db.query(Recipe)

        # Termék szűrés, ha van
        if product_id is not None:
            query = query.filter(Recipe.product_id == product_id)

        # Alapanyag szűrés, ha van
        if inventory_item_id is not None:
            query = query.filter(Recipe.inventory_item_id == inventory_item_id)

        # Összes elem száma
        total = query.count()

        # Paginált elemek lekérdezése
        recipes = query.offset(skip).limit(limit).all()

        # Válasz összeállítása
        page = (skip // limit) + 1 if limit > 0 else 1

        return RecipeListResponse(
            items=[RecipeResponse.model_validate(recipe) for recipe in recipes],
            total=total,
            page=page,
            page_size=limit
        )

    def update_recipe(
        self,
        recipe_id: int,
        recipe_data: RecipeUpdate
    ) -> Optional[Recipe]:
        """
        Recept frissítése.

        Args:
            recipe_id: A frissítendő recept azonosítója
            recipe_data: RecipeUpdate schema a frissítési adatokkal

        Returns:
            Optional[Recipe]: A frissített recept vagy None, ha nem található

        Raises:
            ValueError: Ha az inventory_item_id nem létezik
            ValueError: Ha a módosítás ütközést okozna
        """
        db_recipe = self.get_recipe(recipe_id)

        if not db_recipe:
            return None

        # Ellenőrizzük inventory item létezését, ha változik
        if recipe_data.inventory_item_id is not None:
            inventory_item = self.db.query(InventoryItem).filter(
                InventoryItem.id == recipe_data.inventory_item_id
            ).first()

            if not inventory_item:
                raise ValueError(
                    f"Inventory item with id {recipe_data.inventory_item_id} not found"
                )

        # Ellenőrizzük ütközést, ha változik a product_id vagy inventory_item_id
        new_product_id = recipe_data.product_id if recipe_data.product_id is not None else db_recipe.product_id
        new_inventory_item_id = recipe_data.inventory_item_id if recipe_data.inventory_item_id is not None else db_recipe.inventory_item_id

        if (new_product_id != db_recipe.product_id or
            new_inventory_item_id != db_recipe.inventory_item_id):

            existing_recipe = self.db.query(Recipe).filter(
                Recipe.product_id == new_product_id,
                Recipe.inventory_item_id == new_inventory_item_id,
                Recipe.id != recipe_id
            ).first()

            if existing_recipe:
                raise ValueError(
                    f"Recipe for product_id={new_product_id} and "
                    f"inventory_item_id={new_inventory_item_id} already exists"
                )

        # Frissítjük csak azokat a mezőket, amelyek meg vannak adva
        update_data = recipe_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_recipe, field, value)

        self.db.commit()
        self.db.refresh(db_recipe)

        return db_recipe

    def delete_recipe(self, recipe_id: int) -> bool:
        """
        Recept törlése.

        Args:
            recipe_id: A törlendő recept azonosítója

        Returns:
            bool: True, ha sikerült törölni, False ha nem található
        """
        db_recipe = self.get_recipe(recipe_id)

        if not db_recipe:
            return False

        self.db.delete(db_recipe)
        self.db.commit()

        return True

    def get_recipes_by_product(self, product_id: int) -> List[Recipe]:
        """
        Egy termék összes receptjének lekérdezése.

        Ez megmutatja, hogy egy termék elkészítéséhez milyen
        alapanyagokra van szükség.

        Args:
            product_id: A termék azonosítója

        Returns:
            List[Recipe]: A termék receptjei
        """
        return self.db.query(Recipe).filter(
            Recipe.product_id == product_id
        ).all()

    def get_recipes_by_inventory_item(self, inventory_item_id: int) -> List[Recipe]:
        """
        Egy alapanyag felhasználását mutató receptek lekérdezése.

        Ez megmutatja, hogy egy alapanyagot milyen termékek
        készítéséhez használnak.

        Args:
            inventory_item_id: Az alapanyag azonosítója

        Returns:
            List[Recipe]: Az alapanyagot használó receptek
        """
        return self.db.query(Recipe).filter(
            Recipe.inventory_item_id == inventory_item_id
        ).all()

    def calculate_required_ingredients(
        self,
        product_id: int,
        quantity: int = 1
    ) -> dict:
        """
        Kiszámítja, hogy egy termék elkészítéséhez milyen
        alapanyagok szükségesek és mennyiben.

        Args:
            product_id: A termék azonosítója
            quantity: A termékből készítendő mennyiség (alapértelmezett: 1)

        Returns:
            dict: Az alapanyagok és szükséges mennyiségek
                  Formátum: {inventory_item_id: {name, unit, quantity_needed}}

        Raises:
            ValueError: Ha a termékhez nincs recept
        """
        recipes = self.get_recipes_by_product(product_id)

        if not recipes:
            raise ValueError(f"No recipes found for product_id={product_id}")

        required_ingredients = {}

        for recipe in recipes:
            inventory_item = self.db.query(InventoryItem).filter(
                InventoryItem.id == recipe.inventory_item_id
            ).first()

            if inventory_item:
                quantity_needed = float(recipe.quantity_used) * quantity

                required_ingredients[recipe.inventory_item_id] = {
                    "name": inventory_item.name,
                    "unit": inventory_item.unit,
                    "quantity_needed": quantity_needed,
                    "current_stock": float(inventory_item.current_stock_perpetual)
                }

        return required_ingredients

    def check_availability(
        self,
        product_id: int,
        quantity: int = 1
    ) -> dict:
        """
        Ellenőrzi, hogy egy termék elkészíthető-e a jelenlegi készletből.

        Args:
            product_id: A termék azonosítója
            quantity: A termékből készítendő mennyiség

        Returns:
            dict: Elérhetőségi információk
                  {
                      "available": bool,
                      "max_quantity": int,
                      "missing_ingredients": list
                  }
        """
        try:
            required = self.calculate_required_ingredients(product_id, quantity)
        except ValueError:
            return {
                "available": False,
                "max_quantity": 0,
                "missing_ingredients": ["No recipe found"]
            }

        missing_ingredients = []
        max_quantities = []

        for item_id, ingredient_info in required.items():
            quantity_needed = ingredient_info["quantity_needed"]
            current_stock = ingredient_info["current_stock"]

            if current_stock < quantity_needed:
                missing_ingredients.append({
                    "name": ingredient_info["name"],
                    "needed": quantity_needed,
                    "available": current_stock,
                    "unit": ingredient_info["unit"]
                })

            # Kiszámítjuk, hogy ebből az alapanyagból hány termék készíthető
            recipe = next(r for r in self.get_recipes_by_product(product_id)
                         if r.inventory_item_id == item_id)
            qty_per_unit = float(recipe.quantity_used)

            if qty_per_unit > 0:
                max_qty_from_this = int(current_stock / qty_per_unit)
                max_quantities.append(max_qty_from_this)

        return {
            "available": len(missing_ingredients) == 0,
            "max_quantity": min(max_quantities) if max_quantities else 0,
            "missing_ingredients": missing_ingredients
        }
