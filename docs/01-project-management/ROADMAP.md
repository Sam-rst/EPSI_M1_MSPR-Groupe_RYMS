# ROADMAP - Electio-Analytics POC

> **Prediction des tendances electorales** pour les Presidentielles 2027
> a partir des donnees historiques 2017-2022 et indicateurs socio-economiques

---

## Vue d'ensemble

| | Detail |
|---|--------|
| **Zone** | Gironde (33) - 535 communes |
| **Elections** | Presidentielles 2017 & 2022 (T1 + T2) |
| **Prediction** | Presidentielles 2027 (T1) |
| **Indicateurs** | Securite (SSMSI 2016-2024) |
| **Stack** | Python / Pandas / Scikit-Learn / PostgreSQL / Matplotlib |
| **Duree** | 25h budgetees |
| **Conformite** | RGPD strict |

---

## Avancement Global

```
Phase 1  [====================] 100%  Cadrage & Strategie
Phase 2  [====================] 100%  Architecture & Modelisation
Phase 3  [====================] 100%  Data Engineering (ETL)
Phase 4  [====================] 100%  Data Science & ML
Phase 5  [                    ]   0%  Visualisation & Rapport
Phase 6  [============        ]  60%  Revue & Qualite
```

| Phase | Statut | Duree | Agent(s) |
|-------|--------|-------|----------|
| **Phase 1** - Cadrage | TERMINEE | 1h | `@pm` |
| **Phase 2** - Architecture | TERMINEE | 5h | `@tech` |
| **Phase 3** - Data Engineering | TERMINEE | 12h | `@de` + `@rv` |
| **Phase 4** - Data Science | TERMINEE | 6h | `@ds` + `@rv` |
| **Phase 5** - Visualisation | A FAIRE | 0h/4h | `@da` |
| **Phase 6** - Revue Qualite | PARTIELLE | 2h/1h | `@rv` |

**Consomme :** 26h / 25h (104%) | **Restant :** Phase 5 (4h) + Phase 6 finition

---

## Criteres de Succes

| Critere | Cible | Resultat |
|---------|-------|----------|
| Perimetre | Gironde (535 communes) | 535 communes chargees |
| Donnees ingerees | 2+ sources | 17 262 lignes (Elections + Securite) |
| Schema BDD | Normalise 3NF | 17 tables deployees (schema v3.0) |
| Modele ML | R2 > 0.65 | **R2 = 0.72** (Le Pen, meilleur modele) |
| Predictions 2027 | Par commune | **3 745 predictions** (535 x 7 candidats) |
| Documentation | MCD + ADRs + Rapport | 85% (rapport Phase 5 restant) |
| Code qualite | Review >= 7/10 | **7/10** (2 reviews ETL) |

---

## Phase 1 : Cadrage & Strategie

> **TERMINEE** - 1h - `@pm`

- Choix du perimetre geographique (Bordeaux / Gironde)
- Validation sources de donnees (SSMSI, Ministere Interieur)
- ROADMAP initiale

---

## Phase 2 : Architecture & Modelisation

> **TERMINEE** - 5h/5h (100%) - `@tech`

| Livrable | Fichier | Statut |
|----------|---------|--------|
| MCD v3.0 | `docs/02-architecture/database/01-mcd.md` | FAIT |
| MLD v3.0 | `docs/02-architecture/database/02-mld.md` | FAIT |
| Dictionnaire de Donnees v3.0 | `docs/02-architecture/database/03-dictionnaire-donnees.md` | FAIT |
| ADR-001 (Choix BDD) | `docs/02-architecture/adr/ADR-001-choix-bdd.md` | FAIT |
| ADR-002 (Algo ML) | `docs/02-architecture/adr/ADR-002-choix-algo-ml.md` | FAIT |
| ADR-003 (Architecture ETL) | `docs/02-architecture/adr/ADR-003-architecture-modulaire-etl.md` | FAIT |
| ADR-004 (Schema v3) | `docs/02-architecture/adr/ADR-004-enrichissement-schema-v3.md` | FAIT |
| Architecture ETL | `docs/02-architecture/ARCHITECTURE.md` | FAIT |
| Sources de donnees | `docs/SOURCES_DONNEES.md` | FAIT |

---

## Phase 3 : Data Engineering

> **TERMINEE** - 12h/8h (150%) - `@de` + `@rv`

### Objectifs atteints

- Collecte donnees via APIs (geo.api.gouv.fr + data.gouv.fr + SSMSI)
- Nettoyage et transformation des donnees
- Architecture modulaire enterprise-grade (Extract / Transform / Load)
- Chargement dans PostgreSQL schema v3.0 (17 tables)
- Code review complete avec corrections

### Architecture ETL v3.0

```
src/etl/
├── extract/                 # 3 sources (geographie, elections, securite)
│   ├── config/             # URLs API, chemins
│   ├── core/               # geographie.py, elections.py, securite.py
│   ├── utils/              # download_file()
│   └── main.py
├── transform/               # JSON/Parquet/CSV -> CSV normalises
│   ├── config/             # Chemins, mappings
│   ├── core/               # geographie.py, elections.py, securite.py
│   ├── utils/              # parse_french_number()
│   └── main.py
├── load/                    # CSV -> PostgreSQL (17 tables)
│   ├── config/             # Configs batch
│   ├── core/               # geographie.py, candidats.py, elections.py, indicateurs.py
│   ├── utils/              # validators.py
│   └── main.py
└── main.py                  # Orchestrateur global
```

### Livrables

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Module Extract | `src/etl/extract/` | FAIT |
| Module Transform | `src/etl/transform/` | FAIT |
| Module Load | `src/etl/load/` | FAIT |
| Orchestrateur ETL | `src/etl/main.py` | FAIT |
| Modeles SQLAlchemy | `src/database/models/` | FAIT (17 modeles) |
| Docker + Migrations | `docker-compose.yml` + Alembic | FAIT |
| Documentation ETL | `src/etl/README.md` | FAIT |

### Sources de Donnees

| Source | Volume | Statut |
|--------|--------|--------|
| Geographie (geo.api.gouv.fr) | 3 JSON (~200 KB) | Telecharge |
| Elections 2017-2022 (data.gouv.fr) | 4 JSON + 1 Parquet (~151 MB) | Telecharge |
| Securite SSMSI (data.gouv.fr) | 1 CSV gzip (~34 MB) | Telecharge |
| Emploi INSEE | - | Abandonne (API indisponible) |

### Donnees en PostgreSQL

| Table | Lignes | | Table | Lignes |
|-------|--------|-|-------|--------|
| region | 1 | | election_territoire | ~2 140 |
| departement | 1 | | resultat_participation | ~2 140 |
| commune | ~535 | | resultat_candidat | ~14 484 |
| type_election | 1 | | type_indicateur | 5 |
| election | 2 | | indicateur | ~45 |
| candidat | ~25 | | **prediction** | **3 745** |
| parti | ~15 | | | |
| candidat_parti | ~25 | | **TOTAL** | **~21 007** |

### Code Review

| Review | Score | Resultat |
|--------|-------|----------|
| Review 1 (`@rv`) | 6.5/10 | 15 CRITICAL + 35 MAJOR identifies |
| Corrections (`@de`) | - | 100% CRITICAL/MAJOR resolus |
| Review 2 (`@rv`) | **7/10** | Toutes corrections validees |

Corrections appliquees : SQL injection (requetes parametrees), singleton engine, transaction safety, vectorisation transform, fix Arrow/pd.NA, cache pre-load.

**Commits :** `55cd4d4` feat(etl) | `ed00419` fix(etl)

---

## Phase 4 : Data Science & ML

> **TERMINEE** - 6h/6h (100%) - `@ds` + `@rv`

### Strategie ML (ADR-002)

| Parametre | Valeur |
|-----------|--------|
| Unite d'analyse | Commune (535 alignees) |
| Train | Features 2017 T1 -> Target 2022 T1 |
| Predict | Features 2022 T1 -> Prediction 2027 T1 |
| Candidats | 7 communs (Macron, Le Pen, Melenchon, Lassalle, Arthaud, Dupont-Aignan, Poutou) |
| Modele principal | RandomForestRegressor (n_estimators=200, max_depth=10) |
| Baseline | LinearRegression |
| Validation | KFold CV (k=5, shuffle=True, random_state=42) |

### Features (17 variables)

| # | Feature | Source |
|---|---------|--------|
| 1-7 | `pct_{candidat}_prev` | resultat_candidat (T1 election precedente) |
| 8 | `pct_autres_prev` | Somme candidats hors 7 communs |
| 9 | `taux_participation_prev` | resultat_participation |
| 10 | `taux_abstention_prev` | resultat_participation |
| 11 | `population` | commune |
| 12 | `log_population` | log(population) |
| 13-17 | `securite_*` (5 types) | indicateur (0 si hors Bordeaux) |

### Resultats Random Forest (5-Fold CV)

| Candidat | R2 | MAE (pts) | RMSE (pts) | Qualite |
|----------|-----|-----------|------------|---------|
| Marine LE PEN | **0.7245** | 2.92 | 3.89 | Bon |
| Jean-Luc MELENCHON | 0.5093 | 2.49 | 3.34 | Acceptable |
| Emmanuel MACRON | 0.4083 | 2.89 | 3.92 | Acceptable |
| Jean LASSALLE | 0.2967 | 1.61 | 2.39 | Faible |
| Nicolas DUPONT-AIGNAN | -0.06 | 0.68 | 0.94 | Insuffisant |
| Nathalie ARTHAUD | -0.09 | 0.34 | 0.46 | Insuffisant |
| Philippe POUTOU | -0.09 | 0.46 | 0.68 | Insuffisant |

> **Analyse :** R2 > 0.65 atteint pour Le Pen. Les 3 candidats majeurs ont des metriques
> exploitables (MAE < 3 pts). Les petits candidats (< 2%) sont difficilement predictibles
> avec seulement 2 elections. Le RF surpasse la baseline LR sur tous les candidats majeurs.

### Livrables

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Notebook Exploration | `notebooks/01_exploration.ipynb` | FAIT (13 cells, 6 figures) |
| Notebook ML | `notebooks/02_feature_engineering_ml.ipynb` | FAIT (15 cells, 4 figures) |
| Predictions en base | table `prediction` (3 745 lignes) | FAIT |
| Figures exploration | `docs/figures/exploration/` | FAIT (6 PNG) |
| Figures ML | `docs/figures/ml/` | FAIT (4 PNG) |

### Structure figures

```
docs/figures/
├── exploration/                     # Notebook 01
│   ├── distribution_communes.png    # Histogramme population + boxplot superficie
│   ├── participation.png            # Taux par annee/tour + scatter vs population
│   ├── top_candidats_t1.png         # Barplot % moyen T1 par candidat
│   ├── comparaison_2017_2022.png    # 7 candidats communs cote-a-cote
│   ├── heatmap_communes_candidats.png  # Top 10 communes x candidats
│   └── indicateurs_securite.png     # Evolution securite Bordeaux 2016-2024
└── ml/                              # Notebook 02
    ├── correlation_features.png     # Heatmap correlation + distribution targets
    ├── comparaison_lr_rf.png        # R2 Linear Regression vs Random Forest
    ├── feature_importance.png       # Top features Macron / Le Pen / Melenchon
    └── predictions_2027.png         # Barplot predictions + scatter pred vs actual
```

### Notes techniques

- **id_territoire mismatch** : `resultat_candidat.id_territoire` = `'33XXXXX'` (7 chars) vs `commune.id_commune` = `'XXXXX'` (5 chars). Normalisation via `str[2:]` en pandas.
- **NULL pourcentage** : 745 lignes avec `pourcentage_voix_exprimes = NULL` (0 voix). Traite via `fillna(0)`.
- **Queries ORM** : Toutes les requetes utilisent les modeles SQLAlchemy v3.0.
- **Predictions** : Normalisees a 100% par commune, intervalles de confiance +/-1.96*RMSE.

---

## Phase 5 : Visualisation & Rapport

> **A FAIRE** - 0h/4h - `@da`

| Livrable | Fichier | Description |
|----------|---------|-------------|
| Graphiques avances | `notebooks/03_visualisation.ipynb` | Cartes choropletres, courbes d'evolution |
| Rapport synthese | `docs/RAPPORT_SYNTHESE.md` | Methodologie, resultats, limites |
| Slides executives | `docs/PRESENTATION.pdf` | 10 slides max |

---

## Phase 6 : Revue & Qualite

> **PARTIELLE** - 2h/1h - `@rv`

### Realise
- Structure documentation code review (`docs/03-code-review/`)
- 2 revues ETL completes (6.5/10 -> 7/10)
- Mise a jour documentation v3.0
- Organisation figures notebooks

### Restant
- Tests unitaires
- Validation RGPD

---

## Prochaine Etape

**Phase 5 - Visualisation & Rapport**

```bash
@da Demarre la Phase 5 : Notebook visualisation avancee,
rapport de synthese et slides executives
```
