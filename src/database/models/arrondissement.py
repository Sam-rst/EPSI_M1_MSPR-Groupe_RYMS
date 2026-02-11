"""
Modèle Arrondissement - Arrondissements (grandes villes).
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Arrondissement(Base):
    """Arrondissements (optionnel, pour grandes villes comme Paris, Lyon, Marseille)."""

    __tablename__ = "arrondissement"

    id_arrondissement = Column(String(10), primary_key=True)  # Ex: '33063_01' = Bordeaux Centre
    id_commune = Column(String(5), ForeignKey("commune.id_commune", ondelete="CASCADE"), nullable=False, index=True)
    numero_arrondissement = Column(Integer, nullable=True)
    nom_arrondissement = Column(String(100), nullable=True)
    population = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Arrondissement(id={self.id_arrondissement}, nom={self.nom_arrondissement})>"
