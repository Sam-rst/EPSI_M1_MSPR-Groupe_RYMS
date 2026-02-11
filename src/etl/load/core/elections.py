"""
Chargement des résultats électoraux dans PostgreSQL.

Charge les données transformées des élections présidentielles 2017 & 2022
depuis CSV vers la table election_result.

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

from typing import Dict, Any, List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import ElectionResult
from src.database.config import get_session
from ..config import ELECTIONS_CSV, BATCH_SIZE, VERBOSE
from ..utils import validate_csv_exists, validate_elections_data


def load_elections_batch(
    session: Session,
    df: pd.DataFrame,
) -> int:
    """
    Charge un batch de résultats électoraux dans PostgreSQL.

    Args:
        session: Session SQLAlchemy
        df: DataFrame avec résultats électoraux

    Returns:
        Nombre de lignes insérées
    """
    inserted_count = 0

    for _, row in df.iterrows():
        # Convertir id_territoire en string (peut être int depuis le CSV)
        id_territoire = str(row["id_territoire"])

        # Vérifier si la ligne existe déjà (éviter doublons)
        existing = (
            session.query(ElectionResult)
            .filter(
                ElectionResult.id_territoire == id_territoire,
                ElectionResult.annee == row["annee"],
                ElectionResult.tour == row["tour"],
                ElectionResult.candidat == row["candidat"],
            )
            .first()
        )

        if existing:
            continue

        # Créer l'enregistrement
        election = ElectionResult(
            id_territoire=id_territoire,
            annee=int(row["annee"]),
            tour=int(row["tour"]),
            candidat=row["candidat"],
            nombre_voix=int(row["nombre_voix"]),
            pourcentage_voix=float(row["pourcentage_voix"]),
            taux_participation=float(row.get("taux_participation", 0.0)),
            metadata_=row.get("metadata_", None),
        )

        session.add(election)
        inserted_count += 1

    return inserted_count


def load_elections_from_csv(session: Session) -> Dict[str, Any]:
    """
    Charge tous les résultats électoraux depuis le CSV transformé.

    Args:
        session: Session SQLAlchemy

    Returns:
        Dictionnaire avec statistiques de chargement

    Raises:
        FileNotFoundError: Si le CSV n'existe pas
        ValueError: Si validation échoue
    """
    # Validation fichier
    validate_csv_exists(ELECTIONS_CSV)
    print(f" Lecture du fichier : {ELECTIONS_CSV}")

    # Lecture CSV
    df = pd.read_csv(ELECTIONS_CSV)
    print(f" Lignes lues : {len(df):,}")

    # Validation données
    validate_elections_data(df, "resultats_elections_bordeaux.csv")
    print("[OK] Validation réussie")

    # Chargement par batch
    total_inserted = 0
    num_batches = (len(df) - 1) // BATCH_SIZE + 1

    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1

        if VERBOSE:
            print(f"\n Batch {batch_num}/{num_batches} ({len(batch_df)} lignes)...")

        inserted = load_elections_batch(session, batch_df)
        total_inserted += inserted

        # Commit par batch
        session.commit()

        if VERBOSE:
            print(f"[OK] Batch {batch_num} : {inserted} insérées")

    stats = {
        "total_rows": len(df),
        "total_inserted": total_inserted,
        "num_batches": num_batches,
        "batch_size": BATCH_SIZE,
    }

    return stats


def run_load_elections() -> Dict[str, Any]:
    """
    Point d'entrée principal pour charger les résultats électoraux.

    Returns:
        Dictionnaire avec statistiques de chargement
    """
    print("\n" + "=" * 80)
    print("CHARGEMENT DES RÉSULTATS ÉLECTORAUX")
    print("=" * 80)

    with get_session() as session:
        # Comptage avant
        count_before = session.query(ElectionResult).count()
        print(f"\n Nombre de résultats avant : {count_before:,}")

        # Chargement
        print(f"\n Chargement depuis : {ELECTIONS_CSV.name}")
        stats = load_elections_from_csv(session)

        # Comptage après
        count_after = session.query(ElectionResult).count()
        print(f"\n Nombre de résultats après : {count_after:,}")
        print(f"[OK] Résultats insérés : {stats['total_inserted']:,}")

    result = {
        "count_before": count_before,
        "count_after": count_after,
        "inserted": stats["total_inserted"],
        "source": ELECTIONS_CSV.name,
        "num_batches": stats["num_batches"],
    }

    print("\n" + "=" * 80)
    print("[OK] CHARGEMENT RÉSULTATS ÉLECTORAUX TERMINÉ")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    run_load_elections()
