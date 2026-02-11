"""
Modèles SQLAlchemy ORM - Electio-Analytics.

Ce module contient tous les modèles de base de données définis avec SQLAlchemy ORM.
Ces modèles sont utilisés pour :
- Migrations Alembic
- API REST (FastAPI)
- Validations et contraintes
- Sauvegarde des prédictions ML

Usage:
    >>> from database.models import Territoire, ElectionResult
    >>> from database.config import get_session
    >>>
    >>> with get_session() as session:
    ...     territoire = session.query(Territoire).first()
    ...     print(territoire.nom_territoire)
"""

from .base import Base
from .territoire import Territoire
from .type_indicateur import TypeIndicateur
from .indicateur import Indicateur
from .election_result import ElectionResult
from .prediction import Prediction

# Ordre d'import important pour Alembic (dépendances FK)
__all__ = [
    "Base",
    "Territoire",
    "TypeIndicateur",
    "Indicateur",
    "ElectionResult",
    "Prediction",
]

__version__ = "2.0.0"
