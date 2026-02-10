"""
Module de transformation des données de sécurité.

Ce module gère la transformation du fichier de sécurité SSMSI
en filtrant pour Bordeaux uniquement.

Transformations appliquées:
    - Filtrage géographique (Bordeaux uniquement)
    - Extraction des données de délinquance communale

Auteur: @de (Data Engineer)
"""

import logging
from pathlib import Path

import pandas as pd

from ..config import (
    CODE_COMMUNE,
    DATA_PROCESSED_INDICATEURS,
    DATA_RAW_SECURITE,
    FICHIER_SECURITE,
)

logger = logging.getLogger(__name__)


def transform_securite() -> bool:
    """
    Transforme le fichier de sécurité SSMSI en filtrant pour Bordeaux uniquement.

    Processus:
        1. Lit le fichier gzip complet (France entière)
        2. Filtre sur la colonne CODGEO_2025 pour Bordeaux (33063)
        3. Sauvegarde le sous-ensemble filtré

    Fichier traité:
        - Base statistique communale de la délinquance enregistrée
        - Période: 2016-2024
        - Source: SSMSI (Service Statistique Ministériel de la Sécurité Intérieure)

    Format d'entrée:
        CSV gzip avec délimiteur point-virgule (;)
        Encoding UTF-8
        ~34 MB compressé

    Format de sortie:
        CSV UTF-8 standard
        Environ 135 lignes pour Bordeaux

    Returns:
        True si le filtrage et la sauvegarde ont réussi
        False en cas d'erreur ou si aucune donnée Bordeaux trouvée

    Note:
        Le fichier d'entrée contient TOUTES les communes de France.
        Seules les lignes avec CODGEO_2025 = "33063" sont conservées.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TRANSFORMATION DONNÉES SÉCURITÉ")
    logger.info("=" * 80)

    filepath: Path = DATA_RAW_SECURITE / FICHIER_SECURITE

    if not filepath.exists():
        logger.warning(f"[MANQUANT] {filepath.name}")
        return False

    logger.info(f"  Fichier: {filepath.name}")

    try:
        # Lire le fichier complet (gzip compressé, séparateur point-virgule)
        df = pd.read_csv(
            filepath,
            sep=';',
            encoding='utf-8',
            compression='gzip',
            low_memory=False
        )
        logger.info(f"  Lignes totales: {len(df):,}")
        logger.info(f"  Colonnes: {list(df.columns[:5])}...")

        # Filtrer pour Bordeaux (colonne CODGEO_2025)
        if 'CODGEO_2025' not in df.columns:
            logger.error("  [ERREUR] Colonne CODGEO_2025 introuvable")
            logger.error(f"  Colonnes disponibles: {list(df.columns)}")
            return False

        # Filtrer pour Bordeaux (colonne CODGEO_2025)
        df_bordeaux: pd.DataFrame = df[
            df['CODGEO_2025'].astype(str).str.strip() == CODE_COMMUNE
        ].copy()
        logger.info(f"  Lignes Bordeaux: {len(df_bordeaux)}")

        if df_bordeaux.empty:
            logger.warning("  Aucune donnée pour Bordeaux")
            return False

        # Sauvegarder le fichier filtré
        DATA_PROCESSED_INDICATEURS.mkdir(parents=True, exist_ok=True)
        output_file: Path = DATA_PROCESSED_INDICATEURS / "delinquance_bordeaux.csv"
        df_bordeaux.to_csv(output_file, index=False, encoding='utf-8')

        logger.info(f"\n[OK] Fichier sauvegardé: {output_file}")
        logger.info(f"     {len(df_bordeaux)} lignes (période 2016-2024)")
        return True

    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False
