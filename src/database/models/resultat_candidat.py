"""
Modèle ResultatCandidat - Résultats par candidat et territoire/tour.
"""

from sqlalchemy import Column, BigInteger, Integer, String, Numeric, JSON, TIMESTAMP, ForeignKey, ForeignKeyConstraint, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class ResultatCandidat(Base):
    """
    Résultats individuels de chaque candidat par territoire et tour.

    N lignes = 1 territoire × 1 tour × N candidats.
    """

    __tablename__ = "resultat_candidat"

    id_resultat_cand = Column(BigInteger, primary_key=True, autoincrement=True)
    id_election = Column(Integer, nullable=False, index=True)
    id_candidat = Column(Integer, ForeignKey("candidat.id_candidat", ondelete="CASCADE"), nullable=False, index=True)
    id_territoire = Column(String(15), nullable=False)
    type_territoire = Column(String(20), nullable=False)
    tour = Column(Integer, nullable=False, index=True)

    # Résultats du candidat
    nombre_voix = Column(Integer, nullable=False)
    pourcentage_voix_inscrits = Column(Numeric(5, 2), nullable=True)  # % Voix/Ins
    pourcentage_voix_exprimes = Column(Numeric(5, 2), nullable=True)  # % Voix/Exp

    metadata_ = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id_election", "id_territoire", "type_territoire"],
            ["election_territoire.id_election", "election_territoire.id_territoire", "election_territoire.type_territoire"],
            ondelete="CASCADE"
        ),
        UniqueConstraint("id_election", "id_candidat", "id_territoire", "type_territoire", "tour", name="uq_resultat_election_candidat_territoire_tour"),
        CheckConstraint("tour IN (1, 2)", name="check_tour_candidat"),
        CheckConstraint("nombre_voix >= 0", name="check_nombre_voix"),
        CheckConstraint("pourcentage_voix_inscrits IS NULL OR pourcentage_voix_inscrits BETWEEN 0 AND 100", name="check_pct_inscrits"),
        CheckConstraint("pourcentage_voix_exprimes IS NULL OR pourcentage_voix_exprimes BETWEEN 0 AND 100", name="check_pct_exprimes"),
        CheckConstraint(
            "type_territoire IN ('BUREAU', 'CANTON', 'COMMUNE', 'ARRONDISSEMENT', 'DEPARTEMENT', 'REGION', 'NATIONAL')",
            name="check_type_territoire_candidat"
        ),
    )

    def __repr__(self):
        return f"<ResultatCandidat(election_id={self.id_election}, candidat_id={self.id_candidat}, territoire={self.id_territoire}, tour={self.tour})>"
