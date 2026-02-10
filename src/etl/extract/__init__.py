"""
Module d'extraction des données pour Electio-Analytics.

Architecture modulaire enterprise-grade pour le téléchargement de données depuis data.gouv.fr.

Packages:
    - config/ : Configuration centralisée (settings.py avec URLs, chemins, constantes)
    - utils/ : Fonctions génériques de téléchargement (download.py)
    - core/ : Logique métier par source de données
        - elections.py : Téléchargement des élections présidentielles
        - securite.py : Téléchargement des données SSMSI
    - main.py : Script orchestrateur principal

Données téléchargées:
    - Élections présidentielles 2017 & 2022 (4 fichiers, 1er et 2nd tours)
    - Données de sécurité (SSMSI, délinquance)

Usage:
    python -m src.etl.extract.main

Architecture:
    Cette structure suit le pattern de séparation par type de fonction :
    - Configuration isolée dans config/
    - Utilitaires génériques dans utils/
    - Logique métier dans core/
    - Orchestration dans main.py

Auteur: @de (Data Engineer)
"""

from .core import download_elections, download_securite
from .main import main
from .utils import download_file

__all__ = [
    "main",
    "download_file",
    "download_elections",
    "download_securite",
]
