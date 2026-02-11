"""
Modèle TypeElection - Types d'élections (Présidentielle, Législative, etc.).
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from .base import Base


class TypeElection(Base):
    """Types d'élections (PRES, LEG, MUN, EUR, REG)."""

    __tablename__ = "type_election"

    id_type_election = Column(Integer, primary_key=True, autoincrement=True)
    code_type = Column(String(20), unique=True, nullable=False, index=True)
    nom_type = Column(String(100), nullable=False)
    mode_scrutin = Column(String(50), nullable=True)  # Ex: "uninominal_2tours", "proportionnel"
    niveau_geographique = Column(String(50), nullable=True)  # Ex: "national", "circonscription", "commune"
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "code_type IN ('PRES', 'LEG', 'MUN', 'EUR', 'REG', 'DEP', 'SENAT')",
            name="check_code_type"
        ),
    )

    def __repr__(self):
        return f"<TypeElection(code={self.code_type}, nom={self.nom_type})>"
