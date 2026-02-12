"""
Module de transformation des données géographiques.

Transforme les fichiers JSON de geo.api.gouv.fr en CSV prêts pour le load.

Transformations:
    - Régions : Filtre Nouvelle-Aquitaine (code=75)
    - Département : Gironde (code=33)
    - Communes : Toutes les communes du département 33

Auteur: @de (Data Engineer)
"""

import json
import logging
from pathlib import Path

import pandas as pd

from ..config import (
    CODE_DEPARTEMENT,
    CODE_REGION,
    DATA_PROCESSED_GEOGRAPHIE,
    DATA_RAW_GEOGRAPHIE,
    FICHIERS_GEOGRAPHIE,
)

logger = logging.getLogger(__name__)


def transform_geographie() -> bool:
    """
    Transforme les fichiers JSON géographiques en CSV normalisés.

    Processus:
        1. Lit regions.json, filtre pour Nouvelle-Aquitaine
        2. Lit departement_33.json
        3. Lit communes_33.json, normalise les colonnes

    Format de sortie:
        - regions.csv : id_region, code_insee, nom_region
        - departements.csv : id_departement, id_region, code_insee, nom_departement, population, chef_lieu
        - communes.csv : id_commune, id_departement, code_insee, nom_commune, population

    Returns:
        True si la transformation a réussi
    """
    logger.info("=" * 80)
    logger.info("TRANSFORMATION DONNÉES GÉOGRAPHIQUES")
    logger.info("=" * 80)

    try:
        DATA_PROCESSED_GEOGRAPHIE.mkdir(parents=True, exist_ok=True)

        # 1. Régions
        logger.info("\n[Régions]")
        regions_path = DATA_RAW_GEOGRAPHIE / FICHIERS_GEOGRAPHIE["regions"]
        if not regions_path.exists():
            logger.error(f"  [MANQUANT] {regions_path.name}")
            return False

        with open(regions_path, 'r', encoding='utf-8') as f:
            regions_data = json.load(f)

        # Filtrer Nouvelle-Aquitaine (code=75)
        regions_filtered = [r for r in regions_data if r.get("code") == CODE_REGION]
        if not regions_filtered:
            logger.error(f"  Région code={CODE_REGION} introuvable")
            return False

        df_regions = pd.DataFrame([{
            "id_region": r["code"],
            "code_insee": r["code"],
            "nom_region": r["nom"],
        } for r in regions_filtered])

        output_regions = DATA_PROCESSED_GEOGRAPHIE / "regions.csv"
        df_regions.to_csv(output_regions, index=False, encoding='utf-8')
        logger.info(f"  [OK] {output_regions.name} ({len(df_regions)} régions)")

        # 2. Département
        logger.info("\n[Département]")
        dept_path = DATA_RAW_GEOGRAPHIE / FICHIERS_GEOGRAPHIE["departement"]
        if not dept_path.exists():
            logger.error(f"  [MANQUANT] {dept_path.name}")
            return False

        with open(dept_path, 'r', encoding='utf-8') as f:
            dept_data = json.load(f)

        df_depts = pd.DataFrame([{
            "id_departement": dept_data["code"],
            "id_region": dept_data.get("codeRegion", CODE_REGION),
            "code_insee": dept_data["code"],
            "nom_departement": dept_data["nom"],
            "population": dept_data.get("population"),
            "chef_lieu": dept_data.get("chefLieu"),
        }])

        output_depts = DATA_PROCESSED_GEOGRAPHIE / "departements.csv"
        df_depts.to_csv(output_depts, index=False, encoding='utf-8')
        logger.info(f"  [OK] {output_depts.name} ({len(df_depts)} département)")

        # 3. Communes
        logger.info("\n[Communes]")
        communes_path = DATA_RAW_GEOGRAPHIE / FICHIERS_GEOGRAPHIE["communes"]
        if not communes_path.exists():
            logger.error(f"  [MANQUANT] {communes_path.name}")
            return False

        with open(communes_path, 'r', encoding='utf-8') as f:
            communes_data = json.load(f)

        df_communes = pd.DataFrame([{
            "id_commune": c["code"],
            "id_departement": c.get("codeDepartement", CODE_DEPARTEMENT),
            "code_insee": c["code"],
            "nom_commune": c["nom"],
            "population": c.get("population"),
        } for c in communes_data])

        output_communes = DATA_PROCESSED_GEOGRAPHIE / "communes.csv"
        df_communes.to_csv(output_communes, index=False, encoding='utf-8')
        logger.info(f"  [OK] {output_communes.name} ({len(df_communes)} communes)")

        logger.info(f"\n[OK] Transformation géographie terminée")
        return True

    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False
