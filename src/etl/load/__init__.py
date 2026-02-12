"""
Module Load ETL v3.0 - Chargement des données dans PostgreSQL.

Architecture:
- config/ : Configuration (chemins, constantes, types d'indicateurs, élections)
- core/ : Fonctions de chargement principales
    - geographie.py : Region, Departement, Commune
    - type_indicateur.py : TypeIndicateur (référentiel)
    - candidats.py : TypeElection, Election, Candidat, Parti, CandidatParti
    - elections.py : ElectionTerritoire, ResultatParticipation, ResultatCandidat
    - indicateurs.py : Indicateur (polymorphe)
- utils/ : Utilitaires de validation
- main.py : Orchestrateur du pipeline

Auteur: @de (Data Engineer)
"""

from .main import run_load_pipeline
from .core import (
    run_load_geographie,
    run_load_types_indicateurs,
    run_load_candidats,
    run_load_elections,
    run_load_securite,
)

__version__ = "3.0.0"

__all__ = [
    "run_load_pipeline",
    "run_load_geographie",
    "run_load_types_indicateurs",
    "run_load_candidats",
    "run_load_elections",
    "run_load_securite",
]
