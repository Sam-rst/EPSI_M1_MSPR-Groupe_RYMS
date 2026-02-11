"""
Modèle Commune - Communes françaises.
"""

from sqlalchemy import Column, String, Integer, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Commune(Base):
    """Communes françaises (niveau 3 hiérarchie géographique)."""

    __tablename__ = "commune"

    id_commune = Column(String(5), primary_key=True)  # Ex: '33063' = Bordeaux
    id_departement = Column(String(3), ForeignKey("departement.id_departement", ondelete="CASCADE"), nullable=False, index=True)
    code_insee = Column(String(5), unique=True, nullable=False, index=True)
    nom_commune = Column(String(100), nullable=False)
    population = Column(Integer, nullable=True)
    superficie_km2 = Column(Numeric(10, 2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Commune(id={self.id_commune}, nom={self.nom_commune})>"
