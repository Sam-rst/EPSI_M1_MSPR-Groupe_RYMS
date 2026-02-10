"""
Utilitaires de parsing pour la transformation de données.

Ce module contient les fonctions génériques de parsing et conversion
de formats spécifiques (nombres français, dates, etc.).

Fonctionnalités:
    - Conversion de nombres au format français (virgule décimale)
    - Gestion des formats CSV français

Auteur: @de (Data Engineer)
"""


def parse_french_number(value: str) -> int:
    """
    Convertit un nombre au format français (virgule décimale) en entier.

    Les fichiers électoraux utilisent le format français avec des virgules
    comme séparateurs décimaux (ex: "1.234,56" au lieu de "1,234.56").

    Args:
        value: Nombre au format string français (ex: "1234,56")

    Returns:
        Valeur convertie en entier

    Example:
        >>> parse_french_number("1234,56")
        1234
        >>> parse_french_number("0,26")
        0
        >>> parse_french_number("147632,0")
        147632

    Note:
        Cette fonction est nécessaire car pandas ne gère pas correctement
        les virgules décimales françaises dans certains fichiers CSV.
    """
    return int(float(value.replace(',', '.')))
