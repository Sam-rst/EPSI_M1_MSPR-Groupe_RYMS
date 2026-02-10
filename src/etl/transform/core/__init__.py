"""
Package core pour la transformation de données.

Contient la logique métier pour la transformation de chaque source de données.

Modules:
    - elections.py : Transformation des élections présidentielles
    - securite.py : Transformation des données SSMSI

Auteur: @de (Data Engineer)
"""

from .elections import transform_elections
from .securite import transform_securite

__all__ = [
    "transform_elections",
    "transform_securite",
]
