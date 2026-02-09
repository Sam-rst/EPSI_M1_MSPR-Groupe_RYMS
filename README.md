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
├── data/raw/              # Données brutes (CSV)
├── data/processed/        # Données nettoyées
├── docs/                  # Documentation (MCD, ADRs, ROADMAP)
├── src/etl/               # Scripts ETL
├── src/models/            # Modèles ML
├── notebooks/             # Jupyter notebooks
├── pyproject.toml         # Configuration + dépendances
└── README.md              # CE FICHIER
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

## 📊 Avancement (6h/25h - 24%)

| Phase | Statut | Durée |
|-------|--------|-------|
| Phase 1 : Cadrage | ✅ TERMINÉE | 1h |
| Phase 2 : Architecture | ✅ TERMINÉE | 5h |
| Phase 3 : Data Engineering | ⏸️ EN ATTENTE | 8h |
| Phase 4 : Data Science | ⏸️ EN ATTENTE | 6h |
| Phase 5 : Visualisation | ⏸️ EN ATTENTE | 4h |
| Phase 6 : Revue Qualité | ⏸️ EN ATTENTE | 1h |

---

## 📚 Documentation

**Index complet :** [docs/README.md](docs/README.md)

**Documents principaux :**
- [ROADMAP.md](docs/01-project-management/ROADMAP.md) - Planning 25h
- [MCD.md](docs/02-architecture/MCD.md) - Base de données
- [ARCHITECTURE.md](docs/02-architecture/ARCHITECTURE.md) - Pipeline ETL
- [SOURCES_DONNEES.md](docs/03-data-sources/SOURCES_DONNEES.md) - URLs data.gouv.fr
- [SETUP_UV.md](docs/04-setup-installation/SETUP_UV.md) - Installation UV
- [ADR-001](docs/02-architecture/adr/ADR-001-choix-bdd.md) - PostgreSQL
- [ADR-002](docs/02-architecture/adr/ADR-002-choix-algo-ml.md) - Random Forest

---

## 📞 Support

Consulter l'[index de la documentation](docs/README.md) ou contacter l'équipe projet.
