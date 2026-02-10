"""
Configuration centralisée pour l'extraction des données.

Ce module contient toutes les URLs, chemins et constantes utilisées
pour le téléchargement des données depuis data.gouv.fr et autres sources.

Sources officielles:
    - data.gouv.fr: Élections présidentielles et données de sécurité (SSMSI)
    - INSEE: Données d'emploi et référentiels géographiques

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

# Racine du projet (remonte de 5 niveaux depuis ce fichier)
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent.parent

# Répertoires principaux
DATA_RAW: Path = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED: Path = PROJECT_ROOT / "data" / "processed"

# Sous-répertoires par type de données
DATA_RAW_ELECTIONS: Path = DATA_RAW / "elections"
DATA_RAW_SECURITE: Path = DATA_RAW / "securite"
DATA_RAW_EMPLOI: Path = DATA_RAW / "emploi"

# ==============================================================================
# PÉRIMÈTRE GÉOGRAPHIQUE
# ==============================================================================

CODE_DEPARTEMENT: str = "33"      # Gironde
CODE_COMMUNE: str = "33063"       # Bordeaux
NOM_COMMUNE: str = "Bordeaux"

# ==============================================================================
# URLs DATA.GOUV.FR - ÉLECTIONS PRÉSIDENTIELLES
# ==============================================================================

# URLs directes vers les ressources CSV (format: /api/1/datasets/r/{resource_id})
# Source: Ministère de l'Intérieur
# Granularité: Bureau de vote (niveau le plus fin disponible)

ELECTIONS_2017_T1_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "8fdb0926-ea9d-4fb4-a136-7767cd97e30b"  # Présidentielles 2017 - Tour 1 (23 avril 2017)
)

ELECTIONS_2017_T2_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "2e3e44de-e584-4aa2-8148-670daf5617e1"  # Présidentielles 2017 - Tour 2 (7 mai 2017)
)

ELECTIONS_2022_T1_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "79b5cac4-4957-486b-bbda-322d80868224"  # Présidentielles 2022 - Tour 1 (10 avril 2022)
)

ELECTIONS_2022_T2_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "4dfd05a9-094e-4043-8a19-43b6b6bbe086"  # Présidentielles 2022 - Tour 2 (24 avril 2022)
)

# ==============================================================================
# URLs DATA.GOUV.FR - SÉCURITÉ (SSMSI)
# ==============================================================================

# Base statistique communale de la délinquance enregistrée
# Source: Service Statistique Ministériel de la Sécurité Intérieure (SSMSI)
# Format: CSV gzip compressé
# Période: 2016-2024
# Granularité: Communale (toutes les communes de France)

SECURITE_COMMUNALE_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "6252a84c-6b9e-4415-a743-fc6a631877bb"
)

# ==============================================================================
# URLs INSEE - EMPLOI (non utilisées pour le POC)
# ==============================================================================

# Note: INSEE nécessite souvent un téléchargement manuel
# Ces URLs sont conservées pour référence future

EMPLOI_IRIS_BASE_URL: str = "https://www.insee.fr/fr/statistiques/7654804"
EMPLOI_BORDEAUX_DOSSIER_URL: str = (
    "https://www.insee.fr/fr/statistiques/2011101?geo=COM-33063"
)

# ==============================================================================
# RÉFÉRENTIELS GÉOGRAPHIQUES (non utilisés pour le POC)
# ==============================================================================

# Table de correspondance Bureau de vote → IRIS
CORRESPONDANCE_BUREAU_IRIS_URL: str = "https://www.insee.fr/fr/information/2008354"

# Contours IRIS (IGN)
CONTOURS_IRIS_URL: str = "https://geoservices.ign.fr/contoursiris"

# ==============================================================================
# NOMS DES FICHIERS DE SORTIE
# ==============================================================================

# Fichiers électoraux (format: presidentielles_{annee}_tour{numero}_bureaux_vote.csv)
FICHIERS_ELECTIONS: Dict[str, str] = {
    "2017_T1": "presidentielles_2017_tour1_bureaux_vote.csv",
    "2017_T2": "presidentielles_2017_tour2_bureaux_vote.csv",
    "2022_T1": "presidentielles_2022_tour1_bureaux_vote.csv",
    "2022_T2": "presidentielles_2022_tour2_bureaux_vote.csv",
}

# Configuration des élections (URL, nom_fichier, description)
# Format: List[Tuple[url, filename, description]]
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
