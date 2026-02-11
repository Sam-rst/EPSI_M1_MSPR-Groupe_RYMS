"""
Modèle Canton - Cantons (granularité électorale alternative).
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Canton(Base):
    """Cantons (granularité électorale parallèle à commune)."""

    __tablename__ = "canton"

    id_canton = Column(String(10), primary_key=True)  # Ex: '3301' = Canton 1 de la Gironde
    id_departement = Column(String(3), ForeignKey("departement.id_departement", ondelete="CASCADE"), nullable=False, index=True)
    code_canton = Column(String(10), nullable=False)
    numero_canton = Column(Integer, nullable=True)
    nom_canton = Column(String(100), nullable=False)
    population = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Canton(id={self.id_canton}, nom={self.nom_canton})>"
