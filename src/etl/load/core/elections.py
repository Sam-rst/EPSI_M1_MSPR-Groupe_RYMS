"""
Chargement des résultats électoraux v3.0 dans PostgreSQL.

Charge: ElectionTerritoire → ResultatParticipation → ResultatCandidat.
Utilise le système polymorphe de territoire (id_territoire + type_territoire).

Auteur: @de (Data Engineer)
"""

from typing import Dict, Any
import pandas as pd
from sqlalchemy.orm import Session

from src.database.models import (
    Election,
    ElectionTerritoire,
    ResultatParticipation,
    ResultatCandidat,
    Candidat,
    TypeElection,
)
from src.database.config import get_session
from ..config import (
    PARTICIPATION_CSV,
    CANDIDATS_CSV,
    BATCH_SIZE,
    VERBOSE,
)
from ..utils import validate_csv_exists


def _get_election_id(session: Session, annee: int) -> int:
    """Récupère l'id_election pour une année donnée."""
    election = session.query(Election).filter(Election.annee == annee).first()
    if not election:
        raise ValueError(f"Election non trouvée pour l'année {annee}")
    return election.id_election


def _get_or_create_election_territoire(
    session: Session,
    id_election: int,
    id_territoire: str,
    type_territoire: str,
) -> int:
    """Récupère ou crée un enregistrement ElectionTerritoire."""
    existing = session.query(ElectionTerritoire).filter(
        ElectionTerritoire.id_election == id_election,
        ElectionTerritoire.id_territoire == id_territoire,
        ElectionTerritoire.type_territoire == type_territoire,
    ).first()

    if existing:
        return existing.id_election_territoire

    et = ElectionTerritoire(
        id_election=id_election,
        id_territoire=id_territoire,
        type_territoire=type_territoire,
        granularite_source="COMMUNE",
        source_fichier="data.gouv.fr (dataset agrégé)",
        statut_validation="EN_COURS",
    )
    session.add(et)
    session.flush()  # Pour obtenir l'ID sans commit
    return et.id_election_territoire


def load_participation(session: Session) -> int:
    """
    Charge les résultats de participation depuis le CSV transformé.

    Crée automatiquement les enregistrements ElectionTerritoire nécessaires.
    """
    if not PARTICIPATION_CSV.exists():
        print(f"  [WARN] Fichier participation non trouvé: {PARTICIPATION_CSV}")
        return 0

    validate_csv_exists(PARTICIPATION_CSV)
    df = pd.read_csv(PARTICIPATION_CSV)
    print(f"  Lignes participation: {len(df):,}")

    total_inserted = 0

    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_inserted = 0

        for _, row in batch_df.iterrows():
            annee = int(row["annee"])
            tour = int(row["tour"])
            id_territoire = str(row["id_territoire"]).strip()
            type_territoire = str(row.get("type_territoire", "COMMUNE")).strip()

            # Obtenir l'id_election
            id_election = _get_election_id(session, annee)

            # Obtenir ou créer ElectionTerritoire
            _get_or_create_election_territoire(
                session, id_election, id_territoire, type_territoire
            )

            # Vérifier doublon
            existing = session.query(ResultatParticipation).filter(
                ResultatParticipation.id_election == id_election,
                ResultatParticipation.id_territoire == id_territoire,
                ResultatParticipation.type_territoire == type_territoire,
                ResultatParticipation.tour == tour,
            ).first()

            if existing:
                continue

            inscrits = int(row["nombre_inscrits"])
            abstentions = int(row["nombre_abstentions"])
            votants = int(row["nombre_votants"])
            blancs_nuls = int(row["nombre_blancs_nuls"])
            exprimes = int(row["nombre_exprimes"])

            # Corrections de cohérence si nécessaire
            # Le modèle impose: votants + abstentions = inscrits
            if votants + abstentions != inscrits and inscrits > 0:
                abstentions = inscrits - votants

            # Le modèle impose: exprimes + blancs_nuls = votants
            if exprimes + blancs_nuls != votants and votants > 0:
                blancs_nuls = votants - exprimes

            resultat = ResultatParticipation(
                id_election=id_election,
                id_territoire=id_territoire,
                type_territoire=type_territoire,
                tour=tour,
                nombre_inscrits=inscrits,
                nombre_abstentions=abstentions,
                nombre_votants=votants,
                nombre_blancs_nuls=blancs_nuls,
                nombre_exprimes=exprimes,
            )
            session.add(resultat)
            batch_inserted += 1

        session.commit()
        total_inserted += batch_inserted

        if VERBOSE:
            batch_num = (i // BATCH_SIZE) + 1
            print(f"  Batch {batch_num}: {batch_inserted} participations insérées")

    return total_inserted


def load_resultats_candidats(session: Session) -> int:
    """
    Charge les résultats par candidat depuis le CSV transformé.

    Nécessite que les candidats et les ElectionTerritoire soient déjà chargés.
    """
    if not CANDIDATS_CSV.exists():
        print(f"  [WARN] Fichier candidats non trouvé: {CANDIDATS_CSV}")
        return 0

    validate_csv_exists(CANDIDATS_CSV)
    df = pd.read_csv(CANDIDATS_CSV)
    print(f"  Lignes candidats: {len(df):,}")

    # Construire un cache des candidats (nom, prenom) → id_candidat
    candidats_cache: Dict[tuple, int] = {}
    all_candidats = session.query(Candidat).all()
    for c in all_candidats:
        candidats_cache[(c.nom, c.prenom)] = c.id_candidat

    total_inserted = 0

    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_inserted = 0

        for _, row in batch_df.iterrows():
            annee = int(row["annee"])
            tour = int(row["tour"])
            id_territoire = str(row["id_territoire"]).strip()
            type_territoire = str(row.get("type_territoire", "COMMUNE")).strip()
            nom = str(row["nom"]).strip()
            prenom = str(row["prenom"]).strip()

            # Trouver le candidat
            id_candidat = candidats_cache.get((nom, prenom))
            if not id_candidat:
                continue

            # Obtenir l'id_election
            id_election = _get_election_id(session, annee)

            # Obtenir ou créer ElectionTerritoire
            _get_or_create_election_territoire(
                session, id_election, id_territoire, type_territoire
            )

            # Vérifier doublon
            existing = session.query(ResultatCandidat).filter(
                ResultatCandidat.id_election == id_election,
                ResultatCandidat.id_candidat == id_candidat,
                ResultatCandidat.id_territoire == id_territoire,
                ResultatCandidat.type_territoire == type_territoire,
                ResultatCandidat.tour == tour,
            ).first()

            if existing:
                continue

            voix = int(row.get("nombre_voix", 0))
            pct_ins = float(row.get("pourcentage_voix_inscrits", 0))
            pct_exp = float(row.get("pourcentage_voix_exprimes", 0))

            resultat = ResultatCandidat(
                id_election=id_election,
                id_candidat=id_candidat,
                id_territoire=id_territoire,
                type_territoire=type_territoire,
                tour=tour,
                nombre_voix=voix,
                pourcentage_voix_inscrits=round(pct_ins, 2) if pct_ins > 0 else None,
                pourcentage_voix_exprimes=round(pct_exp, 2) if pct_exp > 0 else None,
            )
            session.add(resultat)
            batch_inserted += 1

        session.commit()
        total_inserted += batch_inserted

        if VERBOSE:
            batch_num = (i // BATCH_SIZE) + 1
            print(f"  Batch {batch_num}: {batch_inserted} résultats candidats insérés")

    return total_inserted


def run_load_elections() -> Dict[str, Any]:
    """
    Point d'entrée pour charger les résultats électoraux v3.0.

    Ordre: ElectionTerritoire → ResultatParticipation → ResultatCandidat
    """
    print("\n" + "=" * 80)
    print("CHARGEMENT DES RÉSULTATS ÉLECTORAUX (v3.0)")
    print("=" * 80)

    with get_session() as session:
        # Participation
        print(f"\n> Résultats participation...")
        participation_inserted = load_participation(session)
        print(f"  [OK] {participation_inserted} participations insérées")

        # Candidats
        print(f"\n> Résultats par candidat...")
        candidats_inserted = load_resultats_candidats(session)
        print(f"  [OK] {candidats_inserted} résultats candidats insérés")

        # Comptages finaux
        et_count = session.query(ElectionTerritoire).count()
        rp_count = session.query(ResultatParticipation).count()
        rc_count = session.query(ResultatCandidat).count()

    total = participation_inserted + candidats_inserted

    result = {
        "participation_inserted": participation_inserted,
        "candidats_inserted": candidats_inserted,
        "election_territoire_count": et_count,
        "resultat_participation_count": rp_count,
        "resultat_candidat_count": rc_count,
        "inserted": total,
        "source": "CSV transformés (dataset agrégé)",
    }

    print("\n" + "=" * 80)
    print(f"[OK] CHARGEMENT RÉSULTATS TERMINÉ ({total} insertions)")
    print(f"     ElectionTerritoire: {et_count}, Participation: {rp_count}, Candidats: {rc_count}")
    print("=" * 80 + "\n")

    return result
