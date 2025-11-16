"""
Database Configuration - SQLAlchemy Engine & Session
Module 8: Adminisztráció és NTAK

Ez a modul felelős az SQLAlchemy engine és session kezeléséért.
FastAPI dependency injection-höz használható get_db függvény.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import NullPool
from typing import Generator

# Declarative Base - Minden modellhez
Base = declarative_base()

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
        @app.get("/admin/audit-logs")
        def get_audit_logs(db: Session = Depends(get_db)):
            logs = db.query(AuditLog).all()
            return logs

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
