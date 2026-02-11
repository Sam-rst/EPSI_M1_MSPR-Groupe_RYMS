"""
Modèle ORM : Indicateur.

Table générique pour TOUS les indicateurs socio-économiques (Pattern EAV).
Utilise le système polymorphe de territoire (id_territoire + type_territoire).
"""

from sqlalchemy import Column, BigInteger, String, Integer, Text, TIMESTAMP, CheckConstraint, Index, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Indicateur(Base):
    """
    Entité Indicateur : Table générique pour tous les indicateurs.

    Pattern EAV (Entity-Attribute-Value) : Permet l'ajout dynamique de nouvelles sources.
    Système polymorphe : Supporte multi-granularités (COMMUNE, CANTON, DEPARTEMENT, etc.)

    Attributes:
        id_indicateur: Identifiant auto-incrémenté (PK)
        id_territoire: Identifiant polymorphe du territoire (ex: '33063', '3301', '33')
        type_territoire: Type de territoire (COMMUNE, CANTON, DEPARTEMENT, REGION, NATIONAL)
        id_type: Référence type_indicateur (FK)
        annee: Année de référence (2000-2100)
        periode: Période infra-annuelle (T1-T4, M01-M12, NULL si annuel)
        valeur_numerique: Valeur principale (nombre, pourcentage, euros)
        valeur_texte: Valeur qualitative (optionnel)
        metadata_: Métadonnées variables selon type (JSONB)
        source_detail: Source précise
        fiabilite: Niveau de fiabilité (CONFIRME, ESTIME, PROVISOIRE, REVISION)
        created_at: Date d'insertion

    Relations:
        - type_indicateur: Type d'indicateur (N:1)

    Contrainte Unicité:
        (id_territoire, type_territoire, id_type, annee, periode) → Un seul indicateur par combinaison

    Example:
        >>> # Indicateur communal
        >>> indicateur = Indicateur(
        ...     id_territoire='33063',
        ...     type_territoire='COMMUNE',
        ...     id_type=1,
        ...     annee=2022,
        ...     periode=None,
        ...     valeur_numerique=504.0,
        ...     metadata_={'taux_pour_1000_hab': 2.0},
        ...     fiabilite='CONFIRME'
        ... )
        >>> # Indicateur départemental
        >>> indicateur_dept = Indicateur(
        ...     id_territoire='33',
        ...     type_territoire='DEPARTEMENT',
        ...     id_type=1,
        ...     annee=2022,
        ...     valeur_numerique=15420.0,
        ...     fiabilite='CONFIRME'
        ... )
    """

    __tablename__ = "indicateur"

    # Colonnes
    id_indicateur = Column(BigInteger, primary_key=True, autoincrement=True)

    # Système polymorphe de territoire (comme resultat_participation/candidat)
    id_territoire = Column(String(15), nullable=False, comment="ID polymorphe du territoire")
    type_territoire = Column(String(20), nullable=False, comment="Type de territoire")

    id_type = Column(
        Integer,
        ForeignKey('type_indicateur.id_type', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False,
        index=True
    )
    annee = Column(Integer, nullable=False, index=True, comment="Année référence (2000-2100)")
    periode = Column(String(20), nullable=True, comment="T1-T4, M01-M12, NULL (annuel)")
    valeur_numerique = Column("valeur_numerique", Numeric(15, 4), nullable=True, comment="Valeur principale")
    valeur_texte = Column(Text, nullable=True, comment="Valeur qualitative")
    metadata_ = Column("metadata", JSONB, nullable=True, comment="Métadonnées variables selon type")
    source_detail = Column(String(200), nullable=True, comment="Source précise")
    fiabilite = Column(
        String(20),
        default='CONFIRME',
        nullable=False,
        comment="CONFIRME, ESTIME, PROVISOIRE, REVISION"
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Contraintes
    __table_args__ = (
        # CHECK constraints
        CheckConstraint(
            "annee BETWEEN 2000 AND 2100",
            name='ck_indicateur_annee'
        ),
        CheckConstraint(
            "fiabilite IN ('CONFIRME', 'ESTIME', 'PROVISOIRE', 'REVISION')",
            name='ck_indicateur_fiabilite'
        ),
        CheckConstraint(
            "type_territoire IN ('BUREAU', 'CANTON', 'COMMUNE', 'ARRONDISSEMENT', 'DEPARTEMENT', 'REGION', 'NATIONAL')",
            name='ck_indicateur_type_territoire'
        ),
        # Contrainte unicité (ajout type_territoire)
        UniqueConstraint(
            'id_territoire', 'type_territoire', 'id_type', 'annee', 'periode',
            name='unique_indicateur_territoire_type'
        ),
        # Indexes pour performance ML
        Index('idx_indicateur_territoire', 'id_territoire', 'type_territoire'),
        Index('idx_indicateur_type', 'id_type'),
        Index('idx_indicateur_annee', 'annee'),
        Index('idx_indicateur_composite', 'id_territoire', 'type_territoire', 'id_type', 'annee'),
        Index('idx_indicateur_metadata', metadata_, postgresql_using='gin'),  # Index GIN sur JSONB
    )

    # Relations ORM
    type_indicateur = relationship("TypeIndicateur", back_populates="indicateurs")

    def __repr__(self):
        return f"<Indicateur(id={self.id_indicateur}, territoire='{self.id_territoire}', type_terr='{self.type_territoire}', type={self.id_type}, annee={self.annee})>"
