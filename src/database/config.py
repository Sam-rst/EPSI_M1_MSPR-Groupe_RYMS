"""
Configuration de connexion PostgreSQL pour Electio-Analytics.

Ce module centralise la configuration de la base de données et fournit
une interface pour créer des connexions SQLAlchemy.

Usage:
    >>> from database.config import get_engine, get_session
    >>> engine = get_engine()
    >>> with get_session() as session:
    ...     result = session.execute("SELECT COUNT(*) FROM territoire")
"""

import os
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Charger .env depuis la racine du projet
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


# ============================================================================
# Configuration Base de Données
# ============================================================================

class DatabaseConfig:
    """Configuration centralisée pour PostgreSQL."""

    # Lecture depuis variables d'environnement (ou valeurs par défaut)
    HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    DATABASE: str = os.getenv("POSTGRES_DB", "electio_analytics")
    USER: str = os.getenv("POSTGRES_USER", "admin")
    PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "secure_password")

    # Options connexion
    ECHO_SQL: bool = os.getenv("DB_ECHO_SQL", "False").lower() == "true"
    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))

    @classmethod
    def get_database_url(cls, driver: str = "postgresql+psycopg2") -> str:
        """
        Construit l'URL de connexion PostgreSQL.

        Args:
            driver: Driver SQLAlchemy (par défaut psycopg2)
                    Options : 'postgresql+psycopg2', 'postgresql+pg8000'

        Returns:
            URL de connexion PostgreSQL

        Example:
            >>> DatabaseConfig.get_database_url()
            'postgresql+psycopg2://admin:***@localhost:5432/electio_analytics'
        """
        # Échapper le mot de passe (caractères spéciaux)
        password_encoded = quote_plus(cls.PASSWORD)

        return (
            f"{driver}://{cls.USER}:{password_encoded}"
            f"@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"
        )

    @classmethod
    def validate_connection(cls) -> bool:
        """
        Valide la connexion à la base de données.

        Returns:
            True si connexion réussie, False sinon
        """
        try:
            engine = create_engine(
                cls.get_database_url(),
                poolclass=NullPool,  # Pas de pool pour test rapide
                echo=False
            )
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"❌ Échec connexion PostgreSQL : {e}")
            return False


# ============================================================================
# Factory Functions
# ============================================================================

def get_engine(echo: Optional[bool] = None) -> Engine:
    """
    Crée un moteur SQLAlchemy avec pool de connexions.

    Args:
        echo: Si True, affiche les requêtes SQL (debug)
              Si None, utilise DatabaseConfig.ECHO_SQL

    Returns:
        SQLAlchemy Engine

    Example:
        >>> engine = get_engine()
        >>> df = pd.read_sql("SELECT * FROM territoire LIMIT 10", engine)
    """
    echo_sql = echo if echo is not None else DatabaseConfig.ECHO_SQL

    engine = create_engine(
        DatabaseConfig.get_database_url(),
        echo=echo_sql,
        pool_size=DatabaseConfig.POOL_SIZE,
        max_overflow=DatabaseConfig.MAX_OVERFLOW,
        pool_timeout=DatabaseConfig.POOL_TIMEOUT,
        pool_pre_ping=True,  # Vérifie la connexion avant utilisation
        pool_recycle=3600,   # Recycle connexions après 1h
    )

    return engine


def get_session() -> Session:
    """
    Crée une session SQLAlchemy ORM.

    Returns:
        SQLAlchemy Session (context manager)

    Example:
        >>> with get_session() as session:
        ...     territoires = session.query(Territoire).limit(10).all()
        ...     for t in territoires:
        ...         print(t.nom_territoire)
    """
    engine = get_engine()
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )
    return SessionLocal()


# ============================================================================
# Utilitaires
# ============================================================================

def test_connection() -> None:
    """
    Teste la connexion et affiche les informations.

    Usage:
        python -c "from database.config import test_connection; test_connection()"
    """
    print("🔍 Test de connexion PostgreSQL...")
    print(f"   Host: {DatabaseConfig.HOST}:{DatabaseConfig.PORT}")
    print(f"   Database: {DatabaseConfig.DATABASE}")
    print(f"   User: {DatabaseConfig.USER}")

    if DatabaseConfig.validate_connection():
        print("✅ Connexion réussie !")

        # Afficher version PostgreSQL
        engine = get_engine(echo=False)
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.fetchone()[0]
            print(f"   PostgreSQL Version: {version.split(',')[0]}")

            # Compter les tables
            result = conn.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            nb_tables = result.fetchone()[0]
            print(f"   Nombre de tables : {nb_tables}")
    else:
        print("❌ Échec de connexion")
        print("\n💡 Vérifier :")
        print("   1. PostgreSQL est démarré : sudo systemctl status postgresql")
        print("   2. Variables d'environnement : POSTGRES_HOST, POSTGRES_USER, etc.")
        print("   3. Permissions utilisateur : psql -U admin -d electio_analytics")


def create_database_if_not_exists() -> None:
    """
    Crée la base de données si elle n'existe pas.

    Note:
        Nécessite connexion à la base 'postgres' avec privilèges CREATE DATABASE
    """
    from sqlalchemy import text

    # Connexion à la base système 'postgres'
    temp_config_url = (
        f"postgresql+psycopg2://{DatabaseConfig.USER}:"
        f"{quote_plus(DatabaseConfig.PASSWORD)}"
        f"@{DatabaseConfig.HOST}:{DatabaseConfig.PORT}/postgres"
    )

    engine = create_engine(temp_config_url, isolation_level="AUTOCOMMIT")

    with engine.connect() as conn:
        # Vérifier existence
        result = conn.execute(text(
            f"SELECT 1 FROM pg_database WHERE datname = '{DatabaseConfig.DATABASE}'"
        ))
        exists = result.fetchone()

        if not exists:
            print(f"📦 Création base de données '{DatabaseConfig.DATABASE}'...")
            conn.execute(text(f"CREATE DATABASE {DatabaseConfig.DATABASE}"))
            print("✅ Base de données créée")
        else:
            print(f"✅ Base de données '{DatabaseConfig.DATABASE}' existe déjà")


# ============================================================================
# Script Principal (pour tests)
# ============================================================================

if __name__ == "__main__":
    """
    Point d'entrée pour tests rapides :
        python src/database/config.py
    """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--create-db":
        create_database_if_not_exists()
    else:
        test_connection()
