"""Package de configuration pour le module Load ETL."""

from .settings import (
    # Chemins
    ELECTIONS_CSV,
    SECURITE_CSV,
    # Territoire
    CODE_COMMUNE,
    NOM_COMMUNE,
    TYPE_TERRITOIRE,
    POPULATION_BORDEAUX,
    # Types indicateurs
    TYPES_INDICATEURS,
    # Batch
    BATCH_SIZE,
    VERBOSE,
    # Validation
    ANNEES_ELECTIONS_VALIDES,
    ANNEES_INDICATEURS_VALIDES,
    TOURS_VALIDES,
)

__all__ = [
    "ELECTIONS_CSV",
    "SECURITE_CSV",
    "CODE_COMMUNE",
    "NOM_COMMUNE",
    "TYPE_TERRITOIRE",
    "POPULATION_BORDEAUX",
    "TYPES_INDICATEURS",
    "BATCH_SIZE",
    "VERBOSE",
    "ANNEES_ELECTIONS_VALIDES",
    "ANNEES_INDICATEURS_VALIDES",
    "TOURS_VALIDES",
]
