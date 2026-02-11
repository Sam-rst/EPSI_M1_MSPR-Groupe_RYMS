"""
Modèles SQLAlchemy ORM - Electio-Analytics v3.0.

Ce module contient tous les modèles de base de données définis avec SQLAlchemy ORM.
Ces modèles sont utilisés pour :
- Migrations Alembic
- API REST (FastAPI)
- Validations et contraintes
- Sauvegarde des prédictions ML

Usage:
    >>> from database.models import Candidat, Parti, ResultatCandidat
    >>> from database.config import get_session
    >>>
    >>> with get_session() as session:
    ...     candidat = session.query(Candidat).first()
    ...     print(candidat.nom_complet)
"""

from .base import Base

# Hiérarchie géographique
from .region import Region
from .departement import Departement
from .canton import Canton
from .commune import Commune
from .arrondissement import Arrondissement
from .bureau_vote import BureauVote

# Candidats & Partis
from .parti import Parti
from .candidat import Candidat
from .candidat_parti import CandidatParti

# Élections
from .type_election import TypeElection
from .election import Election
from .election_territoire import ElectionTerritoire

# Résultats
from .resultat_participation import ResultatParticipation
from .resultat_candidat import ResultatCandidat

# Indicateurs socio-économiques (mis à jour avec système polymorphe)
from .type_indicateur import TypeIndicateur
from .indicateur import Indicateur

# Prédictions ML
from .prediction import Prediction

# Ordre d'import important pour Alembic (dépendances FK)
# IMPORTANT: Respecter l'ordre hiérarchique pour éviter erreurs FK
__all__ = [
    # Base
    "Base",

    # Hiérarchie géographique
    "Region",
    "Departement",
    "Canton",
    "Commune",
    "Arrondissement",
    "BureauVote",

    # Candidats & Partis
    "Parti",
    "Candidat",
    "CandidatParti",

    # Élections
    "TypeElection",
    "Election",
    "ElectionTerritoire",

    # Résultats
    "ResultatParticipation",
    "ResultatCandidat",

    # Indicateurs
    "TypeIndicateur",
    "Indicateur",

    # Prédictions
    "Prediction",
]

__version__ = "3.0.0"
