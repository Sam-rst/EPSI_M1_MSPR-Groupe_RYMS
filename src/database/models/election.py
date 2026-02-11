"""
Modèle Election - Événements électoraux.
"""

from sqlalchemy import Column, Integer, Date, Text, JSON, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class Election(Base):
    """Événements électoraux (ex: Présidentielles 2022)."""

    __tablename__ = "election"

    id_election = Column(Integer, primary_key=True, autoincrement=True)
    id_type_election = Column(Integer, ForeignKey("type_election.id_type_election", ondelete="CASCADE"), nullable=False, index=True)
    annee = Column(Integer, nullable=False, index=True)
    date_tour1 = Column(Date, nullable=False)
    date_tour2 = Column(Date, nullable=True)
    nombre_tours = Column(Integer, server_default="1", nullable=False)
    contexte = Column(Text, nullable=True)  # Ex: "Contexte COVID-19, crise sanitaire"
    metadata_ = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_type_election", "annee", "date_tour1", name="uq_type_annee_date"),
        CheckConstraint("annee BETWEEN 1900 AND 2100", name="check_annee"),
        CheckConstraint("nombre_tours IN (1, 2)", name="check_nombre_tours"),
        CheckConstraint("date_tour2 IS NULL OR date_tour2 > date_tour1", name="check_dates_tours"),
    )

    def __repr__(self):
        return f"<Election(annee={self.annee}, type_id={self.id_type_election})>"
