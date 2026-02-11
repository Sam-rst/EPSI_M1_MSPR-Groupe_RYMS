"""
Configuration centralisée pour le module Load ETL.

Ce module centralise toutes les constantes et configurations nécessaires
au chargement des données dans PostgreSQL.

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

from pathlib import Path

# ==============================================================================
# CHEMINS DES DONNÉES TRANSFORMÉES
# ==============================================================================

# Répertoire racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[4]

# Données transformées (inputs)
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
ELECTIONS_PROCESSED = DATA_PROCESSED / "elections"
INDICATEURS_PROCESSED = DATA_PROCESSED / "indicateurs"

# Fichiers CSV transformés
ELECTIONS_CSV = ELECTIONS_PROCESSED / "resultats_elections_bordeaux.csv"
SECURITE_CSV = INDICATEURS_PROCESSED / "delinquance_bordeaux.csv"

# ==============================================================================
# CONFIGURATION TERRITOIRE
# ==============================================================================

# Bordeaux (Commune)
CODE_COMMUNE = "33063"
NOM_COMMUNE = "Bordeaux"
TYPE_TERRITOIRE = "COMMUNE"
POPULATION_BORDEAUX = 252040  # Population 2023 (INSEE)

# ==============================================================================
# CONFIGURATION TYPES D'INDICATEURS
# ==============================================================================

# Catalogue statique des types d'indicateurs
TYPES_INDICATEURS = [
    # === SÉCURITÉ (SSMSI) ===
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
# CONFIGURATION BATCH LOADING
# ==============================================================================

# Taille des batchs pour insertion en masse
BATCH_SIZE = 1000

# Activer le mode verbose
VERBOSE = True

# ==============================================================================
# VALIDATION
# ==============================================================================

# Années valides
ANNEES_ELECTIONS_VALIDES = [2017, 2022]
ANNEES_INDICATEURS_VALIDES = list(range(2016, 2025))
TOURS_VALIDES = [1, 2]
