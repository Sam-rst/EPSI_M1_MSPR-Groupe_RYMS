"""
Modèle ORM : TypeIndicateur.

Catalogue centralisé des types d'indicateurs socio-économiques.
"""

from sqlalchemy import Column, Integer, String, Text, Date, Boolean, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class TypeIndicateur(Base):
    """
    Entité TypeIndicateur : Catalogue des types d'indicateurs.

    Pattern Catalog : Documentation centralisée des sources de données.

    Attributes:
        id_type: Identifiant auto-incrémenté (PK)
        code_type: Code unique (ex: SECURITE_CAMBRIOLAGES, EMPLOI_TAUX_CHOMAGE)
        categorie: Catégorie macro (SECURITE, EMPLOI, DEMOGRAPHIE)
        nom_affichage: Libellé interface utilisateur
        description: Description détaillée
        unite_mesure: Unité de la valeur (nombre, pourcentage, euros)
        source_officielle: Organisme source (SSMSI, INSEE)
        frequence: Périodicité (ANNUEL, TRIMESTRIEL, MENSUEL)
        date_debut_disponibilite: Première année disponible
        actif: Indicateur activé (soft delete)
        schema_metadata: Schéma JSON de validation (optionnel)
        created_at: Date de création

    Relations:
        - indicateurs: Indicateurs utilisant ce type (1:N)

    Example:
        >>> type_ind = TypeIndicateur(
        ...     code_type='SECURITE_CAMBRIOLAGES',
        ...     categorie='SECURITE',
        ...     nom_affichage='Cambriolages de logement',
        ...     unite_mesure='nombre',
        ...     source_officielle='SSMSI',
        ...     frequence='ANNUEL'
        ... )
    """

    __tablename__ = "type_indicateur"

    # Colonnes
    id_type = Column(Integer, primary_key=True, autoincrement=True, comment="Identifiant auto-incrémenté")
    code_type = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="Code unique identifiant (MAJUSCULE_SNAKE_CASE)"
    )
    categorie = Column(String(50), nullable=False, comment="Catégorie macro")
    nom_affichage = Column(String(100), nullable=False, comment="Libellé interface utilisateur")
    description = Column(Text, nullable=True, comment="Description détaillée")
    unite_mesure = Column(String(50), nullable=True, comment="Unité : nombre, pourcentage, euros")
    source_officielle = Column(String(100), nullable=True, comment="Organisme source")
    frequence = Column(String(20), nullable=True, comment="Périodicité : ANNUEL, TRIMESTRIEL, MENSUEL")
    date_debut_disponibilite = Column(Date, nullable=True, comment="Première année disponible")
    actif = Column(Boolean, default=True, nullable=False, comment="Soft delete")
    schema_metadata = Column(JSONB, nullable=True, comment="Schéma JSON validation métadonnées")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_type_indicateur_categorie', 'categorie'),
        Index('idx_type_indicateur_code', 'code_type'),
    )

    # Relations ORM
    indicateurs = relationship(
        "Indicateur",
        back_populates="type_indicateur",
        lazy="select"
    )

    def __repr__(self):
        return f"<TypeIndicateur(id={self.id_type}, code='{self.code_type}', categorie='{self.categorie}')>"
