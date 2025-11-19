"""
Recipe API Routes
Module 5: Készletkezelés

Ez a modul tartalmazza a Recipe entitáshoz kapcsolódó FastAPI végpontokat.
Implementálja a teljes CRUD műveletsort és támogatja a lapozást és szűrést.
Receptúrák kezelése: product-alapanyag kapcsolatok és mennyiségek.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_inventory.models.database import get_db
from backend.service_inventory.services.recipe_service import RecipeService
from backend.service_inventory.schemas.recipe import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeListResponse
)


# Router létrehozása
router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)


def get_recipe_service(db: Session = Depends(get_db)) -> RecipeService:
    """
    Dependency function a RecipeService injektálásához.

    Args:
        db: Database session (injected)

    Returns:
        RecipeService: Recipe service instance
    """
    return RecipeService(db)


@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recipe",
    description="""
    Create a new recipe (product-ingredient relationship).

    This endpoint allows you to define which inventory items (ingredients)
    are used to produce a menu product and in what quantities.

    **Requirements:**
    - Product ID is required
    - Inventory item ID is required (must exist)
    - Quantity used must be > 0
    - Combination of product_id + inventory_item_id must be unique

    **Returns:**
    - 201: Successfully created recipe
    - 400: Invalid input data, inventory item not found, or duplicate combination
    """
)
def create_recipe(
    recipe_data: RecipeCreate,
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Új recept létrehozása.

    Args:
        recipe_data: RecipeCreate schema with recipe details
        service: RecipeService instance (injected)

    Returns:
        RecipeResponse: Created recipe details

    Raises:
        HTTPException 400: If validation fails or duplicate combination
    """
    try:
        recipe = service.create_recipe(recipe_data)
        return recipe
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the recipe: {str(e)}"
        )


@router.get(
    "",
    response_model=RecipeListResponse,
    summary="Get all recipes with pagination and filtering",
    description="""
    Retrieve a paginated list of recipes with optional filtering.

    This endpoint supports:
    - **Pagination**: Control the number of results and skip records
    - **Filtering**: Filter by product_id or inventory_item_id

    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 20, max: 100)
    - `product_id`: Filter by product ID (optional)
    - `inventory_item_id`: Filter by inventory item ID (optional)

    **Returns:**
    - 200: Paginated list of recipes with metadata (total count, page info)
    """
)
def get_recipes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    inventory_item_id: Optional[int] = Query(None, description="Filter by inventory item ID"),
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Receptek listázása lapozással és szűréssel.

    Args:
        skip: Pagination offset
        limit: Page size
        product_id: Optional product filter
        inventory_item_id: Optional inventory item filter
        service: RecipeService instance (injected)

    Returns:
        RecipeListResponse: Paginated list with metadata
    """
    try:
        return service.list_recipes(
            skip=skip,
            limit=limit,
            product_id=product_id,
            inventory_item_id=inventory_item_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving recipes: {str(e)}"
        )


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get recipe by ID",
    description="""
    Retrieve a single recipe by its unique identifier.

    **Path Parameters:**
    - `recipe_id`: Unique recipe identifier (integer)

    **Returns:**
    - 200: Recipe details
    - 404: Recipe not found
    """
)
def get_recipe(
    recipe_id: int,
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Recept lekérdezése ID alapján.

    Args:
        recipe_id: Recipe unique identifier
        service: RecipeService instance (injected)

    Returns:
        RecipeResponse: Recipe details

    Raises:
        HTTPException 404: If recipe not found
    """
    recipe = service.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    return recipe


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Update recipe",
    description="""
    Update an existing recipe by its ID.

    This endpoint allows partial updates - you only need to provide the fields
    you want to change. All other fields will remain unchanged.

    **Path Parameters:**
    - `recipe_id`: Unique recipe identifier (integer)

    **Request Body:**
    - Any combination of updatable fields (all optional)

    **Returns:**
    - 200: Updated recipe details
    - 404: Recipe not found
    - 400: Invalid update data or duplicate combination
    """
)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Recept frissítése.

    Args:
        recipe_id: Recipe unique identifier
        recipe_data: RecipeUpdate schema with fields to update
        service: RecipeService instance (injected)

    Returns:
        RecipeResponse: Updated recipe details

    Raises:
        HTTPException 404: If recipe not found
        HTTPException 400: If validation fails or duplicate combination
    """
    try:
        recipe = service.update_recipe(recipe_id, recipe_data)

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )

        return recipe
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the recipe: {str(e)}"
        )


@router.delete(
    "/{recipe_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete recipe",
    description="""
    Delete a recipe by its ID.

    **Warning:** This is a hard delete operation. The recipe will be permanently
    removed from the database.

    **Path Parameters:**
    - `recipe_id`: Unique recipe identifier (integer)

    **Returns:**
    - 204: Recipe successfully deleted (no content)
    - 404: Recipe not found
    """
)
def delete_recipe(
    recipe_id: int,
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Recept törlése.

    Args:
        recipe_id: Recipe unique identifier
        service: RecipeService instance (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: If recipe not found
    """
    success = service.delete_recipe(recipe_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    return None


@router.get(
    "/product/{product_id}/ingredients",
    response_model=None,
    summary="Get required ingredients for a product",
    description="""
    Calculate the required ingredients and quantities to produce a specific product.

    This endpoint returns a detailed breakdown of all inventory items needed
    to produce the specified product, including current stock levels.

    **Path Parameters:**
    - `product_id`: Product identifier (integer)

    **Query Parameters:**
    - `quantity`: Number of products to produce (default: 1)

    **Returns:**
    - 200: Dictionary of required ingredients with quantities and stock levels
    - 400: No recipe found for the product
    """
)
def get_required_ingredients(
    product_id: int,
    quantity: int = Query(1, ge=1, description="Number of products to produce"),
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Szükséges alapanyagok kiszámítása egy termékhez.

    Args:
        product_id: Product identifier
        quantity: Number of products to produce
        service: RecipeService instance (injected)

    Returns:
        dict: Required ingredients with quantities and stock info

    Raises:
        HTTPException 400: If no recipe found for product
    """
    try:
        return service.calculate_required_ingredients(product_id, quantity)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calculating ingredients: {str(e)}"
        )


@router.get(
    "/product/{product_id}/availability",
    response_model=None,
    summary="Check product availability based on current stock",
    description="""
    Check if a product can be produced with the current inventory stock.

    This endpoint analyzes the current stock levels and recipe requirements
    to determine if the requested quantity of a product can be produced.

    **Path Parameters:**
    - `product_id`: Product identifier (integer)

    **Query Parameters:**
    - `quantity`: Number of products to check (default: 1)

    **Returns:**
    - 200: Availability information including:
        - `available`: boolean indicating if production is possible
        - `max_quantity`: maximum number that can be produced
        - `missing_ingredients`: list of insufficient ingredients (if any)
    - 400: No recipe found for the product
    """
)
def check_product_availability(
    product_id: int,
    quantity: int = Query(1, ge=1, description="Number of products to check"),
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Termék elérhetőségének ellenőrzése készlet alapján.

    Args:
        product_id: Product identifier
        quantity: Number of products to check
        service: RecipeService instance (injected)

    Returns:
        dict: Availability info with max quantity and missing ingredients
    """
    try:
        return service.check_availability(product_id, quantity)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while checking availability: {str(e)}"
        )
