"""
Module de transformation des données électorales.

Ce module gère la transformation des fichiers électoraux bruts
pour extraire et agréger les données de Bordeaux.

Transformations appliquées:
    - Filtrage géographique (Bordeaux uniquement)
    - Agrégation des bureaux de vote au niveau communal
    - Calcul du taux de participation
    - Conversion des formats numériques français

Auteur: @de (Data Engineer)
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

from ..config import (
    CODE_COMMUNE,
    DATA_PROCESSED_ELECTIONS,
    DATA_RAW_ELECTIONS,
    FICHIERS_ELECTIONS,
    NOM_COMMUNE,
)
from ..utils import parse_french_number

logger = logging.getLogger(__name__)


def transform_elections() -> bool:
    """
    Transforme les fichiers électoraux bruts pour extraire et agréger les données de Bordeaux.

    Processus:
        1. Lit chaque fichier CSV avec le module csv natif (pandas échoue sur format français)
        2. Filtre les bureaux de vote de Bordeaux (département 33, commune 063)
        3. Parse les nombres au format français (virgules décimales)
        4. Agrège les bureaux au niveau communal
        5. Calcule le taux de participation
        6. Sauvegarde dans un fichier unique consolidé

    Fichiers traités:
        - Présidentielles 2017 - Tours 1 & 2
        - Présidentielles 2022 - Tours 1 & 2

    Format d'entrée:
        CSV avec délimiteur point-virgule (;)
        Encoding latin-1
        Nombres au format français (virgule = décimale)

    Format de sortie:
        CSV UTF-8 avec colonnes:
        - code_commune, nom_commune, annee, tour
        - inscrits, votants, exprimes, taux_participation

    Returns:
        True si au moins une élection a été transformée avec succès
        False si aucune donnée n'a pu être traitée

    Note:
        Utilise le module csv natif au lieu de pandas car pandas ne gère pas
        correctement les virgules décimales françaises dans ces fichiers.
    """
    logger.info("=" * 80)
    logger.info("TRANSFORMATION DONNÉES ÉLECTORALES")
    logger.info("=" * 80)

    # Configuration des élections à traiter
    elections: List[tuple] = [
        ("2017_T1", 2017, 1),
        ("2017_T2", 2017, 2),
        ("2022_T1", 2022, 1),
        ("2022_T2", 2022, 2),
    ]

    all_results: List[Dict] = []

    for key, annee, tour in elections:
        filepath: Path = DATA_RAW_ELECTIONS / FICHIERS_ELECTIONS[key]

        if not filepath.exists():
            logger.warning(f"[MANQUANT] {filepath.name}")
            continue

        logger.info(f"\n[{annee} Tour {tour}]")
        logger.info(f"  Fichier: {filepath.name}")

        try:
            # Lire avec module csv natif (gère mieux les virgules décimales)
            with open(filepath, 'r', encoding='latin-1') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader)

                # Indices des colonnes importantes
                # Structure du fichier:
                # 0: Code département, 4: Code commune, 5: Nom commune
                # 6: Code bureau, 7: Inscrits, 10: Votants, 16: Exprimés
                cols_idx: Dict[str, int] = {
                    'dept': 0,
                    'code_commune': 4,
                    'nom_commune': 5,
                    'bureau': 6,
                    'inscrits': 7,
                    'votants': 10,
                    'exprimes': 16
                }

                # Collecter les bureaux de vote de Bordeaux
                bureaux: List[Dict] = []
                for row in reader:
                    if len(row) > max(cols_idx.values()):
                        dept: str = row[cols_idx['dept']].strip()
                        commune: str = row[cols_idx['code_commune']].strip()

                        # Filtrer pour Bordeaux uniquement (33063)
                        if dept == '33' and commune == '063':
                            bureaux.append({
                                'bureau': row[cols_idx['bureau']],
                                'inscrits': parse_french_number(row[cols_idx['inscrits']]),
                                'votants': parse_french_number(row[cols_idx['votants']]),
                                'exprimes': parse_french_number(row[cols_idx['exprimes']])
                            })

            if not bureaux:
                logger.warning(f"  Aucun bureau trouvé pour Bordeaux")
                continue

            logger.info(f"  Bureaux de vote: {len(bureaux)}")

            # Agréger au niveau commune
            total_inscrits: int = sum(b['inscrits'] for b in bureaux)
            total_votants: int = sum(b['votants'] for b in bureaux)
            total_exprimes: int = sum(b['exprimes'] for b in bureaux)
            taux_participation: float = round(total_votants / total_inscrits * 100, 2)

            logger.info(f"  Inscrits: {total_inscrits:,}")
            logger.info(f"  Votants: {total_votants:,}")
            logger.info(f"  Participation: {taux_participation}%")

            all_results.append({
                'code_commune': CODE_COMMUNE,
                'nom_commune': NOM_COMMUNE,
                'annee': annee,
                'tour': tour,
                'inscrits': total_inscrits,
                'votants': total_votants,
                'exprimes': total_exprimes,
                'taux_participation': taux_participation
            })

        except Exception as e:
            logger.error(f"  [ERREUR] {e}", exc_info=True)
            continue

    # Sauvegarder le fichier consolidé
    if all_results:
        DATA_PROCESSED_ELECTIONS.mkdir(parents=True, exist_ok=True)
        df: pd.DataFrame = pd.DataFrame(all_results)
        output_file: Path = DATA_PROCESSED_ELECTIONS / "resultats_elections_bordeaux.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')

        logger.info(f"\n[OK] Fichier sauvegardé: {output_file}")
        logger.info(f"     {len(df)} lignes (4 élections)")
        return True
    else:
        logger.error("\n[ERREUR] Aucune donnée transformée")
        return False
