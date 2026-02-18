<div align="center">

# MSPR : Electio-Analytics

**Outil de prediction des tendances electorales par croisement de donnees historiques et d'indicateurs socio-economiques**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![UV](https://img.shields.io/badge/UV-Package_Manager-DE5FE9?logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Sam-rst/EPSI_M1_MSPR-Groupe_RYMS)

</div>

---

## Presentation

Electio-Analytics est une Preuve de Concept (POC) qui vise a predire les tendances electorales a moyen terme (1-3 ans) en croisant des donnees de votes historiques avec des indicateurs socio-economiques tels que la criminalite.

Le projet s'appuie sur un pipeline ETL complet, une base de donnees relationnelle normalisee et des modeles de Machine Learning pour produire des predictions exploitables.

| | Details |
|---|---|
| **Zone geographique** | Bordeaux (Gironde - 33) |
| **Elections analysees** | Presidentielles 2017 & 2022 (1er et 2nd tours) |
| **Prediction cible** | Presidentielles 2027 |
| **Indicateurs** | Criminalite (SSMSI - 2016-2024) |

---

## Demarrage rapide

### Prerequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installe et demarre
- [UV](https://docs.astral.sh/uv/) (gestionnaire de paquets Python) : `pip install uv`

### Installation

```bash
# Cloner le repository
git clone https://github.com/Sam-rst/EPSI_M1_MSPR-Groupe_RYMS.git
cd EPSI_M1_MSPR-Groupe_RYMS

# Installer les dependances
uv sync --all-extras

# Configurer l'environnement
cp .env.example .env
# Editer .env avec vos identifiants PostgreSQL

# Demarrer PostgreSQL
docker compose up -d

# Creer le schema de base de donnees
uv run alembic -c src/database/alembic.ini upgrade head

# Lancer le pipeline ETL complet
uv run python -m src.etl.main
```

> Guides detailles : [Setup UV](docs/04-setup-installation/SETUP_UV.md) | [Setup Base de donnees](docs/04-setup-installation/SETUP_DATABASE.md)

---

## Architecture

```
electio-analytics/
│
├── data/
│   ├── raw/                     # Donnees brutes (API, Parquet, CSV)
│   └── processed/               # Donnees transformees (CSV normalises)
│
├── src/
│   ├── etl/                     # Pipeline ETL
│   │   ├── extract/             # Extraction depuis les APIs
│   │   ├── transform/           # Nettoyage et transformation
│   │   ├── load/                # Chargement en base
│   │   └── main.py              # Orchestrateur
│   └── database/                # Schema et migrations
│       ├── models/              # 17 modeles ORM (SQLAlchemy)
│       └── migrations/          # Versioning Alembic
│
├── notebooks/                   # Exploration et modelisation ML
├── docs/                        # Documentation technique
└── docker-compose.yml           # Infrastructure PostgreSQL + PostGIS
```

---

## Stack technique

| Categorie | Technologies |
|---|---|
| **Langage** | Python 3.11+ |
| **Gestion des dependances** | UV |
| **Traitement de donnees** | Pandas, NumPy, PyArrow |
| **Base de donnees** | PostgreSQL 15, PostGIS |
| **ORM & Migrations** | SQLAlchemy 2.0, Alembic |
| **Machine Learning** | Scikit-Learn, XGBoost |
| **Visualisation** | Matplotlib, Seaborn, Plotly, Folium |
| **Infrastructure** | Docker Compose |

---

## Pipeline ETL

Le pipeline s'execute en une seule commande ou etape par etape :

```bash
# Execution complete
uv run python -m src.etl.main
```

```bash
# Ou etape par etape
uv run python -m src.etl.extract.main      # Extraction   (APIs → data/raw/)
uv run python -m src.etl.transform.main     # Transformation (raw → data/processed/)
uv run python -m src.etl.load.main          # Chargement     (processed → PostgreSQL)
```

### Sources de donnees

| Source | Origine | Description |
|---|---|---|
| **Geographie** | geo.api.gouv.fr | Regions, departements, communes |
| **Elections** | data.gouv.fr (API tabulaire + Parquet) | Participation et resultats par bureau de vote |
| **Securite** | data.gouv.fr (SSMSI) | Indicateurs de delinquance - Bordeaux |

> Documentation complete du pipeline : [src/etl/README.md](src/etl/README.md)

---

## Documentation

L'ensemble de la documentation technique est disponible dans le repertoire [`docs/`](docs/).

| Document | Description |
|---|---|
| [Architecture](docs/02-architecture/ARCHITECTURE.md) | Vue d'ensemble du pipeline et des composants |
| [MCD](docs/02-architecture/database/01-mcd.md) | Modele Conceptuel de Donnees (17 entites) |
| [MLD](docs/02-architecture/database/02-mld.md) | Schema relationnel et requetes SQL |
| [Dictionnaire de donnees](docs/02-architecture/database/03-dictionnaire-donnees.md) | Description de chaque attribut |
| [Sources de donnees](docs/01-project-management/SOURCES_DONNEES.md) | Referentiel des jeux de donnees utilises |
| [Roadmap](docs/01-project-management/ROADMAP.md) | Planning et phases du projet |

### Architecture Decision Records (ADR)

| ADR | Decision |
|---|---|
| [ADR-001](docs/02-architecture/adr/ADR-001-choix-bdd.md) | PostgreSQL comme SGBD principal |
| [ADR-002](docs/02-architecture/adr/ADR-002-choix-algo-ml.md) | Random Forest pour la prediction |
| [ADR-003](docs/02-architecture/adr/ADR-003-architecture-modulaire-etl.md) | Architecture ETL modulaire |
| [ADR-004](docs/02-architecture/adr/ADR-004-enrichissement-schema-bd.md) | Enrichissement du schema v3.0 |
| [ADR-005](docs/02-architecture/adr/ADR-005-choix-perimetre-geographique.md) | Perimetre geographique Bordeaux |

---

## Equipe

**Groupe RYMS** - Projet MSPR, M1 EPSI

| Membre |
|---|
| Samuel RESSIOT |
| Yassine ZOUITNI |
| Rudolph ATTISSO |
| Marc-Alex NEZOUT |
