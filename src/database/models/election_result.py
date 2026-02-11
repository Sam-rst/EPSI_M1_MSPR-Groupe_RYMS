"""
Modèle ORM : ElectionResult.

Résultats électoraux présidentielles 2017 & 2022 (1er et 2nd tours).
"""

from sqlalchemy import Column, BigInteger, String, Integer, TIMESTAMP, CheckConstraint, Index, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class ElectionResult(Base):
    """
    Entité ElectionResult : Résultats électoraux.

    Table spécialisée pour performance (volume élevé, schéma stable).

    Attributes:
        id_result: Identifiant auto-incrémenté (PK)
        id_territoire: Référence territoire (FK)
        annee: Année élection (2000-2100)
        tour: Tour (1 ou 2)
        candidat: Nom complet candidat
        parti: Parti politique
        nombre_voix: Voix obtenues
        pourcentage_voix: % voix exprimées (0-100)
        nombre_inscrits: Nombre d'inscrits
        nombre_votants: Nombre de votants
        nombre_exprimes: Nombre de voix exprimées
        taux_participation: % participation (0-100)
        metadata_: Métadonnées additionnelles (JSONB)
        created_at: Date d'insertion

    Relations:
        - territoire: Territoire associé (N:1)

    Contrainte Unicité:
        (id_territoire, annee, tour, candidat) → Un résultat par candidat/bureau/tour

    Example:
        >>> result = ElectionResult(
        ...     id_territoire='BV_33063_001',
        ...     annee=2022,
        ...     tour=1,
        ...     candidat='Emmanuel MACRON',
        ...     parti='LREM',
        ...     nombre_voix=450,
        ...     pourcentage_voix=28.45,
        ...     nombre_inscrits=1500,
        ...     nombre_votants=1130,
        ...     nombre_exprimes=1100,
        ...     taux_participation=75.33
        ... )
    """

    __tablename__ = "election_result"

    # Colonnes
    id_result = Column(BigInteger, primary_key=True, autoincrement=True)
    id_territoire = Column(
        String(20),
        ForeignKey('territoire.id_territoire', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    annee = Column(Integer, nullable=False, comment="Année élection")
    tour = Column(Integer, nullable=False, comment="Tour (1 ou 2)")
    candidat = Column(String(100), nullable=False, comment="Nom complet candidat")
    parti = Column(String(50), nullable=True, comment="Parti politique")
    nombre_voix = Column(Integer, nullable=False, comment="Voix obtenues")
    pourcentage_voix = Column(Numeric(5, 2), nullable=False, comment="% voix exprimées")
    nombre_inscrits = Column(Integer, nullable=True, comment="Nombre d'inscrits")
    nombre_votants = Column(Integer, nullable=True, comment="Nombre de votants")
    nombre_exprimes = Column(Integer, nullable=True, comment="Nombre de voix exprimées")
    taux_participation = Column(Numeric(5, 2), nullable=True, comment="% participation")
    metadata_ = Column("metadata", JSONB, nullable=True, comment="Métadonnées : nuance politique, etc.")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Contraintes
    __table_args__ = (
        # CHECK constraints
        CheckConstraint("annee BETWEEN 2000 AND 2100", name='ck_election_annee'),
        CheckConstraint("tour IN (1, 2)", name='ck_election_tour'),
        CheckConstraint("nombre_voix >= 0", name='ck_election_voix'),
        CheckConstraint("pourcentage_voix BETWEEN 0 AND 100", name='ck_election_pct_voix'),
        CheckConstraint("nombre_inscrits >= 0", name='ck_election_inscrits'),
        CheckConstraint("nombre_votants >= 0", name='ck_election_votants'),
        CheckConstraint("nombre_exprimes >= 0", name='ck_election_exprimes'),
        CheckConstraint("taux_participation BETWEEN 0 AND 100", name='ck_election_taux_part'),
        # Contrainte unicité
        UniqueConstraint(
            'id_territoire', 'annee', 'tour', 'candidat',
            name='unique_election_result'
        ),
        # Indexes
        Index('idx_election_territoire', 'id_territoire'),
        Index('idx_election_annee_tour', 'annee', 'tour'),
        Index('idx_election_candidat', 'candidat'),
        Index('idx_election_composite', 'id_territoire', 'annee', 'tour'),
    )

    # Relations ORM
    territoire = relationship("Territoire", back_populates="election_results")

    def __repr__(self):
        return f"<ElectionResult(territoire='{self.id_territoire}', annee={self.annee}, tour={self.tour}, candidat='{self.candidat}')>"
