"""
Module Load ETL - Chargement des données dans PostgreSQL.

Ce module charge les données transformées depuis les CSV vers PostgreSQL
en utilisant SQLAlchemy ORM et le pattern Batch Loading.

Architecture :
- config/ : Configuration (chemins, constantes, types d'indicateurs)
- core/ : Fonctions de chargement principales
- utils/ : Utilitaires de validation
- main.py : Orchestrateur du pipeline

Utilisation :
    from src.etl.load import run_load_pipeline
    results = run_load_pipeline()

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

from .main import run_load_pipeline
from .core import (
    run_load_types_indicateurs,
    run_load_territoire,
    run_load_elections,
    run_load_securite,
)

__version__ = "1.0.0"

__all__ = [
    "run_load_pipeline",
    "run_load_types_indicateurs",
    "run_load_territoire",
    "run_load_elections",
    "run_load_securite",
]
