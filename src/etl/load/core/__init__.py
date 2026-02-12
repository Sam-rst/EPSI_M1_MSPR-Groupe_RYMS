"""
Package de fonctions core pour le module Load ETL v3.0.

Ordre de chargement (respect des FK):
1. Géographie : Region → Departement → Commune
2. Types d'indicateurs : TypeIndicateur (référentiel statique)
3. Candidats & Élections : TypeElection → Election → Candidat → Parti → CandidatParti
4. Résultats : ElectionTerritoire → ResultatParticipation → ResultatCandidat
5. Indicateurs : Indicateur (polymorphe)
"""

from .geographie import run_load_geographie
from .type_indicateur import (
    load_types_indicateurs,
    run_load_types_indicateurs,
)
from .candidats import run_load_candidats
from .elections import run_load_elections
from .indicateurs import (
    load_indicateurs_from_csv,
    run_load_securite,
)

__all__ = [
    "run_load_geographie",
    "load_types_indicateurs",
    "run_load_types_indicateurs",
    "run_load_candidats",
    "run_load_elections",
    "load_indicateurs_from_csv",
    "run_load_securite",
]
