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

    # Mapper les colonnes vers le format attendu
    all_records = []
    for _, row in df_filtered.iterrows():
        election_id = str(row.get(col_election, "")).strip() if col_election else ""
        annee, tour = ELECTION_ID_MAP.get(election_id, (0, 0))

        # Construire id_commune
        code_dept = str(row.get(col_dept, "")).strip().zfill(2) if col_dept else CODE_DEPARTEMENT
        # Chercher la colonne commune
        code_commune_val = ""
        for c in ["code_commune", "code_de_la_commune", "code_com"]:
            if c in row.index:
                code_commune_val = str(row[c]).strip().zfill(3)
                break
        id_commune = code_dept + code_commune_val

        # Nom, prénom du candidat
        nom = ""
        prenom = ""
        for c in ["nom", "nom_candidat", "nom_du_candidat"]:
            if c in row.index and pd.notna(row[c]):
                nom = str(row[c]).strip()
                break
        for c in ["prenom", "prenom_candidat", "prenom_du_candidat"]:
            if c in row.index and pd.notna(row[c]):
                prenom = str(row[c]).strip()
                break

        # Sexe
        sexe = ""
        for c in ["sexe", "sexe_candidat"]:
            if c in row.index and pd.notna(row[c]):
                sexe = str(row[c]).strip()
                break

        # Nuance politique
        nuance = ""
        for c in ["nuance", "code_nuance", "nuance_candidat"]:
            if c in row.index and pd.notna(row[c]):
                nuance = str(row[c]).strip()
                break

        # Voix
        voix = 0
        for c in ["voix", "nb_voix", "nombre_voix"]:
            if c in row.index and pd.notna(row[c]):
                voix = _parse_int(row[c])
                break

        # Pourcentages
        pct_ins = 0.0
        for c in ["pourcentage_voix_inscrits", "pct_voix_inscrits", "voix_ins"]:
            if c in row.index and pd.notna(row[c]):
                try:
                    pct_ins = float(str(row[c]).replace(",", "."))
                except ValueError:
                    pass
                break

        pct_exp = 0.0
        for c in ["pourcentage_voix_exprimes", "pct_voix_exprimes", "voix_exp"]:
            if c in row.index and pd.notna(row[c]):
                try:
                    pct_exp = float(str(row[c]).replace(",", "."))
                except ValueError:
                    pass
                break

        all_records.append({
            "id_election_code": election_id,
            "annee": annee,
            "tour": tour,
            "id_territoire": id_commune,
            "type_territoire": "COMMUNE",
            "nom": nom,
            "prenom": prenom,
            "sexe": sexe,
            "nuance": nuance,
            "nombre_voix": voix,
            "pourcentage_voix_inscrits": round(pct_ins, 2),
            "pourcentage_voix_exprimes": round(pct_exp, 2),
        })

    df_result = pd.DataFrame(all_records)

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
                df_nuances = pd.read_csv(nuances_path, encoding='utf-8', sep=None, engine='python')
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
