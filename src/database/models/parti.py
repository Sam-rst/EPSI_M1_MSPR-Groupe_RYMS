"""
Modèle Parti - Référentiel des partis politiques.
"""

from sqlalchemy import Column, Integer, String, Numeric, Date, JSON, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Parti(Base):
    """Référentiel des partis politiques français."""

    __tablename__ = "parti"

    id_parti = Column(Integer, primary_key=True, autoincrement=True)
    code_parti = Column(String(20), unique=True, nullable=False, index=True)
    nom_officiel = Column(String(200), nullable=False)
    nom_court = Column(String(100), nullable=True)
    classification_ideologique = Column(String(50), nullable=True, index=True)
    position_economique = Column(Numeric(3, 2), nullable=True)  # -1.0 (gauche) à +1.0 (droite)
    position_sociale = Column(Numeric(3, 2), nullable=True)     # -1.0 (libéral) à +1.0 (conservateur)
    couleur_hex = Column(String(7), nullable=True)  # Ex: #FF5733
    logo_url = Column(String(500), nullable=True)
    date_creation = Column(Date, nullable=True)
    date_dissolution = Column(Date, nullable=True)
    successeur_id = Column(Integer, ForeignKey("parti.id_parti", ondelete="SET NULL"), nullable=True)
    metadata_ = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("position_economique BETWEEN -1.0 AND 1.0", name="check_position_economique"),
        CheckConstraint("position_sociale BETWEEN -1.0 AND 1.0", name="check_position_sociale"),
        CheckConstraint(
            "classification_ideologique IN ('extreme_gauche', 'gauche', 'centre_gauche', 'centre', 'centre_droit', 'droite', 'extreme_droite', 'autre')",
            name="check_classification_ideologique"
        ),
        CheckConstraint("date_dissolution IS NULL OR date_dissolution >= date_creation", name="check_dates_parti"),
    )

    def __repr__(self):
        return f"<Parti(code={self.code_parti}, nom={self.nom_court or self.nom_officiel})>"
