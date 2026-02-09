# Module Extract - Téléchargement des Données

## Description

Scripts de téléchargement automatisé des données sources pour Electio-Analytics :
- **Élections** : Présidentielles 2017 & 2022 (1er et 2nd tours)
- **Sécurité** : Base SSMSI (2016-2024, commune de Bordeaux)
- **Emploi** : Données INSEE (IRIS + Commune)

## Structure

```
src/etl/extract/
├── __init__.py              # Exports du module
├── config.py                # Configuration centralisée (URLs, chemins)
├── download_elections.py    # Téléchargement élections (4 fichiers CSV)
├── download_securite.py     # Téléchargement sécurité (filtré Bordeaux)
├── download_emploi.py       # Instructions téléchargement emploi (manuel)
└── README.md                # Ce fichier
```

## Usage

### Télécharger TOUTES les données électorales

```bash
# Via CLI (défini dans pyproject.toml)
uv run electio-download

# Ou directement
python -m src.etl.extract.download_elections
```

**Résultat :** 4 fichiers CSV dans `data/raw/elections/`

### Télécharger les données de sécurité

```bash
python -m src.etl.extract.download_securite
```

**Résultat :** 1 fichier CSV filtré dans `data/raw/securite/`

### Télécharger les données d'emploi

```bash
python -m src.etl.extract.download_emploi
```

**Résultat :** Instructions pour téléchargement manuel INSEE

## Fichiers Téléchargés

### Élections (4 fichiers)

```
data/raw/elections/
├── presidentielles_2017_tour1_bureaux_vote.csv  (23 avril 2017)
├── presidentielles_2017_tour2_bureaux_vote.csv  (7 mai 2017)
├── presidentielles_2022_tour1_bureaux_vote.csv  (10 avril 2022)
└── presidentielles_2022_tour2_bureaux_vote.csv  (24 avril 2022)
```

### Sécurité (1 fichier)

```
data/raw/securite/
└── delinquance_bordeaux_2016_2024.csv
```

### Emploi (2 fichiers - manuel)

```
data/raw/emploi/
├── demandeurs_emploi_iris_2022.csv
└── population_active_bordeaux_2017_2024.csv
```

## Configuration

Toutes les URLs et chemins sont centralisés dans `config.py` :

```python
from src.etl.extract.config import (
    ELECTIONS_2017_T1_URL,
    ELECTIONS_2022_T1_URL,
    DATA_RAW_ELECTIONS,
    CODE_COMMUNE,  # "33063" (Bordeaux)
)
```

## Gestion des Erreurs

Les scripts gèrent :
- ✅ Fichiers déjà téléchargés (skip automatique)
- ✅ Barres de progression (tqdm)
- ✅ Timeouts HTTP (60-120s)
- ✅ Codes de retour (0 = succès, 1 = échec)
- ✅ Logging structuré

## Dépendances

```toml
dependencies = [
    "requests>=2.31.0",   # HTTP
    "pandas>=2.0.0",      # Manipulation CSV
    "tqdm>=4.66.0",       # Barres de progression
]
```

## Validation Post-Téléchargement

Vérifier que les fichiers sont présents :

```bash
# Linux/Mac
ls -lh data/raw/elections/
ls -lh data/raw/securite/
ls -lh data/raw/emploi/

# Windows
dir data\raw\elections\
dir data\raw\securite\
dir data\raw\emploi\
```

**Volumétrie attendue :**
- Élections : ~50-100 MB par fichier
- Sécurité : ~5-10 MB (après filtrage Bordeaux)
- Emploi : ~1-5 MB

## Prochaines Étapes

Après téléchargement, lancer les scripts de transformation :

```bash
# Phase ETL : Transform
python -m src.etl.transform.clean_elections
python -m src.etl.transform.harmonize_geo

# Phase ETL : Load
python -m src.etl.load.load_to_db
```

## Licence & Conformité

**Toutes les données sont sous Licence Ouverte v2.0 (Etalab)**
- ✅ Usage libre (y compris commercial)
- ⚠️ Attribution obligatoire : Mentionner les sources

**Conformité RGPD :**
- ✅ Données agrégées uniquement (bureaux de vote, communes)
- ✅ Aucune donnée personnelle

## Références

- [data.gouv.fr - Élections](https://www.data.gouv.fr/)
- [SSMSI - Sécurité](https://www.interieur.gouv.fr/Interstats)
- [INSEE - Emploi](https://www.insee.fr/)
- [DARES - Open Data](https://dares.travail-emploi.gouv.fr/dossier/open-data)
