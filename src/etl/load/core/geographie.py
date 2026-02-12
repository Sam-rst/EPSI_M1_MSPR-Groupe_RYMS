"""
Chargement de la hiérarchie géographique dans PostgreSQL.

Charge Region → Departement → Commune (respect des FK).

Auteur: @de (Data Engineer)
"""

from typing import Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import Region, Departement, Commune
from src.database.config import get_session
from ..config import REGIONS_CSV, DEPARTEMENTS_CSV, COMMUNES_CSV, BATCH_SIZE, VERBOSE
from ..utils import validate_csv_exists


def load_regions(session: Session) -> int:
    """Charge les régions depuis le CSV transformé."""
    validate_csv_exists(REGIONS_CSV)
    df = pd.read_csv(REGIONS_CSV)
    inserted = 0

    for _, row in df.iterrows():
        id_region = str(row["id_region"]).strip()
        existing = session.query(Region).filter(Region.id_region == id_region).first()
        if existing:
            if VERBOSE:
                print(f"  [EXISTE] Région {id_region}")
            continue

        region = Region(
            id_region=id_region,
            code_insee=str(row["code_insee"]).strip(),
            nom_region=str(row["nom_region"]).strip(),
        )
        session.add(region)
        inserted += 1

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    return inserted


def load_departements(session: Session) -> int:
    """Charge les départements depuis le CSV transformé."""
    validate_csv_exists(DEPARTEMENTS_CSV)
    df = pd.read_csv(DEPARTEMENTS_CSV)
    inserted = 0

    for _, row in df.iterrows():
        id_dept = str(row["id_departement"]).strip()
        existing = session.query(Departement).filter(Departement.id_departement == id_dept).first()
        if existing:
            if VERBOSE:
                print(f"  [EXISTE] Département {id_dept}")
            continue

        dept = Departement(
            id_departement=id_dept,
            id_region=str(row["id_region"]).strip(),
            code_insee=str(row["code_insee"]).strip(),
            nom_departement=str(row["nom_departement"]).strip(),
            population=int(row["population"]) if pd.notna(row.get("population")) else None,
            chef_lieu=str(row["chef_lieu"]).strip() if pd.notna(row.get("chef_lieu")) else None,
        )
        session.add(dept)
        inserted += 1

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    return inserted


def load_communes(session: Session) -> int:
    """Charge les communes depuis le CSV transformé (par batch)."""
    validate_csv_exists(COMMUNES_CSV)
    df = pd.read_csv(COMMUNES_CSV)
    total_inserted = 0

    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_inserted = 0

        for _, row in batch_df.iterrows():
            id_commune = str(row["id_commune"]).strip()
            existing = session.query(Commune).filter(Commune.id_commune == id_commune).first()
            if existing:
                continue

            commune = Commune(
                id_commune=id_commune,
                id_departement=str(row["id_departement"]).strip(),
                code_insee=str(row["code_insee"]).strip(),
                nom_commune=str(row["nom_commune"]).strip(),
                population=int(row["population"]) if pd.notna(row.get("population")) else None,
            )
            session.add(commune)
            batch_inserted += 1

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        total_inserted += batch_inserted

        if VERBOSE:
            batch_num = (i // BATCH_SIZE) + 1
            print(f"  Batch {batch_num}: {batch_inserted} communes insérées")

    return total_inserted


def run_load_geographie() -> Dict[str, Any]:
    """
    Point d'entrée principal pour charger la hiérarchie géographique.

    Ordre: Region → Departement → Commune (respect FK)
    """
    print("\n" + "=" * 80)
    print("CHARGEMENT HIÉRARCHIE GÉOGRAPHIQUE")
    print("=" * 80)

    with get_session() as session:
        # Régions
        print(f"\n> Régions...")
        regions_inserted = load_regions(session)
        print(f"  [OK] {regions_inserted} région(s) insérée(s)")

        # Départements
        print(f"\n> Départements...")
        depts_inserted = load_departements(session)
        print(f"  [OK] {depts_inserted} département(s) inséré(s)")

        # Communes
        print(f"\n> Communes...")
        communes_before = session.query(Commune).count()
        communes_inserted = load_communes(session)
        communes_after = session.query(Commune).count()
        print(f"  [OK] {communes_inserted} commune(s) insérée(s) (total: {communes_after})")

    result = {
        "regions_inserted": regions_inserted,
        "departements_inserted": depts_inserted,
        "communes_inserted": communes_inserted,
        "inserted": regions_inserted + depts_inserted + communes_inserted,
        "source": "geo.api.gouv.fr (CSV transformés)",
    }

    print("\n" + "=" * 80)
    print("[OK] CHARGEMENT GÉOGRAPHIE TERMINÉ")
    print("=" * 80 + "\n")

    return result
