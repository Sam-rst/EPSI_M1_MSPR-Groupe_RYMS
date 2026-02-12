"""
Chargement du catalogue de types d'indicateurs dans PostgreSQL.

Charge le référentiel statique TYPES_INDICATEURS depuis la configuration
dans la table type_indicateur.

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import TypeIndicateur
from src.database.config import get_session
from ..config import TYPES_INDICATEURS, VERBOSE


def load_types_indicateurs(session: Session) -> int:
    """
    Charge le catalogue de types d'indicateurs dans PostgreSQL.

    Args:
        session: Session SQLAlchemy

    Returns:
        Nombre de types d'indicateurs insérés

    Raises:
        IntegrityError: Si des doublons existent déjà
    """
    inserted_count = 0

    for type_data in TYPES_INDICATEURS:
        # Vérifier si le type existe déjà
        existing = (
            session.query(TypeIndicateur)
            .filter(TypeIndicateur.code_type == type_data["code_type"])
            .first()
        )

        if existing:
            if VERBOSE:
                print(f"[WARN]  Type indicateur existe déjà : {type_data['code_type']}")
            continue

        # Créer le type indicateur
        type_indicateur = TypeIndicateur(
            code_type=type_data["code_type"],
            categorie=type_data["categorie"],
            nom_affichage=type_data["nom_affichage"],
            description=type_data.get("description"),
            unite_mesure=type_data["unite_mesure"],
            source_officielle=type_data.get("source_officielle"),
            frequence=type_data.get("frequence"),
        )

        session.add(type_indicateur)
        inserted_count += 1

        if VERBOSE:
            print(f"[OK] Inséré : {type_data['code_type']} ({type_data['nom_affichage']})")

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return inserted_count


def run_load_types_indicateurs() -> Dict[str, Any]:
    """
    Point d'entrée principal pour charger les types d'indicateurs.

    Returns:
        Dictionnaire avec statistiques de chargement
    """
    print("\n" + "=" * 80)
    print("CHARGEMENT DES TYPES D'INDICATEURS")
    print("=" * 80)

    with get_session() as session:
        # Comptage avant
        count_before = session.query(TypeIndicateur).count()
        print(f"\n Nombre de types avant : {count_before}")

        # Chargement
        print(f"\n Chargement de {len(TYPES_INDICATEURS)} types depuis la configuration...")
        inserted = load_types_indicateurs(session)

        # Comptage après
        count_after = session.query(TypeIndicateur).count()
        print(f"\n Nombre de types après : {count_after}")
        print(f"[OK] Types insérés : {inserted}")

    result = {
        "count_before": count_before,
        "count_after": count_after,
        "inserted": inserted,
        "source": "config.TYPES_INDICATEURS",
    }

    print("\n" + "=" * 80)
    print("[OK] CHARGEMENT TYPES D'INDICATEURS TERMINÉ")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    run_load_types_indicateurs()
