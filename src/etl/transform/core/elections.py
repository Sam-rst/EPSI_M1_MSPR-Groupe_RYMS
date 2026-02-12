"""
Module de transformation des données électorales (v3 - dataset agrégé).

Transforme les données de participation (JSON) et candidats (Parquet)
en CSV prêts pour le chargement dans le schéma v3.0.

Auteur: @de (Data Engineer)
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from ..config import (
    CODE_DEPARTEMENT,
    DATA_PROCESSED_ELECTIONS,
    DATA_RAW_ELECTIONS,
    ELECTIONS_IDS,
    FICHIERS_ELECTIONS_V3,
)

logger = logging.getLogger(__name__)

# Mapping election_id → (annee, tour)
ELECTION_ID_MAP: Dict[str, tuple] = {
    "2017_pres_t1": (2017, 1),
    "2017_pres_t2": (2017, 2),
    "2022_pres_t1": (2022, 1),
    "2022_pres_t2": (2022, 2),
}


def _parse_int(value) -> int:
    """Parse une valeur en int, gère les formats français (virgules)."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().replace(",", ".").replace(" ", "")
    if not s:
        return 0
    return int(float(s))


def _transform_participation() -> Optional[pd.DataFrame]:
    """
    Transforme les fichiers JSON de participation en DataFrame consolidé.

    Colonnes de sortie:
        id_election_code, annee, tour, id_territoire, type_territoire,
        nombre_inscrits, nombre_abstentions, nombre_votants,
        nombre_blancs_nuls, nombre_exprimes
    """
    logger.info("\n[1/3] Transformation participation")

    all_records = []

    for election_id in ELECTIONS_IDS:
        filepath = DATA_RAW_ELECTIONS / f"participation_{election_id}.json"
        if not filepath.exists():
            logger.warning(f"  [MANQUANT] {filepath.name}")
            continue

        annee, tour = ELECTION_ID_MAP[election_id]

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"  {election_id}: {len(data)} bureaux bruts")

        for record in data:
            # Construire l'id du territoire (commune = code_département + code_commune)
            code_dept = str(record.get("code_departement", "")).strip().zfill(2)
            code_commune = str(record.get("code_commune", "")).strip().zfill(3)
            id_commune = code_dept + code_commune

            inscrits = _parse_int(record.get("inscrits"))
            abstentions = _parse_int(record.get("abstentions"))
            votants = _parse_int(record.get("votants"))
            blancs = _parse_int(record.get("blancs", 0))
            nuls = _parse_int(record.get("nuls", 0))
            exprimes = _parse_int(record.get("exprimes"))

            blancs_nuls = blancs + nuls

            # Si exprimes non fourni, le calculer
            if exprimes == 0 and votants > 0:
                exprimes = votants - blancs_nuls

            all_records.append({
                "id_election_code": election_id,
                "annee": annee,
                "tour": tour,
                "id_territoire": id_commune,
                "type_territoire": "COMMUNE",
                "code_bureau": str(record.get("code_bureau_vote", record.get("code_bv", ""))).strip(),
                "nombre_inscrits": inscrits,
                "nombre_abstentions": abstentions,
                "nombre_votants": votants,
                "nombre_blancs_nuls": blancs_nuls,
                "nombre_exprimes": exprimes,
            })

    if not all_records:
        logger.error("  Aucune donnée de participation trouvée")
        return None

    df = pd.DataFrame(all_records)

    # Agréger par commune (sommer les bureaux de vote)
    df_agg = df.groupby(
        ["id_election_code", "annee", "tour", "id_territoire", "type_territoire"],
        as_index=False,
    ).agg({
        "nombre_inscrits": "sum",
        "nombre_abstentions": "sum",
        "nombre_votants": "sum",
        "nombre_blancs_nuls": "sum",
        "nombre_exprimes": "sum",
    })

    logger.info(f"  Total: {len(df_agg)} lignes (communes × élections)")
    return df_agg


def _transform_candidats() -> Optional[pd.DataFrame]:
    """
    Transforme le fichier Parquet candidats en DataFrame filtré dept 33.

    Colonnes de sortie:
        id_election_code, annee, tour, id_territoire, type_territoire,
        nom, prenom, sexe, nuance, nombre_voix,
        pourcentage_voix_inscrits, pourcentage_voix_exprimes
    """
    logger.info("\n[2/3] Transformation candidats (Parquet)")

    parquet_path = DATA_RAW_ELECTIONS / FICHIERS_ELECTIONS_V3["candidats_parquet"]
    if not parquet_path.exists():
        logger.error(f"  [MANQUANT] {parquet_path.name}")
        return None

    try:
        df = pd.read_parquet(parquet_path)
    except Exception as e:
        logger.error(f"  [ERREUR] Lecture Parquet: {e}")
        return None

    logger.info(f"  Lignes totales Parquet: {len(df):,}")
    logger.info(f"  Colonnes: {list(df.columns)}")

    # Filtrer pour département 33 et élections présidentielles
    # Les colonnes peuvent varier selon le dataset, adapter dynamiquement
    col_dept = None
    for candidate_col in ["code_departement", "code_du_departement", "code_dept"]:
        if candidate_col in df.columns:
            col_dept = candidate_col
            break

    col_election = None
    for candidate_col in ["id_election", "id_election_code", "code_election"]:
        if candidate_col in df.columns:
            col_election = candidate_col
            break

    if col_dept:
        df["_dept"] = df[col_dept].astype(str).str.strip().str.zfill(2)
        df_filtered = df[df["_dept"] == CODE_DEPARTEMENT].copy()
        logger.info(f"  Après filtre dept={CODE_DEPARTEMENT}: {len(df_filtered):,} lignes")
    else:
        logger.warning("  Colonne département non trouvée, utilisation de toutes les données")
        df_filtered = df.copy()

    if col_election:
        pres_elections = [eid for eid in ELECTIONS_IDS]
        df_filtered = df_filtered[df_filtered[col_election].astype(str).isin(pres_elections)].copy()
        logger.info(f"  Après filtre présidentielles: {len(df_filtered):,} lignes")

    if df_filtered.empty:
        logger.error("  Aucune donnée candidat après filtrage")
        return None

    # Résoudre les noms de colonnes une seule fois (pas dans une boucle)
    def _find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        for c in candidates:
            if c in df.columns:
                return c
        return None

    col_commune = _find_col(df_filtered, ["code_commune", "code_de_la_commune", "code_com"])
    col_nom = _find_col(df_filtered, ["nom", "nom_candidat", "nom_du_candidat"])
    col_prenom = _find_col(df_filtered, ["prenom", "prenom_candidat", "prenom_du_candidat"])
    col_sexe = _find_col(df_filtered, ["sexe", "sexe_candidat"])
    col_nuance = _find_col(df_filtered, ["nuance", "code_nuance", "nuance_candidat"])
    col_voix = _find_col(df_filtered, ["voix", "nb_voix", "nombre_voix"])
    col_pct_ins = _find_col(df_filtered, ["pourcentage_voix_inscrits", "pct_voix_inscrits", "ratio_voix_inscrits", "voix_ins"])
    col_pct_exp = _find_col(df_filtered, ["pourcentage_voix_exprimes", "pct_voix_exprimes", "ratio_voix_exprimes", "voix_exp"])

    # Mapper vectorisé election_id → (annee, tour)
    df_work = df_filtered.copy()
    if col_election:
        df_work["_election_id"] = df_work[col_election].astype(str).str.strip()
        df_work["annee"] = df_work["_election_id"].map(lambda x: ELECTION_ID_MAP.get(x, (0, 0))[0])
        df_work["tour"] = df_work["_election_id"].map(lambda x: ELECTION_ID_MAP.get(x, (0, 0))[1])
    else:
        df_work["_election_id"] = ""
        df_work["annee"] = 0
        df_work["tour"] = 0

    # Construire id_territoire vectorisé
    code_dept_series = df_work[col_dept].astype(str).str.strip().str.zfill(2) if col_dept else pd.Series(CODE_DEPARTEMENT, index=df_work.index)
    code_commune_series = df_work[col_commune].astype(str).str.strip().str.zfill(3) if col_commune else pd.Series("", index=df_work.index)
    df_work["id_territoire"] = code_dept_series + code_commune_series
    df_work["type_territoire"] = "COMMUNE"

    # Extraire colonnes vectorisé (fillna avant astype pour Arrow/pd.NA)
    df_work["nom"] = df_work[col_nom].fillna("").astype(str).str.strip() if col_nom else ""
    df_work["prenom"] = df_work[col_prenom].fillna("").astype(str).str.strip() if col_prenom else ""
    df_work["sexe"] = df_work[col_sexe].fillna("").astype(str).str.strip() if col_sexe else ""
    df_work["nuance"] = df_work[col_nuance].fillna("").astype(str).str.strip() if col_nuance else ""
    df_work["nombre_voix"] = pd.to_numeric(df_work[col_voix], errors="coerce").fillna(0).astype(int) if col_voix else 0
    if col_pct_ins:
        pct_ins_raw = pd.to_numeric(df_work[col_pct_ins], errors="coerce").fillna(0.0)
        # Si les valeurs sont des ratios (0-1), convertir en pourcentages (0-100)
        if pct_ins_raw.max() <= 1.0:
            pct_ins_raw = pct_ins_raw * 100
        df_work["pourcentage_voix_inscrits"] = pct_ins_raw.round(2)
    else:
        df_work["pourcentage_voix_inscrits"] = 0.0

    if col_pct_exp:
        pct_exp_raw = pd.to_numeric(df_work[col_pct_exp], errors="coerce").fillna(0.0)
        if pct_exp_raw.max() <= 1.0:
            pct_exp_raw = pct_exp_raw * 100
        df_work["pourcentage_voix_exprimes"] = pct_exp_raw.round(2)
    else:
        df_work["pourcentage_voix_exprimes"] = 0.0

    result_cols = [
        "_election_id", "annee", "tour", "id_territoire", "type_territoire",
        "nom", "prenom", "sexe", "nuance", "nombre_voix",
        "pourcentage_voix_inscrits", "pourcentage_voix_exprimes",
    ]
    df_result = df_work[result_cols].rename(columns={"_election_id": "id_election_code"})

    # Agréger par commune (sommer les bureaux)
    df_agg = df_result.groupby(
        ["id_election_code", "annee", "tour", "id_territoire", "type_territoire",
         "nom", "prenom", "sexe", "nuance"],
        as_index=False,
    ).agg({
        "nombre_voix": "sum",
        "pourcentage_voix_inscrits": "mean",
        "pourcentage_voix_exprimes": "mean",
    })

    logger.info(f"  Candidats agrégés: {len(df_agg)} lignes")
    return df_agg


def _extract_referentiels(df_candidats: pd.DataFrame) -> tuple:
    """
    Extrait les référentiels candidats et partis uniques depuis les données candidats.

    Returns:
        (df_candidats_ref, df_partis_ref)
    """
    logger.info("\n[3/3] Extraction référentiels candidats et partis")

    # Référentiel candidats uniques
    df_cand_ref = df_candidats[["nom", "prenom", "sexe"]].drop_duplicates().reset_index(drop=True)
    df_cand_ref.index.name = "idx"
    logger.info(f"  Candidats uniques: {len(df_cand_ref)}")

    # Référentiel partis/nuances uniques
    nuances = df_candidats["nuance"].dropna().unique()
    df_partis_ref = pd.DataFrame({
        "code_nuance": [n for n in nuances if n],
    })
    logger.info(f"  Nuances uniques: {len(df_partis_ref)}")

    return df_cand_ref, df_partis_ref


def transform_elections() -> bool:
    """
    Transforme les données électorales du dataset agrégé.

    Fichiers produits:
        - participation_gironde.csv : Participation par commune × élection × tour
        - candidats_gironde.csv : Voix par candidat × commune × élection × tour
        - referentiel_candidats.csv : Candidats uniques (nom, prénom, sexe)
        - referentiel_partis.csv : Nuances politiques uniques

    Returns:
        True si la transformation a réussi
    """
    logger.info("=" * 80)
    logger.info("TRANSFORMATION DONNÉES ÉLECTORALES (v3)")
    logger.info("=" * 80)

    try:
        DATA_PROCESSED_ELECTIONS.mkdir(parents=True, exist_ok=True)

        # 1. Participation
        df_participation = _transform_participation()
        if df_participation is not None and not df_participation.empty:
            output_part = DATA_PROCESSED_ELECTIONS / "participation_gironde.csv"
            df_participation.to_csv(output_part, index=False, encoding='utf-8')
            logger.info(f"  [OK] {output_part.name} ({len(df_participation)} lignes)")
        else:
            logger.warning("  [WARN] Pas de données de participation")

        # 2. Candidats
        df_candidats = _transform_candidats()
        if df_candidats is not None and not df_candidats.empty:
            output_cand = DATA_PROCESSED_ELECTIONS / "candidats_gironde.csv"
            df_candidats.to_csv(output_cand, index=False, encoding='utf-8')
            logger.info(f"  [OK] {output_cand.name} ({len(df_candidats)} lignes)")

            # 3. Référentiels
            df_cand_ref, df_partis_ref = _extract_referentiels(df_candidats)

            output_cand_ref = DATA_PROCESSED_ELECTIONS / "referentiel_candidats.csv"
            df_cand_ref.to_csv(output_cand_ref, index=False, encoding='utf-8')
            logger.info(f"  [OK] {output_cand_ref.name} ({len(df_cand_ref)} candidats)")

            output_partis_ref = DATA_PROCESSED_ELECTIONS / "referentiel_partis.csv"
            df_partis_ref.to_csv(output_partis_ref, index=False, encoding='utf-8')
            logger.info(f"  [OK] {output_partis_ref.name} ({len(df_partis_ref)} partis)")
        else:
            logger.warning("  [WARN] Pas de données candidats")

        # Enrichir les nuances depuis le fichier CSV si disponible
        nuances_path = DATA_RAW_ELECTIONS / FICHIERS_ELECTIONS_V3.get("nuances_csv", "")
        if nuances_path.exists():
            try:
                df_nuances = pd.read_csv(nuances_path, encoding='utf-8', sep=';')
                output_nuances = DATA_PROCESSED_ELECTIONS / "nuances_politiques.csv"
                df_nuances.to_csv(output_nuances, index=False, encoding='utf-8')
                logger.info(f"  [OK] {output_nuances.name} ({len(df_nuances)} nuances)")
            except Exception as e:
                logger.warning(f"  [WARN] Lecture nuances: {e}")

        has_data = (df_participation is not None and not df_participation.empty) or \
                   (df_candidats is not None and not df_candidats.empty)

        if has_data:
            logger.info(f"\n[OK] Transformation élections terminée")
            return True
        else:
            logger.error("\n[ERREUR] Aucune donnée électorale transformée")
            return False

    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False
