"""
Module ETL pour l'extraction, transformation et chargement des données.

Architecture :
- extract/   : Téléchargement données brutes (data.gouv.fr, SSMSI)
- transform/ : Nettoyage et transformation CSV
- load/      : Chargement dans PostgreSQL
- main.py    : Orchestrateur pipeline complet

Usage:
    from src.etl import run_etl_pipeline
    run_etl_pipeline()

    # Ou via ligne de commande
    python -m src.etl.main
"""

from .main import main as run_etl_pipeline

__all__ = ["run_etl_pipeline"]
