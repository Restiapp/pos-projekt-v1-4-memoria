"""
Database Configuration - SQLAlchemy Engine & Session
Module 0: Terméktörzs és Menü

Ez a modul felelős az SQLAlchemy engine és session kezeléséért.
FastAPI dependency injection-höz használható get_db_connection függvény.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator

# Import Base from models.base
from backend.service_menu.models.base import Base

# CRITICAL FIX (C1.2): Import all models so init_db() can create tables
from backend.service_menu.models import (
    Category,
    Product,
    ImageAsset,
    ModifierGroup,
    Modifier,
    Allergen,
    product_modifier_group_associations,
    product_allergen_associations,
    ChannelVisibility,
)

# Database URL configuration
# Környezeti változóból vagy default PostgreSQL URL
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/pos_db'
)

# SQLAlchemy Engine létrehozása
# pool_pre_ping: Ellenőrzi a kapcsolatot használat előtt
# echo: SQL parancsok logolása (development)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # Állítsd True-ra debug módban
    # For Cloud SQL connections with connector
    poolclass=NullPool if 'unix_sock' in DATABASE_URL else None
)

# SessionLocal factory - egy új session minden kéréshez
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db_connection() -> Generator[Session, None, None]:
    """
    FastAPI dependency function az adatbázis session kezeléséhez.

    Használat FastAPI endpoint-ban:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db_connection)):
            products = db.query(Product).all()
            return products

    Yields:
        Session: SQLAlchemy session objektum
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Adatbázis táblák inicializálása.

    FIGYELEM: Ez csak development/testing során használandó.
    Production környezetben használj Alembic migration-öket!
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Összes tábla törlése az adatbázisból.

    FIGYELEM: Csak development/testing során használd!
    """
    Base.metadata.drop_all(bind=engine)
