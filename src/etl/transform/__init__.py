"""
Module de transformation des données pour Electio-Analytics.

Architecture modulaire enterprise-grade pour la transformation de données.

Packages:
    - config/ : Configuration centralisée (settings.py avec chemins, constantes)
    - utils/ : Fonctions génériques de parsing (parsing.py)
    - core/ : Logique métier par source de données
        - elections.py : Transformation des élections présidentielles
        - securite.py : Transformation des données SSMSI
    - main.py : Script orchestrateur principal

Données transformées:
    - Élections présidentielles 2017 & 2022 (4 fichiers → 1 consolidé)
    - Données de sécurité (France entière → Bordeaux uniquement)

Usage:
    python -m src.etl.transform.main

Architecture:
    Cette structure suit le pattern de séparation par type de fonction :
    - Configuration isolée dans config/
    - Utilitaires génériques dans utils/
    - Logique métier dans core/
    - Orchestration dans main.py

Auteur: @de (Data Engineer)
"""

from .core import transform_elections, transform_securite
from .main import main
from .utils import parse_french_number

__all__ = [
    "main",
    "parse_french_number",
    "transform_elections",
    "transform_securite",
]
