# Electio-Analytics - POC Prédictions Électorales

**Projet MSPR - M1 EPSI**
**Groupe RYMS**

---

## 📋 Contexte

Preuve de Concept (POC) pour la startup "Electio-Analytics" : outil de prédiction des tendances électorales à moyen terme (1-3 ans) en croisant des données historiques avec des indicateurs socio-économiques.

**Périmètre :**
- **Zone :** Bordeaux (Gironde - 33)
- **Élections :** Présidentielles 2017 & 2022 (1er et 2nd tours)
- **Prédiction :** Présidentielles 2027
- **Indicateurs :** Chômage (INSEE) + Criminalité (SSMSI)

---

## 🚀 Quick Start

### Installation avec UV (Recommandé)

```bash
# 1. Installer UV
pip install uv

# 2. Synchroniser les dépendances
uv sync --all-extras

# 3. Activer l'environnement
.venv\Scripts\Activate.ps1   # Windows PowerShell
source .venv/bin/activate    # macOS/Linux

# 4. Configurer .env
cp .env.example .env
```

**Documentation complète :** [docs/04-setup-installation/SETUP_UV.md](docs/04-setup-installation/SETUP_UV.md)

---

## 📁 Structure du Projet

```
EPSI_M1_MSPR-Groupe_RYMS/
├── data/
│   ├── raw/                          # Données brutes (128 MB)
│   │   ├── elections/               # 4 fichiers présidentielles
│   │   └── securite/                # Délinquance SSMSI
│   └── processed/                   # Données nettoyées
│       ├── elections/               # Résultats Bordeaux (4 lignes)
│       └── indicateurs/             # Sécurité Bordeaux (135 lignes)
│
├── docs/                            # Documentation complète
│   ├── 01-project-management/      # ROADMAP, planning
│   ├── 02-architecture/            # MCD, ARCHITECTURE, ADRs
│   ├── 03-data-sources/            # Sources de données
│   ├── 04-setup-installation/      # Guides d'installation
│   └── 05-reports/                 # Rapports et analyses
│
├── src/
│   ├── etl/                         # Module ETL (Architecture Option 3)
│   │   ├── extract/                # Extraction (config/, core/, utils/, main.py)
│   │   ├── transform/              # Transformation (config/, core/, utils/, main.py)
│   │   └── README.md               # Documentation ETL complète
│   └── models/                      # Modèles ML
│
├── notebooks/                       # Jupyter notebooks
├── pyproject.toml                   # Configuration UV + dépendances
└── README.md                        # CE FICHIER
```

---

## 🛠️ Stack Technique

- **Python :** 3.11+
- **Gestionnaire :** UV (10-100x plus rapide que pip)
- **Data :** Pandas, NumPy
- **Database :** PostgreSQL + PostGIS
- **ML :** Scikit-Learn (Random Forest), XGBoost
- **Viz :** Matplotlib, Seaborn, Plotly, Folium

---

## 📊 Avancement (14h/25h - 56%)

| Phase | Statut | Durée |
|-------|--------|-------|
| Phase 1 : Cadrage | ✅ TERMINÉE | 1h |
| Phase 2 : Architecture | ✅ TERMINÉE | 5h |
| Phase 3 : Data Engineering | ✅ TERMINÉE | 8h |
| Phase 4 : Data Science | 🎯 PROCHAINE | 6h |
| Phase 5 : Visualisation | ⏸️ EN ATTENTE | 4h |
| Phase 6 : Revue Qualité | ⏸️ EN ATTENTE | 1h |

### ✨ Nouveauté Phase 3
- ✅ **Architecture modulaire** refactorisée (ADR-003)
- ✅ **18 modules Python** (~1500 lignes)
- ✅ **128 MB de données** téléchargées et transformées
- ✅ **Documentation complète** (src/etl/README.md)

---

## 🔄 Pipeline ETL (Architecture Modulaire)

### Extraction des données

```bash
# Télécharger toutes les données (élections + sécurité)
python -m src.etl.extract.main

# Résultat : 128 MB dans data/raw/
# - 4 fichiers élections (94 MB)
# - 1 fichier sécurité (34 MB gzip)
```

### Transformation des données

```bash
# Nettoyer et filtrer pour Bordeaux
python -m src.etl.transform.main

# Résultat : 2 fichiers dans data/processed/
# - elections/resultats_elections_bordeaux.csv (4 lignes)
# - indicateurs/delinquance_bordeaux.csv (135 lignes)
```

### Pipeline complet

```bash
# Extraction + Transformation en une commande
python -m src.etl.extract.main && python -m src.etl.transform.main
```

**Documentation détaillée :** [src/etl/README.md](src/etl/README.md)

---

## 📚 Documentation

**Index complet :** [docs/README.md](docs/README.md)

**Documents principaux :**
- [ROADMAP.md](docs/01-project-management/ROADMAP.md) - Planning 25h (Phase 3 terminée)
- [ARCHITECTURE.md](docs/02-architecture/ARCHITECTURE.md) - Pipeline ETL (v2.0)
- [MCD.md](docs/02-architecture/MCD.md) - Modèle de données
- [SOURCES_DONNEES.md](docs/03-data-sources/SOURCES_DONNEES.md) - URLs data.gouv.fr
- [SETUP_UV.md](docs/04-setup-installation/SETUP_UV.md) - Installation UV

**Architecture Decision Records (ADRs) :**
- [ADR-001](docs/02-architecture/adr/ADR-001-choix-bdd.md) - Choix PostgreSQL vs NoSQL
- [ADR-002](docs/02-architecture/adr/ADR-002-choix-algo-ml.md) - Choix Random Forest
- [ADR-003](docs/02-architecture/adr/ADR-003-architecture-modulaire-etl.md) - Architecture Option 3 ⭐ NOUVEAU

**Documentation technique :**
- [src/etl/README.md](src/etl/README.md) - Guide complet module ETL ⭐ NOUVEAU

---

## 📞 Support

Consulter l'[index de la documentation](docs/README.md) ou contacter l'équipe projet.
