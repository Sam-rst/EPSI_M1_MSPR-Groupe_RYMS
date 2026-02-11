"""
Module Database - Electio-Analytics.

Ce module gère la connexion et l'interaction avec PostgreSQL.

Modules:
    - config: Configuration connexion et création d'engines
    - migrations: Scripts SQL de migration du schéma

Usage:
    >>> from database import get_engine, get_session
    >>> engine = get_engine()
    >>> with get_session() as session:
    ...     # Utiliser la session ORM
    ...     pass
"""

from .config import (
    DatabaseConfig,
    get_engine,
    get_session,
    test_connection,
    create_database_if_not_exists
)

__all__ = [
    "DatabaseConfig",
    "get_engine",
    "get_session",
    "test_connection",
    "create_database_if_not_exists",
]

__version__ = "1.0.0"
