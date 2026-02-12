"""
Configuration centralisée pour la transformation des données.

Organisation:
    - Chemins des données brutes (data/raw/)
    - Chemins des données transformées (data/processed/)
    - Configuration géographique (Gironde - 33)

Auteur: @de (Data Engineer)
"""

from pathlib import Path
from typing import Dict, List

# ==============================================================================
# CHEMINS DE STOCKAGE
# ==============================================================================

PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent.parent

DATA_RAW: Path = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED: Path = PROJECT_ROOT / "data" / "processed"

# ==============================================================================
# CHEMINS DES DONNÉES BRUTES (INPUT)
# ==============================================================================

DATA_RAW_ELECTIONS: Path = DATA_RAW / "elections"
DATA_RAW_SECURITE: Path = DATA_RAW / "securite"
DATA_RAW_GEOGRAPHIE: Path = DATA_RAW / "geographie"

# ==============================================================================
# CHEMINS DES DONNÉES TRANSFORMÉES (OUTPUT)
# ==============================================================================

DATA_PROCESSED_ELECTIONS: Path = DATA_PROCESSED / "elections"
DATA_PROCESSED_INDICATEURS: Path = DATA_PROCESSED / "indicateurs"
DATA_PROCESSED_GEOGRAPHIE: Path = DATA_PROCESSED / "geographie"

# ==============================================================================
# PÉRIMÈTRE GÉOGRAPHIQUE
# ==============================================================================

CODE_DEPARTEMENT: str = "33"      # Gironde
CODE_COMMUNE: str = "33063"       # Bordeaux
NOM_COMMUNE: str = "Bordeaux"
CODE_REGION: str = "75"           # Nouvelle-Aquitaine

# ==============================================================================
# NOMS DES FICHIERS
# ==============================================================================

# Fichiers géographie bruts
FICHIERS_GEOGRAPHIE: Dict[str, str] = {
    "regions": "regions.json",
    "departement": f"departement_{CODE_DEPARTEMENT}.json",
    "communes": f"communes_{CODE_DEPARTEMENT}.json",
}

# Fichiers électoraux bruts (anciens)
FICHIERS_ELECTIONS: Dict[str, str] = {
    "2017_T1": "presidentielles_2017_tour1_bureaux_vote.csv",
    "2017_T2": "presidentielles_2017_tour2_bureaux_vote.csv",
    "2022_T1": "presidentielles_2022_tour1_bureaux_vote.csv",
    "2022_T2": "presidentielles_2022_tour2_bureaux_vote.csv",
}

# Fichiers électoraux bruts (v3)
FICHIERS_ELECTIONS_V3: Dict[str, str] = {
    "candidats_parquet": "candidats_agrege.parquet",
    "nuances_csv": "nuances_politiques.csv",
}

# IDs élections dans le dataset agrégé
ELECTIONS_IDS: List[str] = [
    "2017_pres_t1",
    "2017_pres_t2",
    "2022_pres_t1",
    "2022_pres_t2",
]

# Fichier de sécurité brut
FICHIER_SECURITE: str = "delinquance_france_2016_2024.csv"
