"""
Alembic Environment Configuration - Electio-Analytics.

Ce fichier configure l'environnement Alembic pour les migrations.
"""

from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ajouter le répertoire src au PYTHONPATH
src_path = Path(__file__).resolve().parents[3]  # Remonte à la racine du projet
sys.path.insert(0, str(src_path))

# Import des modèles ORM (IMPORTANT: doit être après PYTHONPATH)
from src.database.models import Base  # Importe Base avec tous les modèles
from src.database.config import DatabaseConfig

# Configuration Alembic
config = context.config

# Setup logging depuis alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées des modèles SQLAlchemy
target_metadata = Base.metadata

# ============================================================================
# Configuration URL Base de Données
# ============================================================================

def get_url():
    """Récupère l'URL de connexion depuis DatabaseConfig ou .env"""
    return DatabaseConfig.get_database_url()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Détecter changements de types
        compare_server_default=True,  # Détecter changements valeurs par défaut
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Exclure les tables PostGIS Tiger de l'autogenerate.
    """
    # Liste des tables PostGIS Tiger à ignorer
    tiger_tables = {
        'spatial_ref_sys', 'geocode_settings', 'geocode_settings_default',
        'direction_lookup', 'secondary_unit_lookup', 'state_lookup',
        'street_type_lookup', 'place_lookup', 'county_lookup',
        'countysub_lookup', 'zip_lookup_base', 'zip_state', 'zip_lookup',
        'zip_state_loc', 'zip_lookup_all', 'county', 'state', 'place',
        'cousub', 'tract', 'tabblock', 'tabblock20', 'bg', 'zcta5',
        'edges', 'faces', 'featnames', 'addr', 'addrfeat',
        'loader_platform', 'loader_variables', 'loader_lookuptables',
        'pagc_gaz', 'pagc_lex', 'pagc_rules', 'topology', 'layer'
    }

    if type_ == "table" and name in tiger_tables:
        return False
    return True


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Override sqlalchemy.url dans alembic.ini avec notre config
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Détecter changements de types
            compare_server_default=True,  # Détecter changements valeurs par défaut
            include_object=include_object,  # Exclure tables Tiger PostGIS
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
