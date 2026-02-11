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
        Encoding UTF-8
        Nombres au format français (virgule = décimale)

    Format de sortie:
        CSV UTF-8 avec colonnes:
        - id_territoire, annee, tour, candidat
        - nombre_voix, pourcentage_voix

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
            # Tentative UTF-8 d'abord, fallback sur latin-1 si échec
            encoding = 'utf-8'
            try:
                with open(filepath, 'r', encoding='utf-8') as test_f:
                    test_f.read(1024)  # Lire un échantillon pour tester l'encodage
            except UnicodeDecodeError:
                encoding = 'latin-1'

            with open(filepath, 'r', encoding=encoding) as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader)

                # Structure du fichier:
                # Colonnes 0-20: Infos générales du bureau (21 colonnes)
                # Colonnes 21+: Pattern répétitif de 7 colonnes par candidat
                #   N°Panneau, Sexe, Nom, Prénom, Voix, % Voix/Ins, % Voix/Exp

                # Collecter les résultats par candidat pour Bordeaux
                candidats_data: Dict[str, Dict] = {}  # {candidat: {voix}}
                bureaux_uniques = set()

                # Infos globales (prendre du premier bureau)
                total_inscrits = 0
                total_votants = 0

                for row in reader:
                    if len(row) <= 20:
                        continue

                    dept: str = row[0].strip()
                    commune: str = row[4].strip()

                    # Filtrer pour Bordeaux uniquement (33063)
                    if dept == '33' and commune == '063':
                        bureau = row[6].strip()
                        bureaux_uniques.add(bureau)

                        # Récupérer infos globales (une seule fois)
                        if total_inscrits == 0:
                            total_inscrits = parse_french_number(row[7])
                            total_votants = parse_french_number(row[10])

                        # Parser tous les candidats (à partir colonne 21, par groupes de 7)
                        col = 21
                        while col + 6 < len(row):
                            try:
                                # Extraire les 7 colonnes du candidat
                                # col+0: N°Panneau, col+1: Sexe, col+2: Nom, col+3: Prénom
                                # col+4: Voix, col+5: %Voix/Ins, col+6: %Voix/Exp
                                nom = row[col + 2].strip()
                                prenom = row[col + 3].strip()

                                if not nom or not prenom:
                                    break  # Fin des candidats

                                candidat = f"{prenom} {nom}"
                                voix = parse_french_number(row[col + 4])

                                # Agréger par candidat
                                if candidat not in candidats_data:
                                    candidats_data[candidat] = {'voix': 0}

                                candidats_data[candidat]['voix'] += voix

                                # Passer au candidat suivant (+7 colonnes)
                                col += 7

                            except (IndexError, ValueError):
                                break  # Fin des candidats pour ce bureau

            if not candidats_data:
                logger.warning(f"  Aucun résultat trouvé pour Bordeaux")
                continue

            logger.info(f"  Bureaux de vote: {len(bureaux_uniques)}")

            # Calculer statistiques globales
            if candidats_data:
                # Total exprimés = somme des voix de TOUS les candidats
                total_exprimes = sum(c['voix'] for c in candidats_data.values())
                taux_participation = round(total_votants / total_inscrits * 100, 2) if total_inscrits > 0 else 0

                logger.info(f"  Inscrits: {total_inscrits:,}")
                logger.info(f"  Votants: {total_votants:,}")
                logger.info(f"  Participation: {taux_participation}%")
                logger.info(f"  Candidats: {len(candidats_data)}")

            # Créer une ligne par candidat
            for candidat, data in candidats_data.items():
                # Calcul correct du pourcentage: voix / total_exprimes
                pourcentage_voix = round((data['voix'] / total_exprimes) * 100, 2) if total_exprimes > 0 else 0

                all_results.append({
                    'id_territoire': CODE_COMMUNE,
                    'annee': annee,
                    'tour': tour,
                    'candidat': candidat,
                    'nombre_voix': data['voix'],
                    'pourcentage_voix': pourcentage_voix
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
        logger.info(f"     {len(df)} lignes ({len(df)} candidats × élections)")
        return True
    else:
        logger.error("\n[ERREUR] Aucune donnée transformée")
        return False
