"""
Chargement du référentiel territoire (Bordeaux) dans PostgreSQL.

Charge les entités géographiques (Commune Bordeaux) dans la table territoire.

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import Territoire
from src.database.config import get_session
from ..config import (
    CODE_COMMUNE,
    NOM_COMMUNE,
    TYPE_TERRITOIRE,
    POPULATION_BORDEAUX,
    VERBOSE,
)


def load_territoire_bordeaux(session: Session) -> int:
    """
    Charge le territoire Bordeaux dans PostgreSQL.

    Args:
        session: Session SQLAlchemy

    Returns:
        Nombre de territoires insérés (0 ou 1)

    Raises:
        IntegrityError: Si le territoire existe déjà
    """
    # Vérifier si Bordeaux existe déjà
    existing = (
        session.query(Territoire)
        .filter(Territoire.id_territoire == CODE_COMMUNE)
        .first()
    )

    if existing:
        if VERBOSE:
            print(f"[WARN]  Territoire existe déjà : {CODE_COMMUNE} ({NOM_COMMUNE})")
        return 0

    # Créer le territoire Bordeaux
    territoire = Territoire(
        id_territoire=CODE_COMMUNE,
        code_insee=CODE_COMMUNE,
        type_territoire=TYPE_TERRITOIRE,
        nom_territoire=NOM_COMMUNE,
        population=POPULATION_BORDEAUX,
        # geometry sera ajouté plus tard si besoin (PostGIS)
        # metadata_ peut contenir des infos supplémentaires
        metadata_={
            "source": "INSEE",
            "annee_population": 2023,
            "note": "Population légale INSEE 2023",
        },
    )

    session.add(territoire)
    session.commit()

    if VERBOSE:
        print(
            f"[OK] Inséré : {CODE_COMMUNE} - {NOM_COMMUNE} "
            f"({POPULATION_BORDEAUX:,} habitants)"
        )

    return 1


def run_load_territoire() -> Dict[str, Any]:
    """
    Point d'entrée principal pour charger le territoire Bordeaux.

    Returns:
        Dictionnaire avec statistiques de chargement
    """
    print("\n" + "=" * 80)
    print("CHARGEMENT DU TERRITOIRE BORDEAUX")
    print("=" * 80)

    with get_session() as session:
        # Comptage avant
        count_before = session.query(Territoire).count()
        print(f"\n Nombre de territoires avant : {count_before}")

        # Chargement
        print(f"\n Chargement de la commune : {NOM_COMMUNE} ({CODE_COMMUNE})...")
        inserted = load_territoire_bordeaux(session)

        # Comptage après
        count_after = session.query(Territoire).count()
        print(f"\n Nombre de territoires après : {count_after}")
        print(f"[OK] Territoires insérés : {inserted}")

    result = {
        "count_before": count_before,
        "count_after": count_after,
        "inserted": inserted,
        "source": "config (Bordeaux)",
    }

    print("\n" + "=" * 80)
    print("[OK] CHARGEMENT TERRITOIRE TERMINÉ")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    run_load_territoire()
