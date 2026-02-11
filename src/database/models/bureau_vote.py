"""
Modèle BureauVote - Bureaux de vote.
"""

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class BureauVote(Base):
    """Bureaux de vote (niveau le plus fin de granularité)."""

    __tablename__ = "bureau_vote"

    id_bureau = Column(String(15), primary_key=True)  # Ex: '33063_BV_001'
    id_commune = Column(String(5), ForeignKey("commune.id_commune", ondelete="CASCADE"), nullable=False, index=True)
    id_arrondissement = Column(String(10), ForeignKey("arrondissement.id_arrondissement", ondelete="SET NULL"), nullable=True, index=True)
    code_bureau = Column(String(10), nullable=False)
    nom_bureau = Column(String(200), nullable=True)
    adresse = Column(Text, nullable=True)
    nombre_inscrits = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_commune", "code_bureau", name="uq_commune_code_bureau"),
    )

    def __repr__(self):
        return f"<BureauVote(id={self.id_bureau}, nom={self.nom_bureau})>"
