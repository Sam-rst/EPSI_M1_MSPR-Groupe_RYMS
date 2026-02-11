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
    Transforme le fichier de sécurité SSMSI pour Bordeaux et agrège par catégories.

    Processus:
        1. Lit le fichier gzip complet (France entière)
        2. Filtre sur la colonne CODGEO_2025 pour Bordeaux (33063)
        3. Map les indicateurs granulaires vers les 5 catégories principales
        4. Agrège les valeurs par (catégorie, année)
        5. Format de sortie: id_territoire, code_type, annee, valeur_numerique

    Mapping des indicateurs:
        - VOLS_SANS_VIOLENCE: Cambriolages, Vols dans/de véhicules
        - VOLS_AVEC_VIOLENCE: Vols avec armes, Vols violents sans arme
        - ATTEINTES_AUX_BIENS: Destructions et dégradations
        - ATTEINTES_AUX_PERSONNES: Violences physiques et sexuelles
        - CRIMINALITE_TOTALE: Somme de tous les indicateurs

    Returns:
        True si la transformation et la sauvegarde ont réussi
        False en cas d'erreur ou si aucune donnée Bordeaux trouvée
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

        # Filtrer pour Bordeaux (colonne CODGEO_2025)
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

        # Mapping des indicateurs granulaires vers les catégories
        MAPPING_INDICATEURS = {
            # Vols sans violence
            'Cambriolages de logement': 'VOLS_SANS_VIOLENCE',
            "Vols d'accessoires sur véhicules": 'VOLS_SANS_VIOLENCE',
            'Vols dans les véhicules': 'VOLS_SANS_VIOLENCE',
            'Vols de véhicule': 'VOLS_SANS_VIOLENCE',
            'Vols sans violence contre des personnes': 'VOLS_SANS_VIOLENCE',
            # Vols avec violence
            'Vols avec armes': 'VOLS_AVEC_VIOLENCE',
            'Vols violents sans arme': 'VOLS_AVEC_VIOLENCE',
            # Atteintes aux biens
            'Destructions et dégradations volontaires': 'ATTEINTES_AUX_BIENS',
            # Atteintes aux personnes
            'Violences physiques hors cadre familial': 'ATTEINTES_AUX_PERSONNES',
            'Violences physiques intrafamiliales': 'ATTEINTES_AUX_PERSONNES',
            'Violences sexuelles': 'ATTEINTES_AUX_PERSONNES',
        }

        # Mapper les indicateurs vers les catégories
        df_bordeaux['code_type'] = df_bordeaux['indicateur'].map(MAPPING_INDICATEURS)

        # Filtrer uniquement les indicateurs mappés (ignorer trafic de stupéfiants, etc.)
        df_mapped = df_bordeaux[df_bordeaux['code_type'].notna()].copy()
        logger.info(f"  Indicateurs mappés: {len(df_mapped)}")

        # Agréger par (code_type, annee)
        df_agg = df_mapped.groupby(['code_type', 'annee'], as_index=False).agg({
            'nombre': 'sum'
        })

        # Calculer CRIMINALITE_TOTALE = somme de tous les crimes par année
        df_total = df_agg.groupby('annee', as_index=False).agg({
            'nombre': 'sum'
        })
        df_total['code_type'] = 'CRIMINALITE_TOTALE'

        # Combiner avec les catégories détaillées
        df_final = pd.concat([df_agg, df_total], ignore_index=True)

        # Renommer et sélectionner colonnes finales
        df_final = df_final.rename(columns={
            'nombre': 'valeur_numerique'
        })
        df_final['id_territoire'] = CODE_COMMUNE

        # Sélectionner et ordonner colonnes finales
        df_output = df_final[['id_territoire', 'code_type', 'annee', 'valeur_numerique']].copy()
        df_output = df_output.sort_values(['annee', 'code_type'])

        # Sauvegarder le fichier transformé
        DATA_PROCESSED_INDICATEURS.mkdir(parents=True, exist_ok=True)
        output_file: Path = DATA_PROCESSED_INDICATEURS / "delinquance_bordeaux.csv"
        df_output.to_csv(output_file, index=False, encoding='utf-8')

        logger.info(f"\n[OK] Fichier sauvegardé: {output_file}")
        logger.info(f"     {len(df_output)} lignes (5 catégories × {df_output['annee'].nunique()} années)")
        logger.info(f"     Période: {df_output['annee'].min()}-{df_output['annee'].max()}")
        return True

    except Exception as e:
        logger.error(f"  [ERREUR] {e}", exc_info=True)
        return False
