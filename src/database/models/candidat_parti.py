"""
Modèle CandidatParti - Association candidat ↔ parti (historique affiliations).
"""

from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class CandidatParti(Base):
    """Historique des affiliations candidat ↔ parti."""

    __tablename__ = "candidat_parti"

    id_affiliation = Column(Integer, primary_key=True, autoincrement=True)
    id_candidat = Column(Integer, ForeignKey("candidat.id_candidat", ondelete="CASCADE"), nullable=False, index=True)
    id_parti = Column(Integer, ForeignKey("parti.id_parti", ondelete="CASCADE"), nullable=False, index=True)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)  # NULL = affiliation actuelle
    fonction = Column(String(200), nullable=True)  # Ex: "Président", "Membre", "Sympathisant"
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_candidat", "id_parti", "date_debut", name="uq_candidat_parti_date"),
        CheckConstraint("date_fin IS NULL OR date_fin >= date_debut", name="check_dates_affiliation"),
    )

    def __repr__(self):
        return f"<CandidatParti(candidat_id={self.id_candidat}, parti_id={self.id_parti}, debut={self.date_debut})>"
