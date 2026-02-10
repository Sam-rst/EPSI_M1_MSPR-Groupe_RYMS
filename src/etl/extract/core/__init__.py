"""
Package core pour l'extraction de données.

Contient la logique métier pour le téléchargement de chaque source de données.

Modules:
    - elections.py : Téléchargement des élections présidentielles
    - securite.py : Téléchargement des données SSMSI

Auteur: @de (Data Engineer)
"""

from .elections import download_elections
from .securite import download_securite

__all__ = [
    "download_elections",
    "download_securite",
]
