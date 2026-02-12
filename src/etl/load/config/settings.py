"""
Configuration centralisée pour le module Load ETL v3.0.

Auteur: @de (Data Engineer)
"""

from pathlib import Path

# ==============================================================================
# CHEMINS DES DONNÉES TRANSFORMÉES
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
ELECTIONS_PROCESSED = DATA_PROCESSED / "elections"
INDICATEURS_PROCESSED = DATA_PROCESSED / "indicateurs"
GEOGRAPHIE_PROCESSED = DATA_PROCESSED / "geographie"

# ==============================================================================
# FICHIERS CSV TRANSFORMÉS
# ==============================================================================

# Géographie
REGIONS_CSV = GEOGRAPHIE_PROCESSED / "regions.csv"
DEPARTEMENTS_CSV = GEOGRAPHIE_PROCESSED / "departements.csv"
COMMUNES_CSV = GEOGRAPHIE_PROCESSED / "communes.csv"

# Élections v3
PARTICIPATION_CSV = ELECTIONS_PROCESSED / "participation_gironde.csv"
CANDIDATS_CSV = ELECTIONS_PROCESSED / "candidats_gironde.csv"
REFERENTIEL_CANDIDATS_CSV = ELECTIONS_PROCESSED / "referentiel_candidats.csv"
REFERENTIEL_PARTIS_CSV = ELECTIONS_PROCESSED / "referentiel_partis.csv"
NUANCES_CSV = ELECTIONS_PROCESSED / "nuances_politiques.csv"

# Indicateurs
SECURITE_CSV = INDICATEURS_PROCESSED / "delinquance_bordeaux.csv"

# Ancien (conservé pour compatibilité)
ELECTIONS_CSV = ELECTIONS_PROCESSED / "resultats_elections_bordeaux.csv"

# ==============================================================================
# CONFIGURATION TERRITOIRE
# ==============================================================================

CODE_COMMUNE = "33063"
NOM_COMMUNE = "Bordeaux"
TYPE_TERRITOIRE = "COMMUNE"
POPULATION_BORDEAUX = 252040  # Population 2023 (INSEE)

# ==============================================================================
# CONFIGURATION TYPES D'INDICATEURS
# ==============================================================================

TYPES_INDICATEURS = [
    {
        "code_type": "CRIMINALITE_TOTALE",
        "categorie": "SECURITE",
        "nom_affichage": "Criminalité totale",
        "description": "Nombre total de crimes et délits enregistrés",
        "unite_mesure": "nombre",
        "source_officielle": "SSMSI",
        "frequence": "ANNUEL",
    },
    {
        "code_type": "VOLS_SANS_VIOLENCE",
        "categorie": "SECURITE",
        "nom_affichage": "Vols sans violence",
        "description": "Cambriolages, vols à la roulotte, vols de véhicules",
        "unite_mesure": "nombre",
        "source_officielle": "SSMSI",
        "frequence": "ANNUEL",
    },
    {
        "code_type": "VOLS_AVEC_VIOLENCE",
        "categorie": "SECURITE",
        "nom_affichage": "Vols avec violence",
        "description": "Vols avec armes, vols violents",
        "unite_mesure": "nombre",
        "source_officielle": "SSMSI",
        "frequence": "ANNUEL",
    },
    {
        "code_type": "ATTEINTES_AUX_BIENS",
        "categorie": "SECURITE",
        "nom_affichage": "Atteintes aux biens",
        "description": "Destructions et dégradations",
        "unite_mesure": "nombre",
        "source_officielle": "SSMSI",
        "frequence": "ANNUEL",
    },
    {
        "code_type": "ATTEINTES_AUX_PERSONNES",
        "categorie": "SECURITE",
        "nom_affichage": "Atteintes aux personnes",
        "description": "Violences physiques, menaces",
        "unite_mesure": "nombre",
        "source_officielle": "SSMSI",
        "frequence": "ANNUEL",
    },
]

# ==============================================================================
# CONFIGURATION ÉLECTIONS
# ==============================================================================

# Type élection présidentielle
TYPE_ELECTION_PRES = {
    "code_type": "PRES",
    "nom_type": "Élection présidentielle",
    "mode_scrutin": "uninominal_2tours",
    "niveau_geographique": "national",
    "description": "Élection du président de la République française",
}

# Élections à charger
ELECTIONS_CONFIG = [
    {
        "annee": 2017,
        "date_tour1": "2017-04-23",
        "date_tour2": "2017-05-07",
        "nombre_tours": 2,
        "contexte": "Élection présidentielle 2017",
    },
    {
        "annee": 2022,
        "date_tour1": "2022-04-10",
        "date_tour2": "2022-04-24",
        "nombre_tours": 2,
        "contexte": "Élection présidentielle 2022, contexte post-COVID",
    },
]

# Mapping nuance → classification idéologique
NUANCE_CLASSIFICATION = {
    "EXG": ("extreme_gauche", "Extrême gauche"),
    "COM": ("extreme_gauche", "Parti communiste français"),
    "FI": ("gauche", "La France insoumise"),
    "SOC": ("gauche", "Parti socialiste"),
    "ECO": ("gauche", "Europe Écologie Les Verts"),
    "DVG": ("gauche", "Divers gauche"),
    "RDG": ("gauche", "Radical de gauche"),
    "VEC": ("gauche", "Verts"),
    "MDM": ("centre", "Modem"),
    "REM": ("centre", "La République en Marche"),
    "ENS": ("centre", "Ensemble"),
    "UDI": ("centre_droit", "Union des démocrates et indépendants"),
    "LR": ("droite", "Les Républicains"),
    "DVD": ("droite", "Divers droite"),
    "DLF": ("droite", "Debout la France"),
    "RN": ("extreme_droite", "Rassemblement national"),
    "REC": ("extreme_droite", "Reconquête"),
    "EXD": ("extreme_droite", "Extrême droite"),
    "DIV": ("autre", "Divers"),
    "DSV": ("autre", "Divers souverainiste"),
}

# Mapping candidat (NOM) → code_parti pour les présidentielles
# Source: Ministère de l'Intérieur (nuances officielles)
CANDIDAT_PARTI_MAP = {
    # 2017 Tour 1
    "ARTHAUD": "EXG",
    "ASSELINEAU": "DIV",
    "CHEMINADE": "DIV",
    "DUPONT-AIGNAN": "DLF",
    "FILLON": "LR",
    "HAMON": "SOC",
    "LASSALLE": "DIV",
    "LE PEN": "RN",
    "MACRON": "REM",
    "MÉLENCHON": "FI",
    "POUTOU": "EXG",
    # 2022 Tour 1
    "HIDALGO": "SOC",
    "JADOT": "ECO",
    "PÉCRESSE": "LR",
    "ROUSSEL": "COM",
    "ZEMMOUR": "REC",
}

# ==============================================================================
# CONFIGURATION BATCH LOADING
# ==============================================================================

BATCH_SIZE = 1000
VERBOSE = True

# ==============================================================================
# VALIDATION
# ==============================================================================

ANNEES_ELECTIONS_VALIDES = [2017, 2022]
ANNEES_INDICATEURS_VALIDES = list(range(2016, 2025))
TOURS_VALIDES = [1, 2]
