"""
Modèle ElectionTerritoire - Référentiel granularités disponibles par élection.
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class ElectionTerritoire(Base):
    """
    Référentiel des granularités territoriales disponibles pour chaque élection.

    Permet de déclarer qu'une élection a des résultats disponibles au niveau BUREAU, CANTON, etc.
    """

    __tablename__ = "election_territoire"

    id_election_territoire = Column(Integer, primary_key=True, autoincrement=True)
    id_election = Column(Integer, ForeignKey("election.id_election", ondelete="CASCADE"), nullable=False, index=True)
    id_territoire = Column(String(15), nullable=False)  # Polymorphe (id_bureau, id_canton, id_commune, etc.)
    type_territoire = Column(String(20), nullable=False, index=True)  # BUREAU, CANTON, COMMUNE, etc.

    # Métadonnées source
    granularite_source = Column(String(20), nullable=False)
    date_import = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    source_fichier = Column(String(500), nullable=True)
    nombre_resultats_attendus = Column(Integer, nullable=True)
    nombre_resultats_charges = Column(Integer, nullable=True)
    statut_validation = Column(String(20), server_default="'EN_COURS'", nullable=False, index=True)
    metadata_ = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_election", "id_territoire", "type_territoire", name="uq_election_territoire_type"),
        CheckConstraint(
            "type_territoire IN ('BUREAU', 'CANTON', 'COMMUNE', 'ARRONDISSEMENT', 'DEPARTEMENT', 'REGION', 'NATIONAL', 'CIRCONSCRIPTION')",
            name="check_type_territoire"
        ),
        CheckConstraint(
            "statut_validation IN ('EN_COURS', 'VALIDE', 'ERREUR', 'INCOMPLET')",
            name="check_statut_validation"
        ),
        CheckConstraint("nombre_resultats_charges IS NULL OR nombre_resultats_charges >= 0", name="check_nb_resultats"),
    )

    def __repr__(self):
        return f"<ElectionTerritoire(election_id={self.id_election}, territoire={self.id_territoire}, type={self.type_territoire})>"
