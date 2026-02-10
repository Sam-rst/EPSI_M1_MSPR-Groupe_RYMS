"""
Configuration centralisée pour la transformation des données.

Ce module contient tous les chemins et constantes utilisées
pour la transformation (nettoyage et structuration) des données brutes.

Organisation:
    - Chemins des données brutes (data/raw/)
    - Chemins des données transformées (data/processed/)
    - Configuration géographique (Bordeaux - 33063)
    - Noms des fichiers d'entrée et sortie

Territoire:
    - Zone: Bordeaux (Gironde - 33)
    - Code INSEE: 33063

Auteur: @de (Data Engineer)
"""

from pathlib import Path
from typing import Dict

# ==============================================================================
# CHEMINS DE STOCKAGE
# ==============================================================================

# Racine du projet (remonte de 5 niveaux depuis ce fichier)
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent.parent

# Répertoires principaux
DATA_RAW: Path = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED: Path = PROJECT_ROOT / "data" / "processed"

# ==============================================================================
# CHEMINS DES DONNÉES BRUTES (INPUT)
# ==============================================================================

DATA_RAW_ELECTIONS: Path = DATA_RAW / "elections"
DATA_RAW_SECURITE: Path = DATA_RAW / "securite"

# ==============================================================================
# CHEMINS DES DONNÉES TRANSFORMÉES (OUTPUT)
# ==============================================================================

DATA_PROCESSED_ELECTIONS: Path = DATA_PROCESSED / "elections"
DATA_PROCESSED_INDICATEURS: Path = DATA_PROCESSED / "indicateurs"

# ==============================================================================
# PÉRIMÈTRE GÉOGRAPHIQUE
# ==============================================================================

CODE_DEPARTEMENT: str = "33"      # Gironde
CODE_COMMUNE: str = "33063"       # Bordeaux
NOM_COMMUNE: str = "Bordeaux"

# ==============================================================================
# NOMS DES FICHIERS D'ENTRÉE
# ==============================================================================

# Fichiers électoraux bruts (format: presidentielles_{annee}_tour{numero}_bureaux_vote.csv)
FICHIERS_ELECTIONS: Dict[str, str] = {
    "2017_T1": "presidentielles_2017_tour1_bureaux_vote.csv",
    "2017_T2": "presidentielles_2017_tour2_bureaux_vote.csv",
    "2022_T1": "presidentielles_2022_tour1_bureaux_vote.csv",
    "2022_T2": "presidentielles_2022_tour2_bureaux_vote.csv",
}

# Fichier de sécurité brut (France entière, sera filtré pour Bordeaux)
FICHIER_SECURITE: str = "delinquance_france_2016_2024.csv"
