"""
Module d'extraction des données pour Electio-Analytics.

Contient les scripts de téléchargement automatisés via API data.gouv.fr :
- Élections présidentielles 2017 & 2022 (4 fichiers, 1er et 2nd tours)
- Données de sécurité (SSMSI)
- Données d'emploi (INSEE)

Architecture:
    api_datagouv.py → Client API REST générique
    config.py → URLs et chemins centralisés
    download_*.py → Scripts de téléchargement spécialisés
"""

from .download_elections import download_all_elections_api
from .download_emploi import download_emploi
from .download_securite import download_securite

__all__ = [
    "download_all_elections_api",
    "download_securite",
    "download_emploi",
]
