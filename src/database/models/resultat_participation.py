"""
Modèle ResultatParticipation - Statistiques de participation par territoire/tour.
"""

from sqlalchemy import Column, BigInteger, Integer, String, Numeric, JSON, TIMESTAMP, ForeignKeyConstraint, CheckConstraint, UniqueConstraint, Computed
from sqlalchemy.sql import func
from .base import Base


class ResultatParticipation(Base):
    """
    Statistiques générales de participation par territoire et tour.

    1 ligne = 1 territoire × 1 tour (indépendamment du nombre de candidats).
    """

    __tablename__ = "resultat_participation"

    id_resultat_part = Column(BigInteger, primary_key=True, autoincrement=True)
    id_election = Column(Integer, nullable=False, index=True)
    id_territoire = Column(String(15), nullable=False)
    type_territoire = Column(String(20), nullable=False)
    tour = Column(Integer, nullable=False, index=True)

    # Statistiques de participation
    nombre_inscrits = Column(Integer, nullable=False)
    nombre_abstentions = Column(Integer, nullable=False)
    nombre_votants = Column(Integer, nullable=False)
    nombre_blancs_nuls = Column(Integer, nullable=False)
    nombre_exprimes = Column(Integer, nullable=False)

    # Pourcentages calculés automatiquement
    pourcentage_abstentions = Column(
        Numeric(5, 2),
        Computed("CASE WHEN nombre_inscrits > 0 THEN ROUND((nombre_abstentions::NUMERIC / nombre_inscrits * 100), 2) ELSE NULL END")
    )
    pourcentage_votants = Column(
        Numeric(5, 2),
        Computed("CASE WHEN nombre_inscrits > 0 THEN ROUND((nombre_votants::NUMERIC / nombre_inscrits * 100), 2) ELSE NULL END")
    )
    pourcentage_blancs_nuls_inscrits = Column(
        Numeric(5, 2),
        Computed("CASE WHEN nombre_inscrits > 0 THEN ROUND((nombre_blancs_nuls::NUMERIC / nombre_inscrits * 100), 2) ELSE NULL END")
    )
    pourcentage_blancs_nuls_votants = Column(
        Numeric(5, 2),
        Computed("CASE WHEN nombre_votants > 0 THEN ROUND((nombre_blancs_nuls::NUMERIC / nombre_votants * 100), 2) ELSE NULL END")
    )
    pourcentage_exprimes_inscrits = Column(
        Numeric(5, 2),
        Computed("CASE WHEN nombre_inscrits > 0 THEN ROUND((nombre_exprimes::NUMERIC / nombre_inscrits * 100), 2) ELSE NULL END")
    )
    pourcentage_exprimes_votants = Column(
        Numeric(5, 2),
        Computed("CASE WHEN nombre_votants > 0 THEN ROUND((nombre_exprimes::NUMERIC / nombre_votants * 100), 2) ELSE NULL END")
    )

    metadata_ = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id_election", "id_territoire", "type_territoire"],
            ["election_territoire.id_election", "election_territoire.id_territoire", "election_territoire.type_territoire"],
            ondelete="CASCADE"
        ),
        UniqueConstraint("id_election", "id_territoire", "type_territoire", "tour", name="uq_participation_election_territoire_tour"),
        CheckConstraint("tour IN (1, 2)", name="check_tour_participation"),
        CheckConstraint(
            "type_territoire IN ('BUREAU', 'CANTON', 'COMMUNE', 'ARRONDISSEMENT', 'DEPARTEMENT', 'REGION', 'NATIONAL')",
            name="check_type_territoire_participation"
        ),
        CheckConstraint("nombre_inscrits >= 0", name="check_inscrits"),
        CheckConstraint("nombre_abstentions >= 0", name="check_abstentions"),
        CheckConstraint("nombre_votants >= 0", name="check_votants"),
        CheckConstraint("nombre_blancs_nuls >= 0", name="check_blancs_nuls"),
        CheckConstraint("nombre_exprimes >= 0", name="check_exprimes"),
        CheckConstraint("nombre_votants + nombre_abstentions = nombre_inscrits", name="check_coherence_inscrits"),
        CheckConstraint("nombre_exprimes + nombre_blancs_nuls = nombre_votants", name="check_coherence_votants"),
    )

    def __repr__(self):
        return f"<ResultatParticipation(election_id={self.id_election}, territoire={self.id_territoire}, tour={self.tour})>"
