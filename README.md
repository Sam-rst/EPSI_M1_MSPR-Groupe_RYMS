# Electio-Analytics - POC Predictions Electorales

**Projet MSPR - M1 EPSI**
**Groupe RYMS**

---

## Contexte

Preuve de Concept (POC) pour la startup "Electio-Analytics" : outil de prediction des tendances electorales a moyen terme (1-3 ans) en croisant des donnees historiques avec des indicateurs socio-economiques.

**Perimetre :**
- **Zone :** Bordeaux (Gironde - 33)
- **Elections :** Presidentielles 2017 & 2022 (1er et 2nd tours)
- **Prediction :** Presidentielles 2027
- **Indicateurs :** Criminalite (SSMSI)

---

## Quick Start

### Prerequis

- **Docker Desktop** installe et demarre
- **UV** (gestionnaire de paquets Python) : `pip install uv`

### Installation

```bash
# 1. Cloner le repository
git clone <repository-url>
cd EPSI_M1_MSPR-Groupe_RYMS

# 2. Installer les dependances
uv sync --all-extras

# 3. Configurer l'environnement
cp .env.example .env
# Editer .env avec votre mot de passe PostgreSQL

# 4. Demarrer PostgreSQL
docker compose up -d

# 5. Creer le schema (17 tables v3.0)
uv run alembic -c src/database/alembic.ini upgrade head

# 6. Lancer le pipeline ETL complet
uv run python -m src.etl.main
```

**Resultat : 17 262 lignes chargees (~130s)**

**Documentation detaillee :**
- [Setup UV](docs/04-setup-installation/SETUP_UV.md)
- [Setup Base de donnees](docs/04-setup-installation/SETUP_DATABASE.md)

---

## Structure du Projet

```
EPSI_M1_MSPR-Groupe_RYMS/
├── data/
│   ├── raw/                          # Donnees brutes (~300 MB)
│   │   ├── geographie/              # JSON geo.api.gouv.fr
│   │   ├── elections/               # JSON + Parquet data.gouv.fr
│   │   └── securite/                # CSV SSMSI
│   └── processed/                   # Donnees transformees
│       ├── geographie/              # 1 region, 1 dept, 534 communes
│       ├── elections/               # 2 146 participations, 14 484 candidats
│       └── indicateurs/             # 45 indicateurs securite
│
├── docs/                            # Documentation complete
│   ├── 01-project-management/      # ROADMAP, planning
│   ├── 02-architecture/            # MCD, MLD, ARCHITECTURE, ADRs
│   ├── 03-data-sources/            # Sources de donnees
│   ├── 04-setup-installation/      # Guides d'installation
│   └── 05-reports/                 # Rapports et analyses
│
├── src/
│   ├── etl/                         # Pipeline ETL v3.0
│   │   ├── extract/                # Extraction (API → raw)
│   │   ├── transform/              # Transformation (raw → CSV)
│   │   ├── load/                   # Chargement (CSV → PostgreSQL)
│   │   └── main.py                 # Orchestrateur
│   └── database/                    # Schema v3.0
│       ├── models/                  # 17 modeles ORM SQLAlchemy
│       ├── migrations/              # Alembic (4 migrations)
│       └── config.py               # Connexion PostgreSQL
│
├── notebooks/                       # Jupyter notebooks
├── docker-compose.yml               # PostgreSQL 15 + PostGIS
├── pyproject.toml                   # Configuration UV + dependances
└── README.md                        # CE FICHIER
```

---

## Stack Technique

- **Python :** 3.11+
- **Gestionnaire :** UV
- **Data :** Pandas, NumPy, PyArrow
- **Database :** PostgreSQL 15 + PostGIS (Docker)
- **ORM :** SQLAlchemy 2.0 + Alembic
- **ML :** Scikit-Learn, XGBoost
- **Viz :** Matplotlib, Seaborn, Plotly, Folium

---

## Pipeline ETL v3.0

### Commande unique

```bash
uv run python -m src.etl.main
```

### Etapes individuelles

```bash
# 1. Extraction (API → data/raw/)
uv run python -m src.etl.extract.main

# 2. Transformation (data/raw/ → data/processed/)
uv run python -m src.etl.transform.main

# 3. Chargement (data/processed/ → PostgreSQL)
uv run python -m src.etl.load.main
```

### Sources de donnees

| Source | API | Donnees |
|--------|-----|---------|
| **Geographie** | geo.api.gouv.fr | Regions, departements, communes |
| **Elections** | tabular-api.data.gouv.fr + Parquet | Participation + candidats par bureau |
| **Securite** | data.gouv.fr (SSMSI) | Delinquance Bordeaux 2016-2024 |

**Documentation ETL :** [src/etl/README.md](src/etl/README.md)

---

## Avancement (14h/25h - 56%)

| Phase | Statut | Duree |
|-------|--------|-------|
| Phase 1 : Cadrage | TERMINEE | 1h |
| Phase 2 : Architecture | TERMINEE | 5h |
| Phase 3 : Data Engineering | TERMINEE | 8h |
| Phase 4 : Data Science | PROCHAINE | 6h |
| Phase 5 : Visualisation | EN ATTENTE | 4h |
| Phase 6 : Revue Qualite | EN ATTENTE | 1h |

---

## Documentation

**Index complet :** [docs/README.md](docs/README.md)

**Documents principaux :**
- [ROADMAP](docs/01-project-management/ROADMAP.md) - Planning 25h
- [ARCHITECTURE](docs/02-architecture/ARCHITECTURE.md) - Pipeline ETL v3.0
- [MCD](docs/02-architecture/database/01-mcd.md) - Modele conceptuel (17 entites)
- [MLD](docs/02-architecture/database/02-mld.md) - Schema relationnel + SQL
- [Dictionnaire de donnees](docs/02-architecture/database/03-dictionnaire-donnees.md)
- [Sources de donnees](docs/03-data-sources/SOURCES_DONNEES.md)

**ADRs :**
- [ADR-001](docs/02-architecture/adr/ADR-001-choix-bdd.md) - Choix PostgreSQL
- [ADR-002](docs/02-architecture/adr/ADR-002-choix-algo-ml.md) - Choix Random Forest
- [ADR-003](docs/02-architecture/adr/ADR-003-architecture-modulaire-etl.md) - Architecture ETL modulaire
- [ADR-004](docs/02-architecture/adr/ADR-004-enrichissement-schema-bd.md) - Schema v3.0

---

## Support

Consulter l'[index de la documentation](docs/README.md) ou contacter l'equipe projet.
