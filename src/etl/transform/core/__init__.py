"""
Package core pour la transformation de données.

Modules:
    - geographie.py : Transformation hiérarchie géographique
    - elections.py : Transformation élections (dataset agrégé)
    - securite.py : Transformation données SSMSI

Auteur: @de (Data Engineer)
"""

from .geographie import transform_geographie
from .elections import transform_elections
from .securite import transform_securite

__all__ = [
    "transform_geographie",
    "transform_elections",
    "transform_securite",
]
