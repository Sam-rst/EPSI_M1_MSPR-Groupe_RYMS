"""
Module de téléchargement des données électorales (v3 - dataset agrégé).

Télécharge les données depuis :
    - API tabulaire data.gouv.fr : Participation par bureau (JSON paginé)
    - data.gouv.fr : Candidats agrégé (Parquet)
    - data.gouv.fr : Nuances politiques (CSV)

Source: Ministère de l'Intérieur via data.gouv.fr

Auteur: @de (Data Engineer)
"""

import json
import logging
from pathlib import Path
from typing import List

import requests

from ..config import (
    CODE_DEPARTEMENT,
    DATA_RAW_ELECTIONS,
    ELECTIONS_CANDIDATS_URL,
    ELECTIONS_IDS,
    ELECTIONS_NUANCES_URL,
    ELECTIONS_PARTICIPATION_RESOURCE,
    FICHIERS_ELECTIONS_V3,
    TABULAR_API_BASE,
)
from ..utils import download_file

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS: int = 300


def _download_participation_paginated(election_id: str, output_path: Path) -> bool:
    """
    Télécharge les données de participation via l'API tabulaire (JSON paginé).

    Pagine automatiquement jusqu'à exhaustion des résultats.
    Filtre sur code_departement=33.
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            logger.info(f"  [EXISTE] {output_path.name}")
            return True

        logger.info(f"  Téléchargement participation: {election_id}")

        all_records = []
        page = 1
        page_size = 50
        base_url = f"{TABULAR_API_BASE}/{ELECTIONS_PARTICIPATION_RESOURCE}/data/"

        while True:
            params = {
                "id_election__exact": election_id,
                "code_departement__exact": CODE_DEPARTEMENT,
                "page_size": page_size,
                "page": page,
            }

            response = requests.get(base_url, params=params, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()

            records = data.get("data", [])
            if not records:
                break

            all_records.extend(records)
            meta = data.get("meta", {})
            total = meta.get("total", "?")
            logger.info(f"    Page {page}: {len(records)} lignes (total: {len(all_records)}/{total})")

            # Vérifier s'il y a une page suivante via links.next
            links = data.get("links", {})
            if not links.get("next"):
                break

            page += 1

        if not all_records:
            logger.warning(f"  [WARN] Aucune donnée pour {election_id} dept={CODE_DEPARTEMENT}")
            return False

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)

        logger.info(f"  [OK] {output_path.name} ({len(all_records)} bureaux)")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"  [ERREUR] API tabulaire: {e}")
        return False
    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False


def download_elections() -> bool:
    """
    Télécharge les données électorales depuis le dataset agrégé.

    Données téléchargées:
        1. Participation (API tabulaire JSON paginé) : 4 fichiers
           - participation_2017_pres_t1.json
           - participation_2017_pres_t2.json
           - participation_2022_pres_t1.json
           - participation_2022_pres_t2.json
        2. Candidats (Parquet agrégé) : 1 fichier ~151 MB
        3. Nuances politiques (CSV) : 1 fichier

    Destination:
        data/raw/elections/

    Returns:
        True si tous les téléchargements ont réussi
    """
    logger.info("=" * 80)
    logger.info("TÉLÉCHARGEMENT DONNÉES ÉLECTORALES (v3 - dataset agrégé)")
    logger.info("=" * 80)

    results: List[bool] = []

    # 1. Participation via API tabulaire (JSON paginé)
    logger.info("\n[1/3] PARTICIPATION (API tabulaire)")
    elections_ids: List[str] = ELECTIONS_IDS

    for election_id in elections_ids:
        output_path = DATA_RAW_ELECTIONS / f"participation_{election_id}.json"
        success = _download_participation_paginated(election_id, output_path)
        results.append(success)

    # 2. Candidats Parquet
    logger.info("\n[2/3] CANDIDATS (Parquet agrégé)")
    parquet_path = DATA_RAW_ELECTIONS / FICHIERS_ELECTIONS_V3["candidats_parquet"]
    results.append(download_file(
        ELECTIONS_CANDIDATS_URL,
        parquet_path,
        "Candidats agrégé (Parquet)",
    ))

    # 3. Nuances politiques CSV
    logger.info("\n[3/3] NUANCES POLITIQUES (CSV)")
    nuances_path = DATA_RAW_ELECTIONS / FICHIERS_ELECTIONS_V3["nuances_csv"]
    results.append(download_file(
        ELECTIONS_NUANCES_URL,
        nuances_path,
        "Nuances politiques (CSV)",
    ))

    # Résumé
    logger.info(f"\n{'=' * 80}")
    logger.info(f"Fichiers élections téléchargés: {sum(results)}/{len(results)}")
    logger.info("=" * 80)

    return all(results)
