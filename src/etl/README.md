# Module ETL - Electio-Analytics

## 📋 Vue d'ensemble

Module d'extraction, transformation et chargement (ETL) pour le projet Electio-Analytics.
Architecture modulaire enterprise-grade pour le traitement des données électorales et socio-économiques.

**Auteur** : @de (Data Engineer)
**Version** : 1.0.0
**Date** : 2026-02-10

---

## 🏗️ Architecture

Le module ETL suit une **architecture Option 3** (séparation par type de fonction) pour une scalabilité et maintenabilité maximales.

```
src/etl/
├── extract/                    # Extraction des données brutes
│   ├── config/                # Configuration (URLs, chemins)
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/                  # Logique métier par source
│   │   ├── __init__.py
│   │   ├── elections.py      # Téléchargement élections
│   │   └── securite.py       # Téléchargement sécurité
│   ├── utils/                 # Utilitaires génériques
│   │   ├── __init__.py
│   │   └── download.py       # Fonction download_file()
│   ├── __init__.py
│   └── main.py               # Orchestrateur extraction
│
├── transform/                  # Transformation des données
│   ├── config/                # Configuration (chemins, constantes)
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/                  # Logique métier par source
│   │   ├── __init__.py
│   │   ├── elections.py      # Transformation élections
│   │   └── securite.py       # Transformation sécurité
│   ├── utils/                 # Utilitaires de parsing
│   │   ├── __init__.py
│   │   └── parsing.py        # parse_french_number()
│   ├── __init__.py
│   └── main.py               # Orchestrateur transformation
│
└── README.md                   # Cette documentation
```

### Principes architecturaux

1. **Séparation des responsabilités** : Chaque package a un rôle unique (config, core, utils)
2. **Scalabilité** : Ajout facile de nouvelles sources de données
3. **Testabilité** : Chaque module peut être testé indépendamment
4. **Réutilisabilité** : Utilitaires génériques dans `utils/`
5. **Maintenabilité** : Code organisé et documenté

---

## 🚀 Utilisation

### Pipeline complet (Extract + Transform)

```bash
# 1. Extraire les données brutes
python -m src.etl.extract.main

# 2. Transformer les données
python -m src.etl.transform.main

# OU en une seule commande
python -m src.etl.extract.main && python -m src.etl.transform.main
```

### Extraction seule

```bash
python -m src.etl.extract.main
```

**Données téléchargées** :
- Élections présidentielles 2017 & 2022 (4 fichiers CSV, ~94 MB)
- Données SSMSI délinquance France (1 fichier gzip, ~34 MB)

**Destination** : `data/raw/{elections,securite}/`

### Transformation seule

```bash
python -m src.etl.transform.main
```

**Données transformées** :
- Élections : 4 fichiers → 1 fichier consolidé Bordeaux (4 lignes)
- Sécurité : France → Bordeaux uniquement (~135 lignes)

**Destination** : `data/processed/{elections,indicateurs}/`

---

## 📦 Données traitées

### Sources de données

| Source | Type | Période | Granularité | Format |
|--------|------|---------|-------------|--------|
| Élections présidentielles | Résultats de votes | 2017, 2022 (T1 & T2) | Bureau de vote | CSV |
| Sécurité (SSMSI) | Délinquance enregistrée | 2016-2024 | Communale | CSV gzip |

### Territoire

**Zone** : Bordeaux (Gironde - 33)
**Code INSEE** : 33063

### Fichiers produits

**Extraction** (`data/raw/`) :
```
elections/
├── presidentielles_2017_tour1_bureaux_vote.csv   (~23 MB)
├── presidentielles_2017_tour2_bureaux_vote.csv   (~23 MB)
├── presidentielles_2022_tour1_bureaux_vote.csv   (~24 MB)
└── presidentielles_2022_tour2_bureaux_vote.csv   (~24 MB)

securite/
└── delinquance_france_2016_2024.csv              (~34 MB gzip)
```

**Transformation** (`data/processed/`) :
```
elections/
└── resultats_elections_bordeaux.csv              (4 lignes)

indicateurs/
└── delinquance_bordeaux.csv                      (~135 lignes)
```

---

## 🔌 API programmatique

### Import des fonctions

```python
# Extraction
from src.etl.extract import main as extract_main
from src.etl.extract import download_elections, download_securite
from src.etl.extract.utils import download_file

# Transformation
from src.etl.transform import main as transform_main
from src.etl.transform import transform_elections, transform_securite
from src.etl.transform.utils import parse_french_number
```

### Exemples d'utilisation

**Pipeline complet** :
```python
from src.etl.extract import main as extract_main
from src.etl.transform import main as transform_main

# Extraire puis transformer
if extract_main():
    transform_main()
```

**Téléchargement spécifique** :
```python
from src.etl.extract.core import download_elections

# Télécharger uniquement les élections
success = download_elections()
```

**Transformation spécifique** :
```python
from src.etl.transform.core import transform_securite

# Transformer uniquement la sécurité
success = transform_securite()
```

**Utilitaire de parsing** :
```python
from src.etl.transform.utils import parse_french_number

# Convertir nombre français
valeur = parse_french_number("1234,56")  # → 1234
```

**Téléchargement générique** :
```python
from pathlib import Path
from src.etl.extract.utils import download_file

# Télécharger n'importe quel fichier
url = "https://example.com/data.csv"
path = Path("data/custom/file.csv")
success = download_file(url, path, "Description")
```

---

## ➕ Ajouter une nouvelle source de données

### Exemple : Ajouter les données d'emploi

#### 1. Extraction (`src/etl/extract/`)

**Créer `core/emploi.py`** :
```python
"""Module de téléchargement des données d'emploi."""

import logging
from pathlib import Path

from ..config import DATA_RAW_EMPLOI, EMPLOI_URL
from ..utils import download_file

logger = logging.getLogger(__name__)

def download_emploi() -> bool:
    """Télécharge les données d'emploi INSEE."""
    logger.info("=" * 80)
    logger.info("TÉLÉCHARGEMENT DONNÉES EMPLOI")
    logger.info("=" * 80)

    output_path = DATA_RAW_EMPLOI / "emploi_bordeaux.csv"
    return download_file(EMPLOI_URL, output_path, "Emploi Bordeaux")
```

**Mettre à jour `config/settings.py`** :
```python
# Ajouter
DATA_RAW_EMPLOI: Path = DATA_RAW / "emploi"
EMPLOI_URL: str = "https://..."
```

**Mettre à jour `core/__init__.py`** :
```python
from .emploi import download_emploi

__all__ = ["download_elections", "download_securite", "download_emploi"]
```

**Mettre à jour `main.py`** :
```python
from .core import download_elections, download_securite, download_emploi

# Dans main()
emploi_ok = download_emploi()
```

#### 2. Transformation (`src/etl/transform/`)

**Créer `core/emploi.py`** :
```python
"""Module de transformation des données d'emploi."""

import logging
import pandas as pd
from ..config import DATA_RAW_EMPLOI, DATA_PROCESSED_EMPLOI

logger = logging.getLogger(__name__)

def transform_emploi() -> bool:
    """Transforme les données d'emploi pour Bordeaux."""
    logger.info("TRANSFORMATION DONNÉES EMPLOI")

    # Logique de transformation
    df = pd.read_csv(DATA_RAW_EMPLOI / "emploi_bordeaux.csv")
    # ... filtrage, nettoyage ...
    df.to_csv(DATA_PROCESSED_EMPLOI / "emploi_clean.csv", index=False)

    return True
```

**Suivre les mêmes étapes** que pour l'extraction (config, __init__, main).

---

## 🧪 Tests

### Tests manuels

```bash
# Tester extraction
python -m src.etl.extract.main

# Tester transformation
python -m src.etl.transform.main

# Tester imports
python -c "from src.etl.extract import main; from src.etl.transform import main as tm"
```

### Tests unitaires (à implémenter)

```python
# tests/test_extract_elections.py
from src.etl.extract.core.elections import download_elections

def test_download_elections():
    assert download_elections() == True

# tests/test_transform_parsing.py
from src.etl.transform.utils.parsing import parse_french_number

def test_parse_french_number():
    assert parse_french_number("1234,56") == 1234
    assert parse_french_number("0,26") == 0
```

---

## 🔧 Configuration

### Variables d'environnement (optionnel)

Actuellement, toutes les configurations sont dans `config/settings.py`.
Pour externaliser :

```python
# Exemple dans config/settings.py
import os

TIMEOUT_SECONDS = int(os.getenv("ETL_TIMEOUT", "300"))
```

### Chemins personnalisés

Modifier `config/settings.py` :
```python
# Utiliser un dossier de données personnalisé
DATA_RAW = Path("/custom/path/data/raw")
```

---

## 📊 Logging

Le module utilise le module `logging` standard de Python.

**Configuration actuelle** :
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
```

**Personnaliser** :
```python
# Pour plus de détails
logging.basicConfig(level=logging.DEBUG)

# Pour sauvegarder dans un fichier
logging.basicConfig(
    filename='etl.log',
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
```

---

## ⚠️ Gestion des erreurs

### Comportement par défaut

- **Fichiers existants** : Détectés et non retéléchargés
- **Erreurs réseau** : Loggées, téléchargement échoue gracieusement
- **Données manquantes** : Warning logué, continue avec les autres fichiers
- **Interruption (Ctrl+C)** : Exit code 130

### Codes de sortie

| Code | Signification |
|------|---------------|
| 0 | Succès complet |
| 1 | Échec partiel ou total |
| 130 | Interruption utilisateur (Ctrl+C) |

---

## 🚦 Bonnes pratiques

1. **Toujours lire la config** avant de modifier les URLs
2. **Utiliser les utilitaires** plutôt que dupliquer du code
3. **Logger les opérations** pour le débogage
4. **Gérer les erreurs** gracieusement
5. **Documenter** les nouvelles sources de données

---

## 📚 Ressources

- **Sources de données** : [data.gouv.fr](https://www.data.gouv.fr)
- **Architecture** : Voir `docs/architecture/ARCHITECTURE.md`
- **Décisions** : Voir `docs/architecture/adr/ADR-003-architecture-modulaire.md`
- **Roadmap** : Voir `docs/gestion-projet/ROADMAP.md`

---

## 🤝 Contribution

Pour contribuer au module ETL :

1. **Respecter l'architecture** Option 3 (config/, core/, utils/, main.py)
2. **Ajouter des type hints** sur toutes les fonctions
3. **Documenter** avec des docstrings Google style
4. **Tester** les modifications avant commit
5. **Mettre à jour cette documentation** si nécessaire

---

## 📝 Changelog

### Version 1.0.0 (2026-02-10)
- ✅ Refactorisation complète en architecture Option 3
- ✅ Séparation extract/ et transform/ en packages modulaires
- ✅ Extraction de utils génériques (download, parsing)
- ✅ Documentation complète
- ✅ Type hints sur toutes les fonctions
- ✅ Gestion robuste des erreurs

---

**Auteur** : @de (Data Engineer)
**Projet** : Electio-Analytics POC
**Contact** : Voir CLAUDE.md
