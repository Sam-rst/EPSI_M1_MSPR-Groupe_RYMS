"""
Package core pour l'extraction de données.

Modules:
    - geographie.py : Téléchargement hiérarchie géographique (geo.api.gouv.fr)
    - elections.py : Téléchargement élections agrégées (API tabulaire + Parquet)
    - securite.py : Téléchargement données SSMSI

Auteur: @de (Data Engineer)
"""

from .geographie import download_geographie
from .elections import download_elections
from .securite import download_securite

__all__ = [
    "download_geographie",
    "download_elections",
    "download_securite",
]
