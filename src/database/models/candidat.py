"""
Modèle Candidat - Référentiel des candidats aux élections.
"""

from sqlalchemy import Column, Integer, String, Date, Text, JSON, TIMESTAMP, CheckConstraint, Computed
from sqlalchemy.sql import func
from .base import Base


class Candidat(Base):
    """Référentiel des candidats aux élections."""

    __tablename__ = "candidat"

    id_candidat = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    nom_complet = Column(
        String(200),
        Computed("prenom || ' ' || nom"),
        index=True
    )
    date_naissance = Column(Date, nullable=True)
    profession = Column(String(200), nullable=True)
    biographie = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    metadata_ = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("date_naissance IS NULL OR date_naissance <= CURRENT_DATE", name="check_date_naissance"),
    )

    def __repr__(self):
        return f"<Candidat(nom_complet={self.prenom} {self.nom})>"
