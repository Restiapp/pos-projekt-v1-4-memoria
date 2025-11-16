"""
Base Model Configuration
Module 0: Terméktörzs és Menü

Közös declarative base minden SQLAlchemy modellhez.
"""

from sqlalchemy.ext.declarative import declarative_base

# Közös Base osztály minden modellhez
Base = declarative_base()
