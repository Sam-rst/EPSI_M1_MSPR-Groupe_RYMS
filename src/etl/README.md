# Module ETL - Electio-Analytics

## Vue d'ensemble

Module d'extraction, transformation et chargement (ETL) pour le projet Electio-Analytics.
Architecture modulaire pour le traitement des donnees electorales et socio-economiques.

**Auteur** : @de (Data Engineer)
**Version** : 3.0.0
**Date** : 2026-02-12

---

## Architecture

Le module ETL suit une **architecture Option 3** (separation par type de fonction).

```
src/etl/
├── extract/                    # Extraction des donnees brutes
│   ├── config/                # Configuration (URLs API, chemins)
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/                  # Logique metier par source
│   │   ├── __init__.py
│   │   ├── elections.py      # API tabulaire data.gouv.fr + Parquet
│   │   ├── geographie.py     # geo.api.gouv.fr
│   │   └── securite.py       # SSMSI CSV gzip
│   ├── utils/                 # Utilitaires generiques
│   │   ├── __init__.py
│   │   └── download.py       # download_file() avec progression
│   ├── __init__.py
│   └── main.py               # Orchestrateur extraction
│
├── transform/                  # Transformation des donnees
│   ├── config/                # Configuration (chemins, constantes)
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/                  # Logique metier par source
│   │   ├── __init__.py
│   │   ├── elections.py      # JSON + Parquet -> CSV normalises
│   │   ├── geographie.py     # JSON API -> CSV referentiels
│   │   └── securite.py       # CSV SSMSI -> indicateurs Bordeaux
│   ├── utils/                 # Utilitaires de parsing
│   │   ├── __init__.py
│   │   └── parsing.py        # parse_french_number()
│   ├── __init__.py
│   └── main.py               # Orchestrateur transformation
│
├── load/                       # Chargement en base de donnees
│   ├── config/                # Configuration (chemins CSV, batch)
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/                  # Logique metier par domaine
│   │   ├── __init__.py
│   │   ├── geographie.py     # Region, Departement, Commune
│   │   ├── candidats.py      # TypeElection, Election, Candidat, Parti
│   │   ├── elections.py      # ElectionTerritoire, ResultatParticipation, ResultatCandidat
│   │   ├── indicateurs.py    # Indicateur (batch 1000 rows)
│   │   └── type_indicateur.py # TypeIndicateur
│   ├── utils/                 # Validations
│   │   ├── __init__.py
│   │   └── validators.py     # Validation CSV
│   ├── __init__.py
│   └── main.py               # Orchestrateur chargement
│
├── __init__.py
├── main.py                     # Orchestrateur ETL global (E -> T -> L)
└── README.md                   # Cette documentation
```

---

## Utilisation

### Pipeline complet (recommande)

```bash
# Extract -> Transform -> Load en une seule commande
python -m src.etl.main
```

### Etapes individuelles

```bash
# Extraction seule (telecharge depuis les APIs)
python -m src.etl.extract.main

# Transformation seule (nettoie et normalise)
python -m src.etl.transform.main

# Chargement seul (insere dans PostgreSQL)
python -m src.etl.load.main
```

### Pre-requis

```bash
# 1. PostgreSQL operationnel
docker compose up -d

# 2. Installer les dependances
pip install -e .

# 3. Variables d'environnement (.env)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=electio_analytics
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password
```

---

## Donnees traitees

### Sources de donnees

| Source | API | Format | Periode |
|--------|-----|--------|---------|
| Geographie | geo.api.gouv.fr | JSON | Actuel |
| Elections presidentielles | data.gouv.fr API tabulaire + Parquet | JSON + Parquet | 2017, 2022 |
| Securite (SSMSI) | data.gouv.fr | CSV gzip | 2016-2024 |

### Territoire

**Zone** : Gironde (departement 33) - ~535 communes
**Filtrage securite** : Bordeaux (33063)

### Fichiers produits

**Extraction** (`data/raw/`) :
```
geographie/
├── regions.json                         (~2 KB)
├── departement_33.json                  (~1 KB)
└── communes_33.json                     (~200 KB)

elections/
├── participation_2017_pres_t1.json      (JSON pagine)
├── participation_2017_pres_t2.json
├── participation_2022_pres_t1.json
├── participation_2022_pres_t2.json
├── candidats_agrege.parquet             (~151 MB)
└── nuances_politiques.csv

securite/
└── delinquance_france_2016_2024.csv     (~34 MB gzip)
```

**Transformation** (`data/processed/`) :
```
geographie/
├── regions.csv                          (1 ligne)
├── departements.csv                     (1 ligne)
└── communes.csv                         (~535 lignes)

elections/
├── participation_gironde.csv            (~2 140 lignes)
├── candidats_gironde.csv                (~14 484 lignes)
├── referentiel_candidats.csv            (~25 lignes)
├── referentiel_partis.csv               (~15 lignes)
└── nuances_politiques.csv

indicateurs/
└── delinquance_bordeaux.csv             (~45 lignes)
```

**Chargement** (PostgreSQL - 17 tables) :
```
Total : ~17 262 lignes
├── Geographie : 537 lignes (region + departement + communes)
├── Elections : ~16 675 lignes (candidats, partis, resultats)
├── Indicateurs : 50 lignes (types + valeurs)
└── Predictions : 0 (en attente Phase 4)
```

---

## API programmatique

### Import des fonctions

```python
# Pipeline complet
from src.etl.main import main as etl_main

# Extraction
from src.etl.extract import download_geographie, download_elections, download_securite
from src.etl.extract.utils import download_file

# Transformation
from src.etl.transform import transform_geographie, transform_elections, transform_securite
from src.etl.transform.utils import parse_french_number

# Chargement
from src.etl.load import main as load_main
```

### Exemples

**Pipeline complet :**
```python
from src.etl.main import main as etl_main
etl_main()
```

**Extraction specifique :**
```python
from src.etl.extract.core import download_elections
success = download_elections()
```

**Transformation specifique :**
```python
from src.etl.transform.core import transform_securite
success = transform_securite()
```

---

## Ajouter une nouvelle source de donnees

### 1. Extraction (`src/etl/extract/`)

Creer `core/nouvelle_source.py` :
```python
"""Module de telechargement de la nouvelle source."""
import logging
from ..config import DATA_RAW_NOUVELLE_SOURCE, NOUVELLE_SOURCE_URL
from ..utils import download_file

logger = logging.getLogger(__name__)

def download_nouvelle_source() -> bool:
    """Telecharge les donnees de la nouvelle source."""
    output_path = DATA_RAW_NOUVELLE_SOURCE / "fichier.csv"
    return download_file(NOUVELLE_SOURCE_URL, output_path, "Nouvelle source")
```

Mettre a jour : `config/settings.py`, `core/__init__.py`, `main.py`

### 2. Transformation (`src/etl/transform/`)

Creer `core/nouvelle_source.py` avec la logique de nettoyage.
Mettre a jour : `config/settings.py`, `core/__init__.py`, `main.py`

### 3. Chargement (`src/etl/load/`)

Creer `core/nouvelle_source.py` avec la logique d'insertion.
Respecter : check-before-insert, batch loading, IntegrityError + rollback.

---

## Gestion des erreurs

### Comportement

- **Fichiers existants** : Detectes et non retelecharges
- **Erreurs reseau** : Loggees, fichier partiel nettoye
- **Donnees manquantes** : Warning logue, continue avec les autres fichiers
- **IntegrityError** : Rollback de la transaction, re-raise
- **Interruption (Ctrl+C)** : Exit code 130

### Codes de sortie

| Code | Signification |
|------|---------------|
| 0 | Succes complet |
| 1 | Echec partiel ou total |
| 130 | Interruption utilisateur |

---

## Securite

- **SQL injection** : Requetes parametrees avec `sqlalchemy.text()` + whitelist de tables
- **Mot de passe BDD** : Variable d'environnement `POSTGRES_PASSWORD`
- **Singleton engine** : Evite les fuites de connexion
- **Transaction safety** : `IntegrityError` + `session.rollback()` sur tous les loaders

---

## Changelog

### Version 3.0.0 (2026-02-12)
- Module Load complet (5 loaders, batch loading, validation CSV)
- Schema v3.0 : 17 tables, systeme polymorphe
- Sources : geo.api.gouv.fr, API tabulaire data.gouv.fr, Parquet candidats
- Corrections review : SQL injection, singleton, transactions, vectorisation
- 17,262 lignes chargees en PostgreSQL

### Version 2.0.0 (2026-02-11)
- Architecture Option 3 complete (extract + transform)
- Module Load initial + encodage UTF-8

### Version 1.0.0 (2026-02-10)
- Refactorisation en architecture Option 3
- Separation extract/ et transform/ en packages modulaires
- Documentation complete

---

**Projet** : Electio-Analytics POC
**Architecture** : Voir `docs/02-architecture/ARCHITECTURE.md`
