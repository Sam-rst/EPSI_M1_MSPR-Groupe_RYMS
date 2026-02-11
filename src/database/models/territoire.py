"""
Modèle ORM : Territoire.

Référentiel géographique stable (IRIS, Bureaux de vote, Communes, Arrondissements).
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

from .base import Base


class Territoire(Base):
    """
    Entité Territoire : Référentiel géographique.

    Attributes:
        id_territoire: Identifiant unique (PK)
        code_insee: Code INSEE commune (ex: 33063 = Bordeaux)
        type_territoire: Type géographique (COMMUNE, IRIS, BUREAU_VOTE, ARRONDISSEMENT)
        nom_territoire: Nom lisible
        geometry: Polygone géospatial (PostGIS, optionnel)
        population: Population totale
        metadata_: Métadonnées flexibles (JSONB)
        created_at: Date de création
        updated_at: Date de dernière modification

    Relations:
        - election_results: Résultats électoraux associés (1:N)
        - indicateurs: Indicateurs socio-économiques (1:N)
        - predictions: Prédictions ML (1:N)

    Example:
        >>> territoire = Territoire(
        ...     id_territoire='33063',
        ...     code_insee='33063',
        ...     type_territoire='COMMUNE',
        ...     nom_territoire='Bordeaux',
        ...     population=252040
        ... )
    """

    __tablename__ = "territoire"

    # Colonnes
    id_territoire = Column(String(20), primary_key=True, comment="Identifiant unique territoire")
    code_insee = Column(String(5), nullable=False, comment="Code INSEE commune")
    type_territoire = Column(
        String(20),
        nullable=False,
        comment="Type: COMMUNE, IRIS, BUREAU_VOTE, ARRONDISSEMENT"
    )
    nom_territoire = Column(String(100), nullable=False, comment="Nom lisible")
    geometry = Column(
        Geometry('POLYGON', srid=4326),
        nullable=True,
        comment="Polygone géographique WGS84 (PostGIS)"
    )
    population = Column(Integer, nullable=True, comment="Population totale")
    metadata_ = Column(
        "metadata",  # Nom colonne en DB
        JSONB,
        nullable=True,
        comment="Métadonnées flexibles : superficie, coordonnées_centre, etc."
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Contraintes CHECK
    __table_args__ = (
        CheckConstraint(
            "type_territoire IN ('COMMUNE', 'IRIS', 'BUREAU_VOTE', 'ARRONDISSEMENT')",
            name='ck_territoire_type'
        ),
        CheckConstraint(
            "population >= 0",
            name='ck_territoire_population'
        ),
        # Indexes
        Index('idx_territoire_insee', 'code_insee'),
        Index('idx_territoire_type', 'type_territoire'),
    )

    # Relations ORM (lazy loading par défaut)
    election_results = relationship(
        "ElectionResult",
        back_populates="territoire",
        cascade="all, delete-orphan",
        lazy="select"
    )

    indicateurs = relationship(
        "Indicateur",
        back_populates="territoire",
        cascade="all, delete-orphan",
        lazy="select"
    )

    predictions = relationship(
        "Prediction",
        back_populates="territoire",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Territoire(id='{self.id_territoire}', nom='{self.nom_territoire}', type='{self.type_territoire}')>"
