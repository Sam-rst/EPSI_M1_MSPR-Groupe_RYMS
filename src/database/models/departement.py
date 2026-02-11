"""
Modèle Departement - Départements français.
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Departement(Base):
    """Départements français (niveau 2 hiérarchie géographique)."""

    __tablename__ = "departement"

    id_departement = Column(String(3), primary_key=True)  # Ex: '33' = Gironde
    id_region = Column(String(2), ForeignKey("region.id_region", ondelete="CASCADE"), nullable=False, index=True)
    code_insee = Column(String(3), nullable=False)
    nom_departement = Column(String(100), nullable=False)
    population = Column(Integer, nullable=True)
    chef_lieu = Column(String(5), nullable=True)  # Code INSEE du chef-lieu
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Departement(id={self.id_departement}, nom={self.nom_departement})>"
