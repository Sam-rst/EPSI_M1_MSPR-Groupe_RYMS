"""
Module de transformation des données de sécurité.

Transforme le fichier SSMSI en filtrant pour Bordeaux et en agrégeant par catégories.
Ajout v3: colonne type_territoire pour le système polymorphe.

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
    Transforme le fichier de sécurité SSMSI pour Bordeaux et agrège par catégories.

    Processus:
        1. Lit le fichier gzip complet (France entière)
        2. Filtre sur CODGEO_2025 pour Bordeaux (33063)
        3. Map les indicateurs granulaires vers 5 catégories
        4. Agrège par (catégorie, année)
        5. Ajoute type_territoire=COMMUNE pour le système polymorphe v3

    Format de sortie:
        id_territoire, type_territoire, code_type, annee, valeur_numerique

    Returns:
        True si la transformation a réussi
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
        df = pd.read_csv(
            filepath,
            sep=';',
            encoding='utf-8',
            compression='gzip',
            low_memory=False
        )
        logger.info(f"  Lignes totales: {len(df):,}")

        if 'CODGEO_2025' not in df.columns:
            logger.error("  [ERREUR] Colonne CODGEO_2025 introuvable")
            return False

        df_bordeaux: pd.DataFrame = df[
            df['CODGEO_2025'].astype(str).str.strip() == CODE_COMMUNE
        ].copy()
        logger.info(f"  Lignes brutes Bordeaux: {len(df_bordeaux)}")

        if df_bordeaux.empty:
            logger.warning("  Aucune donnée pour Bordeaux")
            return False

        MAPPING_INDICATEURS = {
            'Cambriolages de logement': 'VOLS_SANS_VIOLENCE',
            "Vols d'accessoires sur véhicules": 'VOLS_SANS_VIOLENCE',
            'Vols dans les véhicules': 'VOLS_SANS_VIOLENCE',
            'Vols de véhicule': 'VOLS_SANS_VIOLENCE',
            'Vols sans violence contre des personnes': 'VOLS_SANS_VIOLENCE',
            'Vols avec armes': 'VOLS_AVEC_VIOLENCE',
            'Vols violents sans arme': 'VOLS_AVEC_VIOLENCE',
            'Destructions et dégradations volontaires': 'ATTEINTES_AUX_BIENS',
            'Violences physiques hors cadre familial': 'ATTEINTES_AUX_PERSONNES',
            'Violences physiques intrafamiliales': 'ATTEINTES_AUX_PERSONNES',
            'Violences sexuelles': 'ATTEINTES_AUX_PERSONNES',
        }

        df_bordeaux['code_type'] = df_bordeaux['indicateur'].map(MAPPING_INDICATEURS)
        df_mapped = df_bordeaux[df_bordeaux['code_type'].notna()].copy()
        logger.info(f"  Indicateurs mappés: {len(df_mapped)}")

        df_agg = df_mapped.groupby(['code_type', 'annee'], as_index=False).agg({
            'nombre': 'sum'
        })

        df_total = df_agg.groupby('annee', as_index=False).agg({
            'nombre': 'sum'
        })
        df_total['code_type'] = 'CRIMINALITE_TOTALE'

        df_final = pd.concat([df_agg, df_total], ignore_index=True)
        df_final = df_final.rename(columns={'nombre': 'valeur_numerique'})
        df_final['id_territoire'] = CODE_COMMUNE
        df_final['type_territoire'] = 'COMMUNE'

        # Sélectionner et ordonner colonnes finales (v3 avec type_territoire)
        df_output = df_final[[
            'id_territoire', 'type_territoire', 'code_type', 'annee', 'valeur_numerique'
        ]].copy()
        df_output = df_output.sort_values(['annee', 'code_type'])

        DATA_PROCESSED_INDICATEURS.mkdir(parents=True, exist_ok=True)
        output_file: Path = DATA_PROCESSED_INDICATEURS / "delinquance_bordeaux.csv"
        df_output.to_csv(output_file, index=False, encoding='utf-8')

        logger.info(f"\n[OK] Fichier sauvegardé: {output_file}")
        logger.info(f"     {len(df_output)} lignes (5 catégories x {df_output['annee'].nunique()} années)")
        logger.info(f"     Période: {df_output['annee'].min()}-{df_output['annee'].max()}")
        return True

    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False
