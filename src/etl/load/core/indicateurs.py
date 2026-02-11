"""
Chargement des indicateurs socio-économiques dans PostgreSQL.

Charge les données transformées des indicateurs (sécurité, emploi, etc.)
depuis CSV vers la table indicateur.

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

from typing import Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import Indicateur, TypeIndicateur
from src.database.config import get_session
from ..config import SECURITE_CSV, BATCH_SIZE, VERBOSE
from ..utils import validate_csv_exists, validate_indicateurs_data


def get_type_indicateur_mapping(session: Session) -> Dict[str, int]:
    """
    Récupère le mapping code_type -> id_type depuis la base.

    Args:
        session: Session SQLAlchemy

    Returns:
        Dictionnaire {code_type: id_type}

    Raises:
        ValueError: Si aucun type d'indicateur trouvé
    """
    types = session.query(TypeIndicateur).all()

    if not types:
        raise ValueError(
            "Aucun type d'indicateur trouvé dans la base. "
            "Exécutez d'abord load_types_indicateurs()"
        )

    mapping = {t.code_type: t.id_type for t in types}

    if VERBOSE:
        print(f" Types d'indicateurs chargés : {len(mapping)}")

    return mapping


def load_indicateurs_batch(
    session: Session,
    df: pd.DataFrame,
    type_mapping: Dict[str, int],
) -> int:
    """
    Charge un batch d'indicateurs dans PostgreSQL.

    Args:
        session: Session SQLAlchemy
        df: DataFrame avec indicateurs
        type_mapping: Mapping code_type -> id_type

    Returns:
        Nombre de lignes insérées
    """
    inserted_count = 0

    for _, row in df.iterrows():
        # Récupérer l'id_type depuis le code_type
        code_type = row["code_type"]

        if code_type not in type_mapping:
            print(f"[WARN]  Type inconnu ignoré : {code_type}")
            continue

        id_type = type_mapping[code_type]

        # Convertir id_territoire en string (peut être int depuis le CSV)
        id_territoire = str(row["id_territoire"])
        periode = row.get("periode")

        # Vérifier si l'indicateur existe déjà (éviter doublons)
        existing = (
            session.query(Indicateur)
            .filter(
                Indicateur.id_territoire == id_territoire,
                Indicateur.id_type == id_type,
                Indicateur.annee == row["annee"],
                Indicateur.periode == periode,
            )
            .first()
        )

        if existing:
            continue

        # Créer l'enregistrement
        indicateur = Indicateur(
            id_territoire=id_territoire,
            id_type=id_type,
            annee=int(row["annee"]),
            periode=row.get("periode"),
            valeur_numerique=float(row["valeur_numerique"]),
            valeur_texte=row.get("valeur_texte"),
            source_detail=row.get("source_detail"),
            fiabilite=row.get("fiabilite", "CONFIRME"),
            metadata_=row.get("metadata_", None),
        )

        session.add(indicateur)
        inserted_count += 1

    return inserted_count


def load_indicateurs_from_csv(session: Session, csv_path) -> Dict[str, Any]:
    """
    Charge tous les indicateurs depuis un CSV transformé.

    Args:
        session: Session SQLAlchemy
        csv_path: Chemin vers le CSV

    Returns:
        Dictionnaire avec statistiques de chargement

    Raises:
        FileNotFoundError: Si le CSV n'existe pas
        ValueError: Si validation échoue
    """
    # Validation fichier
    validate_csv_exists(csv_path)
    print(f" Lecture du fichier : {csv_path}")

    # Lecture CSV
    df = pd.read_csv(csv_path)
    print(f" Lignes lues : {len(df):,}")

    # Validation données
    validate_indicateurs_data(df, csv_path.name)
    print("[OK] Validation réussie")

    # Récupérer mapping types
    type_mapping = get_type_indicateur_mapping(session)

    # Chargement par batch
    total_inserted = 0
    num_batches = (len(df) - 1) // BATCH_SIZE + 1

    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1

        if VERBOSE:
            print(f"\n Batch {batch_num}/{num_batches} ({len(batch_df)} lignes)...")

        inserted = load_indicateurs_batch(session, batch_df, type_mapping)
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


def run_load_securite() -> Dict[str, Any]:
    """
    Point d'entrée principal pour charger les indicateurs de sécurité.

    Returns:
        Dictionnaire avec statistiques de chargement
    """
    print("\n" + "=" * 80)
    print("CHARGEMENT DES INDICATEURS DE SÉCURITÉ")
    print("=" * 80)

    with get_session() as session:
        # Comptage avant
        count_before = session.query(Indicateur).count()
        print(f"\n Nombre d'indicateurs avant : {count_before:,}")

        # Chargement
        print(f"\n Chargement depuis : {SECURITE_CSV.name}")
        stats = load_indicateurs_from_csv(session, SECURITE_CSV)

        # Comptage après
        count_after = session.query(Indicateur).count()
        print(f"\n Nombre d'indicateurs après : {count_after:,}")
        print(f"[OK] Indicateurs insérés : {stats['total_inserted']:,}")

    result = {
        "count_before": count_before,
        "count_after": count_after,
        "inserted": stats["total_inserted"],
        "source": SECURITE_CSV.name,
        "num_batches": stats["num_batches"],
    }

    print("\n" + "=" * 80)
    print("[OK] CHARGEMENT INDICATEURS DE SÉCURITÉ TERMINÉ")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    run_load_securite()
