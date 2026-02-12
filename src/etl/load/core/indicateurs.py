"""
Chargement des indicateurs socio-économiques dans PostgreSQL.

Utilise le système polymorphe v3.0 (id_territoire + type_territoire).

Auteur: @de (Data Engineer)
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
    """Récupère le mapping code_type → id_type depuis la base."""
    types = session.query(TypeIndicateur).all()

    if not types:
        raise ValueError(
            "Aucun type d'indicateur trouvé dans la base. "
            "Exécutez d'abord load_types_indicateurs()"
        )

    mapping = {t.code_type: t.id_type for t in types}

    if VERBOSE:
        print(f"  Types d'indicateurs chargés: {len(mapping)}")

    return mapping


def load_indicateurs_batch(
    session: Session,
    df: pd.DataFrame,
    type_mapping: Dict[str, int],
) -> int:
    """Charge un batch d'indicateurs dans PostgreSQL."""
    inserted_count = 0

    for _, row in df.iterrows():
        code_type = row["code_type"]

        if code_type not in type_mapping:
            print(f"  [WARN] Type inconnu ignoré: {code_type}")
            continue

        id_type = type_mapping[code_type]
        id_territoire = str(row["id_territoire"])
        type_territoire = str(row.get("type_territoire", "COMMUNE"))
        periode = row.get("periode") if pd.notna(row.get("periode")) else None

        # Vérifier doublon (avec type_territoire pour v3)
        existing = (
            session.query(Indicateur)
            .filter(
                Indicateur.id_territoire == id_territoire,
                Indicateur.type_territoire == type_territoire,
                Indicateur.id_type == id_type,
                Indicateur.annee == row["annee"],
                Indicateur.periode == periode,
            )
            .first()
        )

        if existing:
            continue

        indicateur = Indicateur(
            id_territoire=id_territoire,
            type_territoire=type_territoire,
            id_type=id_type,
            annee=int(row["annee"]),
            periode=periode,
            valeur_numerique=float(row["valeur_numerique"]),
            valeur_texte=row.get("valeur_texte") if pd.notna(row.get("valeur_texte", None)) else None,
            source_detail=row.get("source_detail") if pd.notna(row.get("source_detail", None)) else "SSMSI",
            fiabilite=row.get("fiabilite", "CONFIRME") if pd.notna(row.get("fiabilite", None)) else "CONFIRME",
        )

        session.add(indicateur)
        inserted_count += 1

    return inserted_count


def load_indicateurs_from_csv(session: Session, csv_path) -> Dict[str, Any]:
    """Charge tous les indicateurs depuis un CSV transformé."""
    validate_csv_exists(csv_path)
    print(f"  Lecture du fichier: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"  Lignes lues: {len(df):,}")

    # Validation
    validate_indicateurs_data(df, csv_path.name)
    print("  [OK] Validation réussie")

    # Mapping types
    type_mapping = get_type_indicateur_mapping(session)

    # Chargement par batch
    total_inserted = 0
    num_batches = (len(df) - 1) // BATCH_SIZE + 1

    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1

        if VERBOSE:
            print(f"\n  Batch {batch_num}/{num_batches} ({len(batch_df)} lignes)...")

        inserted = load_indicateurs_batch(session, batch_df, type_mapping)
        total_inserted += inserted
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise

        if VERBOSE:
            print(f"  [OK] Batch {batch_num}: {inserted} insérées")

    return {
        "total_rows": len(df),
        "total_inserted": total_inserted,
        "num_batches": num_batches,
        "batch_size": BATCH_SIZE,
    }


def run_load_securite() -> Dict[str, Any]:
    """Point d'entrée principal pour charger les indicateurs de sécurité."""
    print("\n" + "=" * 80)
    print("CHARGEMENT DES INDICATEURS DE SÉCURITÉ")
    print("=" * 80)

    with get_session() as session:
        count_before = session.query(Indicateur).count()
        print(f"\n  Nombre d'indicateurs avant: {count_before:,}")

        print(f"\n  Chargement depuis: {SECURITE_CSV.name}")
        stats = load_indicateurs_from_csv(session, SECURITE_CSV)

        count_after = session.query(Indicateur).count()
        print(f"\n  Nombre d'indicateurs après: {count_after:,}")
        print(f"  [OK] Indicateurs insérés: {stats['total_inserted']:,}")

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
