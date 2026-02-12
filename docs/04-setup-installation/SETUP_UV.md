# Setup du Projet avec UV

**Date :** 2026-02-09
**Projet :** Electio-Analytics POC

---

## Qu'est-ce que UV ?

[UV](https://github.com/astral-sh/uv) est un gestionnaire de paquets Python ultra-rapide développé par Astral (créateurs de Ruff).

**Avantages :**
- ⚡ **10-100x plus rapide** que pip/poetry
- 🔒 Résolution de dépendances déterministe (`uv.lock`)
- 🐍 Gestion automatique des versions Python
- 📦 Compatible avec `pyproject.toml` (standard Python moderne)
- 🚀 Pas besoin de virtualenv séparé (géré automatiquement)

---

## Installation de UV

### Windows

```powershell
# Via PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Ou via pip (si Python déjà installé)
pip install uv
```

### macOS / Linux

```bash
# Via curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via Homebrew (macOS)
brew install uv

# Ou via pip
pip install uv
```

### Vérification Installation

```bash
uv --version
# Attendu : uv 0.x.x (ou version plus récente)
```

---

## Initialisation du Projet

### 1. Cloner le Repository (si pas déjà fait)

```bash
cd C:\Users\samue\Desktop\Ecoles\EPSI\M1\MSPR
git clone <repository-url> EPSI_M1_MSPR-Groupe_RYMS
cd EPSI_M1_MSPR-Groupe_RYMS
```

### 2. Synchroniser les Dépendances avec UV

```bash
# Créer un environnement virtuel et installer toutes les dépendances
uv sync

# Cela va :
# - Lire pyproject.toml
# - Créer un virtualenv dans .venv/
# - Installer toutes les dépendances
# - Générer uv.lock (fichier de lockage)
```

**Sortie attendue :**
```
Resolved 45 packages in 1.2s
Installed 45 packages in 2.5s
  + numpy==1.26.3
  + pandas==2.2.0
  + scikit-learn==1.4.0
  + ...
✅ Environment synchronized
```

### 3. Installer les Dépendances Optionnelles (Notebooks, Viz, Dev)

```bash
# Installer TOUTES les dépendances optionnelles (recommandé pour le POC)
uv sync --all-extras

# OU installer seulement certains groupes
uv sync --extra notebooks    # Jupyter uniquement
uv sync --extra dev          # Outils de dev (pytest, black, ruff)
uv sync --extra viz          # Plotly pour visualisations interactives
```

### 4. Activer l'Environnement Virtuel

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

**Vérification :**
```bash
# Le prompt doit afficher (.venv)
(.venv) PS C:\...\EPSI_M1_MSPR-Groupe_RYMS>

# Vérifier Python
python --version
# Attendu : Python 3.11.x (ou version spécifiée dans .python-version)

# Vérifier packages
python -c "import pandas; print(pandas.__version__)"
# Attendu : 2.2.0 (ou version installée)
```

---

## Structure du Projet apres Setup

```
EPSI_M1_MSPR-Groupe_RYMS/
├── .venv/                     <- Environnement virtuel (UV)
├── .python-version            <- Version Python (3.11)
├── pyproject.toml             <- Configuration + dependances
├── uv.lock                    <- Lockfile deterministe
├── .env.example               <- Template variables d'environnement
├── docker-compose.yml         <- PostgreSQL 15 + PostGIS
│
├── data/
│   ├── raw/                   <- Donnees brutes (API)
│   └── processed/             <- Donnees transformees (CSV)
│
├── docs/
│   ├── 01-project-management/ <- ROADMAP, planning
│   ├── 02-architecture/       <- MCD, MLD, ADRs, ARCHITECTURE
│   ├── 03-data-sources/       <- Sources de donnees
│   └── 04-setup-installation/ <- Guides setup (CE FICHIER)
│
├── src/
│   ├── etl/                   <- Pipeline ETL v3.0
│   │   ├── extract/           <- Extraction API
│   │   ├── transform/         <- Transformation
│   │   ├── load/              <- Chargement PostgreSQL
│   │   └── main.py            <- Orchestrateur
│   └── database/              <- Schema v3.0 (17 tables)
│       ├── models/            <- Modeles ORM SQLAlchemy
│       ├── migrations/        <- Alembic
│       └── config.py          <- Connexion DB
│
├── notebooks/                 <- Jupyter notebooks
├── logs/                      <- Logs ETL
└── tests/                     <- Tests unitaires (pytest)
```

---

## Commandes UV Essentielles

### Gestion des Dépendances

```bash
# Ajouter une nouvelle dépendance
uv add pandas

# Ajouter une dépendance de développement
uv add --dev pytest

# Ajouter une dépendance optionnelle
uv add --optional notebooks jupyter

# Supprimer une dépendance
uv remove pandas

# Mettre à jour toutes les dépendances
uv sync --upgrade
```

### Executer des Scripts

```bash
# Pipeline ETL complet
uv run python -m src.etl.main

# Etapes individuelles
uv run python -m src.etl.extract.main
uv run python -m src.etl.transform.main
uv run python -m src.etl.load.main

# Lancer Jupyter (si notebooks installes)
uv run jupyter lab
```

### Vérifier l'Environnement

```bash
# Lister toutes les dépendances installées
uv pip list

# Afficher l'arbre des dépendances
uv pip tree

# Vérifier les dépendances manquantes
uv pip check
```

---

## Configuration Environnement (.env)

### 1. Copier le Template

```bash
cp .env.example .env
```

### 2. Éditer .env

```bash
# Windows
notepad .env

# macOS / Linux
nano .env
```

### 3. Remplir les Variables

```bash
# PostgreSQL (si utilisé)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=electio_analytics
POSTGRES_USER=admin
POSTGRES_PASSWORD=MotDePasseSecurise123!

# Chemins (laisser par défaut)
DATA_RAW_PATH=data/raw
DATA_PROCESSED_PATH=data/processed
LOGS_PATH=logs

# Filtres géographiques
DEPARTEMENT_CODE=33
COMMUNE_CODE=33063
COMMUNE_NAME=Bordeaux

# ML
RANDOM_STATE=42
TEST_SIZE=0.2
```

---

## Tester l'Installation

### Test 1 : Import des Librairies

```bash
uv run python -c "
import pandas as pd
import numpy as np
import sklearn
import xgboost
import geopandas
print('✅ Toutes les librairies sont installées correctement')
"
```

### Test 2 : Executer le Pipeline ETL

```bash
# Lancer le pipeline complet (Extract + Transform + Load)
uv run python -m src.etl.main
```

**Sortie attendue :**
```
PIPELINE ETL v3.0 - ELECTIO-ANALYTICS - GIRONDE
[OK] Extract terminee
[OK] Transform terminee
[OK] Load termine: 17262 lignes inserees
[OK] PIPELINE ETL v3.0 TERMINE AVEC SUCCES
```

### Test 3 : Lancer Jupyter (Optionnel)

```bash
# Si notebooks installés
uv run jupyter lab
```

---

## Workflow de Développement Recommandé

### 1. Démarrer une Session de Travail

```bash
cd C:\Users\samue\Desktop\Ecoles\EPSI\M1\MSPR\EPSI_M1_MSPR-Groupe_RYMS

# Activer l'environnement
.venv\Scripts\Activate.ps1   # Windows PowerShell

# Vérifier les dépendances à jour
uv sync
```

### 2. Travailler sur le Code

```bash
# Lancer le pipeline ETL
uv run python -m src.etl.main

# Lancer les tests
uv run pytest

# Formater le code
uv run black src/

# Linter le code
uv run ruff check src/
```

### 3. Ajouter une Nouvelle Dépendance

```bash
# Exemple : ajouter lightgbm pour tester un nouvel algo ML
uv add lightgbm

# UV va automatiquement :
# - Résoudre les dépendances
# - Mettre à jour pyproject.toml
# - Mettre à jour uv.lock
# - Installer le package
```

### 4. Commit des Changements

```bash
git add pyproject.toml uv.lock
git commit -m "Add lightgbm dependency"
git push
```

---

## Dépannage

### Erreur : "uv: command not found"

```bash
# UV n'est pas installé ou pas dans le PATH
# Réinstaller UV :
pip install uv

# Ou relancer le script d'installation
irm https://astral.sh/uv/install.ps1 | iex  # Windows
```

### Erreur : "Failed to resolve dependencies"

```bash
# Nettoyer le cache et réessayer
uv cache clean
uv sync --reinstall
```

### Erreur : "Python version not found"

```bash
# UV ne trouve pas Python 3.11
# Installer Python 3.11 manuellement ou changer .python-version

# Vérifier les versions Python disponibles
uv python list

# Utiliser une version spécifique
uv python install 3.11
```

### Lenteur au Premier Sync

```bash
# Le premier sync peut être long (téléchargement des packages)
# Les syncs suivants seront instantanés grâce au cache UV
```

---

## Différences UV vs Pip/Poetry

| Fonctionnalité | pip | poetry | uv |
|----------------|-----|--------|-----|
| **Vitesse installation** | 🐢 Lent | 🐢 Lent | ⚡ Très rapide (10-100x) |
| **Lockfile** | ❌ requirements.txt | ✅ poetry.lock | ✅ uv.lock |
| **Résolution deps** | ⚠️ Basique | ✅ Complète | ✅ Complète |
| **Gestion venv** | ❌ Manuel | ✅ Auto | ✅ Auto |
| **Standard Python** | ⚠️ requirements.txt | ⚠️ Propriétaire | ✅ pyproject.toml |
| **Commandes** | `pip install` | `poetry add` | `uv add` |

---

## Commandes Rapides de Référence

```bash
# Installation initiale
uv sync --all-extras

# Ajouter un package
uv add <package>

# Exécuter un script
uv run python <script.py>

# Lancer Jupyter
uv run jupyter lab

# Tests
uv run pytest

# Formater le code
uv run black src/

# Mettre à jour les dépendances
uv sync --upgrade

# Nettoyer le cache
uv cache clean
```

---

## Prochaines Etapes

Une fois l'environnement configure :

1. Verifier les dependances : `uv sync --all-extras`
2. Configurer `.env` avec les variables d'environnement
3. Demarrer PostgreSQL : `docker compose up -d`
4. Creer le schema : `uv run alembic -c src/database/alembic.ini upgrade head`
5. Lancer le pipeline ETL : `uv run python -m src.etl.main`

Voir [SETUP_DATABASE.md](SETUP_DATABASE.md) pour le detail de l'installation DB.

---

## Ressources

- [Documentation UV](https://github.com/astral-sh/uv)
- [Pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [Documentation Projet](docs/ROADMAP.md)
