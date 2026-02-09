"""
Configuration des URLs et ressources pour l'extraction des données.

Sources officielles :
- data.gouv.fr (Élections, Sécurité)
- INSEE (Emploi, Référentiels géographiques)
"""

from pathlib import Path

# === Chemins de stockage ===
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

DATA_RAW_ELECTIONS = DATA_RAW / "elections"
DATA_RAW_SECURITE = DATA_RAW / "securite"
DATA_RAW_EMPLOI = DATA_RAW / "emploi"

# === URLs data.gouv.fr - Élections Présidentielles ===

# 2017 - 1er tour (23 avril 2017)
# ATTENTION: Les données 2017 officielles ne sont pas disponibles en téléchargement direct
# Il faut télécharger manuellement depuis :
# https://www.data.gouv.fr/fr/datasets/election-presidentielle-2017-resultats-par-bureaux-de-vote/
ELECTIONS_2017_T1_URL = None  # TÉLÉCHARGEMENT MANUEL REQUIS

# 2017 - 2ème tour (7 mai 2017)
ELECTIONS_2017_T2_URL = None  # TÉLÉCHARGEMENT MANUEL REQUIS

# 2022 - 1er tour (10 avril 2022) - Bureau de vote (niveau le plus fin)
ELECTIONS_2022_T1_URL = "https://static.data.gouv.fr/resources/election-presidentielle-des-10-et-24-avril-2022-resultats-du-1er-tour/20220411-124802/resultats-par-niveau-fe-t1-france-entiere.txt"

# 2022 - 2ème tour (24 avril 2022) - Bureau de vote (niveau le plus fin)
ELECTIONS_2022_T2_URL = "https://static.data.gouv.fr/resources/election-presidentielle-des-10-et-24-avril-2022-resultats-du-second-tour/20220425-112116/resultats-par-niveau-fe-t2-france-entiere.txt"

# === URLs Sécurité (SSMSI) ===
SECURITE_COMMUNALE_URL = (
    "https://www.data.gouv.fr/fr/datasets/r/b4e8e3cb-6ac9-4f64-ad6e-d45bd0ef8770"
)

# === URLs Emploi (INSEE) ===
# Note: INSEE nécessite souvent un téléchargement manuel depuis leur interface
EMPLOI_IRIS_BASE_URL = "https://www.insee.fr/fr/statistiques/7654804"
EMPLOI_BORDEAUX_DOSSIER_URL = "https://www.insee.fr/fr/statistiques/2011101?geo=COM-33063"

# === Référentiels Géographiques ===
# Table de correspondance Bureau de vote → IRIS
CORRESPONDANCE_BUREAU_IRIS_URL = "https://www.insee.fr/fr/information/2008354"

# Contours IRIS (IGN)
CONTOURS_IRIS_URL = "https://geoservices.ign.fr/contoursiris"

# === Périmètre Géographique ===
CODE_DEPARTEMENT = "33"  # Gironde
CODE_COMMUNE = "33063"  # Bordeaux
NOM_COMMUNE = "Bordeaux"

# === Noms des fichiers de sortie ===
FICHIERS_ELECTIONS = {
    "2017_T1": "presidentielles_2017_tour1_bureaux_vote.csv",
    "2017_T2": "presidentielles_2017_tour2_bureaux_vote.csv",
    "2022_T1": "presidentielles_2022_tour1_bureaux_vote.csv",
    "2022_T2": "presidentielles_2022_tour2_bureaux_vote.csv",
}

FICHIER_SECURITE = "delinquance_bordeaux_2016_2024.csv"

FICHIERS_EMPLOI = {
    "IRIS": "demandeurs_emploi_iris_2022.csv",
    "COMMUNE": "population_active_bordeaux_2017_2024.csv",
}
