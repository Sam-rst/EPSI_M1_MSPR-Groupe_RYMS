"""
Modèle Region - Régions françaises.
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base


class Region(Base):
    """Régions françaises (niveau 1 hiérarchie géographique)."""

    __tablename__ = "region"

    id_region = Column(String(2), primary_key=True)  # Ex: '75' = Nouvelle-Aquitaine
    code_insee = Column(String(2), nullable=False)
    nom_region = Column(String(100), nullable=False)
    population = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Region(id={self.id_region}, nom={self.nom_region})>"
