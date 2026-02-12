"""
Configuration centralisée pour l'extraction des données.

Sources officielles:
    - geo.api.gouv.fr: Hiérarchie géographique (régions, départements, communes)
    - tabular-api.data.gouv.fr: Élections agrégées (participation par bureau)
    - data.gouv.fr: Candidats (Parquet), nuances politiques (CSV), sécurité SSMSI

Territoire:
    - Zone: Bordeaux (Gironde - 33)
    - Code INSEE: 33063

Auteur: @de (Data Engineer)
"""

from pathlib import Path
from typing import Dict, List, Tuple

# ==============================================================================
# CHEMINS DE STOCKAGE
# ==============================================================================

PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent.parent

DATA_RAW: Path = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED: Path = PROJECT_ROOT / "data" / "processed"

DATA_RAW_ELECTIONS: Path = DATA_RAW / "elections"
DATA_RAW_SECURITE: Path = DATA_RAW / "securite"
DATA_RAW_GEOGRAPHIE: Path = DATA_RAW / "geographie"
DATA_RAW_EMPLOI: Path = DATA_RAW / "emploi"

# ==============================================================================
# PÉRIMÈTRE GÉOGRAPHIQUE
# ==============================================================================

CODE_DEPARTEMENT: str = "33"      # Gironde
CODE_COMMUNE: str = "33063"       # Bordeaux
NOM_COMMUNE: str = "Bordeaux"

# ==============================================================================
# URLs GEO.API.GOUV.FR - HIÉRARCHIE GÉOGRAPHIQUE
# ==============================================================================

GEO_API_BASE: str = "https://geo.api.gouv.fr"
GEO_REGIONS_URL: str = f"{GEO_API_BASE}/regions"
GEO_DEPARTEMENT_URL: str = f"{GEO_API_BASE}/departements/{CODE_DEPARTEMENT}"
GEO_COMMUNES_URL: str = f"{GEO_API_BASE}/departements/{CODE_DEPARTEMENT}/communes"

# ==============================================================================
# URLs DATA.GOUV.FR - ÉLECTIONS AGRÉGÉES (nouveau dataset)
# ==============================================================================

# API tabulaire pour la participation (JSON paginé)
ELECTIONS_PARTICIPATION_RESOURCE: str = "b8703c69-a18f-46ab-9e7f-3a8368dcb891"
TABULAR_API_BASE: str = "https://tabular-api.data.gouv.fr/api/resources"

# Candidats : Parquet agrégé (~151 MB)
ELECTIONS_CANDIDATS_RESOURCE: str = "4d3b35f6-0b22-4415-a24c-419a676312e2"

# Nuances politiques : CSV dictionnaire
ELECTIONS_NUANCES_RESOURCE: str = "6fd17a6c-519b-465c-a7fd-ad2955fafc76"

# IDs des élections dans le dataset agrégé
ELECTIONS_IDS: List[str] = [
    "2017_pres_t1",
    "2017_pres_t2",
    "2022_pres_t1",
    "2022_pres_t2",
]

# URLs directes pour téléchargement Parquet et CSV
ELECTIONS_CANDIDATS_URL: str = (
    f"https://www.data.gouv.fr/api/1/datasets/r/{ELECTIONS_CANDIDATS_RESOURCE}"
)
ELECTIONS_NUANCES_URL: str = (
    f"https://www.data.gouv.fr/api/1/datasets/r/{ELECTIONS_NUANCES_RESOURCE}"
)

# ==============================================================================
# URLs DATA.GOUV.FR - ANCIENNES ÉLECTIONS (conservées pour compatibilité)
# ==============================================================================

ELECTIONS_2017_T1_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "8fdb0926-ea9d-4fb4-a136-7767cd97e30b"
)
ELECTIONS_2017_T2_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "2e3e44de-e584-4aa2-8148-670daf5617e1"
)
ELECTIONS_2022_T1_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "79b5cac4-4957-486b-bbda-322d80868224"
)
ELECTIONS_2022_T2_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "4dfd05a9-094e-4043-8a19-43b6b6bbe086"
)

# ==============================================================================
# URLs DATA.GOUV.FR - SÉCURITÉ (SSMSI)
# ==============================================================================

SECURITE_COMMUNALE_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "6252a84c-6b9e-4415-a743-fc6a631877bb"
)

# ==============================================================================
# URLs INSEE - EMPLOI (non utilisées pour le POC)
# ==============================================================================

EMPLOI_IRIS_BASE_URL: str = "https://www.insee.fr/fr/statistiques/7654804"
EMPLOI_BORDEAUX_DOSSIER_URL: str = (
    "https://www.insee.fr/fr/statistiques/2011101?geo=COM-33063"
)

# ==============================================================================
# RÉFÉRENTIELS GÉOGRAPHIQUES (non utilisés pour le POC)
# ==============================================================================

CORRESPONDANCE_BUREAU_IRIS_URL: str = "https://www.insee.fr/fr/information/2008354"
CONTOURS_IRIS_URL: str = "https://geoservices.ign.fr/contoursiris"

# ==============================================================================
# NOMS DES FICHIERS DE SORTIE
# ==============================================================================

# Fichiers géographie (JSON depuis geo.api.gouv.fr)
FICHIERS_GEOGRAPHIE: Dict[str, str] = {
    "regions": "regions.json",
    "departement": f"departement_{CODE_DEPARTEMENT}.json",
    "communes": f"communes_{CODE_DEPARTEMENT}.json",
}

# Fichiers électoraux anciens (format: presidentielles_{annee}_tour{numero}_bureaux_vote.csv)
FICHIERS_ELECTIONS: Dict[str, str] = {
    "2017_T1": "presidentielles_2017_tour1_bureaux_vote.csv",
    "2017_T2": "presidentielles_2017_tour2_bureaux_vote.csv",
    "2022_T1": "presidentielles_2022_tour1_bureaux_vote.csv",
    "2022_T2": "presidentielles_2022_tour2_bureaux_vote.csv",
}

# Fichiers électoraux nouveaux (dataset agrégé)
FICHIERS_ELECTIONS_V3: Dict[str, str] = {
    "candidats_parquet": "candidats_agrege.parquet",
    "nuances_csv": "nuances_politiques.csv",
}

# Configuration des élections anciennes (URL, nom_fichier, description)
ELECTIONS: List[Tuple[str, str, str]] = [
    (ELECTIONS_2017_T1_URL, FICHIERS_ELECTIONS["2017_T1"], "Présidentielles 2017 - Tour 1"),
    (ELECTIONS_2017_T2_URL, FICHIERS_ELECTIONS["2017_T2"], "Présidentielles 2017 - Tour 2"),
    (ELECTIONS_2022_T1_URL, FICHIERS_ELECTIONS["2022_T1"], "Présidentielles 2022 - Tour 1"),
    (ELECTIONS_2022_T2_URL, FICHIERS_ELECTIONS["2022_T2"], "Présidentielles 2022 - Tour 2"),
]

# Fichier de sécurité (France entière, sera filtré pour Bordeaux)
FICHIER_SECURITE: str = "delinquance_france_2016_2024.csv"

# Fichiers emploi (non utilisés pour le POC)
FICHIERS_EMPLOI: Dict[str, str] = {
    "IRIS": "demandeurs_emploi_iris_2022.csv",
    "COMMUNE": "population_active_bordeaux_2017_2024.csv",
}
