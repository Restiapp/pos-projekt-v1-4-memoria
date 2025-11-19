"""
Database Configuration - SQLAlchemy Engine & Session
Module 1: Rendeléskezelés és Asztalok

Ez a modul felelős az SQLAlchemy engine és session kezeléséért.
FastAPI dependency injection-höz használható get_db függvény.
"""

import os
import json
from sqlalchemy import create_engine, Text, TypeDecorator
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import JSONB
from typing import Generator, Any

# Declarative Base - Minden modellhez
Base = declarative_base()


class CompatibleJSON(TypeDecorator):
    """
    Cross-database compatible JSON type.

    Uses JSONB for PostgreSQL (native JSON support with indexing)
    and TEXT for SQLite (stores JSON as text string).

    This allows tests to run on SQLite while production uses PostgreSQL.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Any, dialect) -> str:
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, serialize to JSON string
            return json.dumps(value)

    def process_result_value(self, value: Any, dialect) -> Any:
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, deserialize from JSON string
            return json.loads(value)

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


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency function az adatbázis session kezeléséhez.

    Használat FastAPI endpoint-ban:
        @app.get("/orders")
        def get_orders(db: Session = Depends(get_db)):
            orders = db.query(Order).all()
            return orders

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
