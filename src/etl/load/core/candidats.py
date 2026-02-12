"""
Chargement des référentiels électoraux dans PostgreSQL.

Charge: TypeElection → Election → Candidat → Parti → CandidatParti.

Auteur: @de (Data Engineer)
"""

from datetime import date
from typing import Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import TypeElection, Election, Candidat, Parti, CandidatParti
from src.database.config import get_session
from ..config import (
    TYPE_ELECTION_PRES,
    ELECTIONS_CONFIG,
    REFERENTIEL_CANDIDATS_CSV,
    REFERENTIEL_PARTIS_CSV,
    NUANCES_CSV,
    CANDIDATS_CSV,
    NUANCE_CLASSIFICATION,
    CANDIDAT_PARTI_MAP,
    VERBOSE,
)
from ..utils import validate_csv_exists


def load_type_election(session: Session) -> int:
    """Charge le type élection présidentielle."""
    code = TYPE_ELECTION_PRES["code_type"]
    existing = session.query(TypeElection).filter(TypeElection.code_type == code).first()
    if existing:
        if VERBOSE:
            print(f"  [EXISTE] TypeElection {code}")
        return 0

    type_election = TypeElection(
        code_type=code,
        nom_type=TYPE_ELECTION_PRES["nom_type"],
        mode_scrutin=TYPE_ELECTION_PRES.get("mode_scrutin"),
        niveau_geographique=TYPE_ELECTION_PRES.get("niveau_geographique"),
        description=TYPE_ELECTION_PRES.get("description"),
    )
    session.add(type_election)
    session.commit()
    if VERBOSE:
        print(f"  [OK] TypeElection {code} inséré")
    return 1


def load_elections(session: Session) -> int:
    """Charge les événements électoraux (2017, 2022)."""
    type_election = session.query(TypeElection).filter(
        TypeElection.code_type == TYPE_ELECTION_PRES["code_type"]
    ).first()

    if not type_election:
        raise ValueError("TypeElection PRES non trouvé. Chargez d'abord le type.")

    inserted = 0
    for config in ELECTIONS_CONFIG:
        # Vérifier si l'élection existe déjà
        existing = session.query(Election).filter(
            Election.id_type_election == type_election.id_type_election,
            Election.annee == config["annee"],
        ).first()

        if existing:
            if VERBOSE:
                print(f"  [EXISTE] Election {config['annee']}")
            continue

        election = Election(
            id_type_election=type_election.id_type_election,
            annee=config["annee"],
            date_tour1=date.fromisoformat(config["date_tour1"]),
            date_tour2=date.fromisoformat(config["date_tour2"]) if config.get("date_tour2") else None,
            nombre_tours=config.get("nombre_tours", 2),
            contexte=config.get("contexte"),
        )
        session.add(election)
        inserted += 1
        if VERBOSE:
            print(f"  [OK] Election {config['annee']} insérée")

    session.commit()
    return inserted


def load_candidats(session: Session) -> int:
    """Charge le référentiel des candidats uniques."""
    if not REFERENTIEL_CANDIDATS_CSV.exists():
        print(f"  [WARN] Fichier référentiel candidats non trouvé: {REFERENTIEL_CANDIDATS_CSV}")
        return 0

    df = pd.read_csv(REFERENTIEL_CANDIDATS_CSV)
    if df.empty:
        print("  [WARN] Fichier référentiel candidats vide")
        return 0

    # Charger les candidats existants pour éviter N+1 queries
    existing_candidats = {
        (c.nom, c.prenom) for c in session.query(Candidat).all()
    }

    inserted = 0
    for _, row in df.iterrows():
        nom = str(row["nom"]).strip()
        prenom = str(row["prenom"]).strip()

        if not nom or not prenom:
            continue

        if (nom, prenom) in existing_candidats:
            continue

        candidat = Candidat(nom=nom, prenom=prenom)
        session.add(candidat)
        existing_candidats.add((nom, prenom))
        inserted += 1

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    if VERBOSE:
        print(f"  [OK] {inserted} candidat(s) inséré(s)")
    return inserted


def load_partis(session: Session) -> int:
    """Charge les partis depuis le mapping statique CANDIDAT_PARTI_MAP."""
    # Collecter les codes parti uniques depuis le mapping
    codes_partis = set(CANDIDAT_PARTI_MAP.values())
    inserted = 0

    for code_parti in sorted(codes_partis):
        existing = session.query(Parti).filter(Parti.code_parti == code_parti).first()
        if existing:
            continue

        classification, nom_officiel = NUANCE_CLASSIFICATION.get(
            code_parti, ("autre", f"Nuance {code_parti}")
        )

        parti = Parti(
            code_parti=code_parti,
            nom_officiel=nom_officiel,
            nom_court=code_parti,
            classification_ideologique=classification,
        )
        session.add(parti)
        inserted += 1

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    if VERBOSE:
        print(f"  [OK] {inserted} parti(s) inséré(s)")
    return inserted


def load_candidat_parti(session: Session) -> int:
    """Crée les affiliations candidat ↔ parti via le mapping statique."""
    # Récupérer tous les candidats et partis en base (éviter N+1)
    all_candidats = session.query(Candidat).all()
    partis_cache = {p.code_parti: p.id_parti for p in session.query(Parti).all()}
    existing_affiliations = {
        (cp.id_candidat, cp.id_parti, cp.date_debut)
        for cp in session.query(CandidatParti).all()
    }

    inserted = 0
    unmapped_count = 0

    for candidat in all_candidats:
        nom_upper = candidat.nom.upper()
        code_parti = CANDIDAT_PARTI_MAP.get(nom_upper)
        if not code_parti:
            unmapped_count += 1
            print(f"  [WARN] Pas de parti mappé pour {candidat.prenom} {candidat.nom}")
            continue

        id_parti = partis_cache.get(code_parti)
        if not id_parti:
            print(f"  [WARN] Parti {code_parti} introuvable en base")
            continue

        # Date d'affiliation = 1er janvier de la première élection
        date_debut = date(2017, 1, 1)
        if (candidat.id_candidat, id_parti, date_debut) in existing_affiliations:
            continue

        affiliation = CandidatParti(
            id_candidat=candidat.id_candidat,
            id_parti=id_parti,
            date_debut=date_debut,
            fonction="Candidat",
        )
        session.add(affiliation)
        inserted += 1

    if unmapped_count > 0:
        print(f"  [INFO] {unmapped_count} candidat(s) sans mapping parti")

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    if VERBOSE:
        print(f"  [OK] {inserted} affiliation(s) insérée(s)")
    return inserted


def run_load_candidats() -> Dict[str, Any]:
    """
    Point d'entrée pour charger les référentiels électoraux.

    Ordre: TypeElection → Election → Candidat → Parti → CandidatParti
    """
    print("\n" + "=" * 80)
    print("CHARGEMENT RÉFÉRENTIELS ÉLECTORAUX")
    print("=" * 80)

    with get_session() as session:
        # TypeElection
        print(f"\n> Type d'élection...")
        type_inserted = load_type_election(session)

        # Elections
        print(f"\n> Élections...")
        elections_inserted = load_elections(session)

        # Candidats
        print(f"\n> Candidats...")
        candidats_inserted = load_candidats(session)

        # Partis
        print(f"\n> Partis...")
        partis_inserted = load_partis(session)

        # Affiliations
        print(f"\n> Affiliations candidat-parti...")
        affiliations_inserted = load_candidat_parti(session)

    total = type_inserted + elections_inserted + candidats_inserted + partis_inserted + affiliations_inserted

    result = {
        "type_election_inserted": type_inserted,
        "elections_inserted": elections_inserted,
        "candidats_inserted": candidats_inserted,
        "partis_inserted": partis_inserted,
        "affiliations_inserted": affiliations_inserted,
        "inserted": total,
        "source": "CSV transformés + config statique",
    }

    print("\n" + "=" * 80)
    print(f"[OK] CHARGEMENT RÉFÉRENTIELS TERMINÉ ({total} insertions)")
    print("=" * 80 + "\n")

    return result
