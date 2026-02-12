# ROADMAP - Electio-Analytics POC

## Perimetre Valide

**Zone geographique :** Bordeaux - Gironde (33)
**Type d'election :** Presidentielles 2017 & 2022 (1er et 2nd tours) -> Prediction 2027
**Indicateurs socio-eco :** Securite (SSMSI)

---

## Contraintes Projet

| Contrainte | Valeur |
|------------|--------|
| **Duree totale** | 25h |
| **Perimetre geographique** | Gironde (535 communes) |
| **Stack technique** | Python, Pandas, Scikit-Learn, SQL, Matplotlib/PowerBI |
| **Conformite** | RGPD strict |
| **Livrabilite** | Code documente + Rapport + ADRs |

---

## Phase 1 : Cadrage & Strategie - TERMINEE

**Duree :** 1h
**Agent :** `@pm`

### Livrables
- Choix du perimetre geographique (Bordeaux / Gironde)
- Validation sources de donnees (SSMSI, Ministere Interieur)
- ROADMAP.md

---

## Phase 2 : Architecture & Modelisation - TERMINEE (5h/5h - 100%)

**Agent :** `@tech`

### Livrables

| Livrable | Fichier | Statut |
|----------|---------|--------|
| **MCD v3.0** | `docs/02-architecture/database/01-mcd.md` | FAIT |
| **MLD v3.0** | `docs/02-architecture/database/02-mld.md` | FAIT |
| **Dictionnaire de Donnees v3.0** | `docs/02-architecture/database/03-dictionnaire-donnees.md` | FAIT |
| **ADR-001** | `docs/02-architecture/adr/ADR-001-choix-bdd.md` | FAIT |
| **ADR-002** | `docs/02-architecture/adr/ADR-002-choix-algo-ml.md` | FAIT |
| **ADR-003** | `docs/02-architecture/adr/ADR-003-architecture-modulaire-etl.md` | FAIT |
| **ADR-004** | `docs/02-architecture/adr/ADR-004-enrichissement-schema-v3.md` | FAIT |
| **Architecture ETL** | `docs/02-architecture/ARCHITECTURE.md` | FAIT |
| **Sources de donnees** | `docs/SOURCES_DONNEES.md` | FAIT |

---

## Phase 3 : Data Engineering - TERMINEE (12h/8h - 150%)

**Agent :** `@de` + `@rv` (Code Review)
**Duree reelle :** 12h (incluant ETL v3.0 complet + corrections review + documentation)

### Objectifs atteints
- Collecte donnees via APIs (geo.api.gouv.fr + data.gouv.fr tabulaire + Parquet + SSMSI)
- Nettoyage et transformation des donnees
- Architecture modulaire enterprise-grade (Extract/Transform/Load)
- Chargement dans PostgreSQL schema v3.0 (17 tables)
- Code review complete avec corrections

### Architecture ETL v3.0 Implementee

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
│   ├── core/               # geographie.py, candidats.py, elections.py, indicateurs.py, type_indicateur.py
│   ├── utils/              # validators.py
│   └── main.py
└── main.py                  # Orchestrateur global
```

### Livrables

| Livrable | Fichier | Statut |
|----------|---------|--------|
| **Module Extract** | `src/etl/extract/` | FAIT |
| **Module Transform** | `src/etl/transform/` | FAIT |
| **Module Load** | `src/etl/load/` | FAIT |
| **Orchestrateur ETL** | `src/etl/main.py` | FAIT |
| **Modeles SQLAlchemy** | `src/database/models/` | FAIT (17 modeles) |
| **Docker + Migrations** | `docker-compose.yml` + Alembic | FAIT |
| **Documentation ETL** | `src/etl/README.md` | FAIT |

### Sources de Donnees Finales

| Source | Statut | Volume |
|--------|--------|--------|
| **Geographie** (geo.api.gouv.fr) | Telecharge | 3 JSON (~200 KB) |
| **Elections 2017 & 2022** (data.gouv.fr) | Telecharge | 4 JSON + 1 Parquet (~151 MB) |
| **Securite SSMSI** (data.gouv.fr) | Telecharge | 1 CSV gzip (~34 MB) |
| **Emploi INSEE** | Abandonne | API indisponible |

### Donnees Chargees en PostgreSQL

| Table | Lignes |
|-------|--------|
| region | 1 |
| departement | 1 |
| commune | ~535 |
| type_election | 1 |
| election | 2 |
| candidat | ~25 |
| parti | ~15 |
| candidat_parti | ~25 |
| election_territoire | ~2 140 |
| resultat_participation | ~2 140 |
| resultat_candidat | ~14 484 |
| type_indicateur | 5 |
| indicateur | ~45 |
| **TOTAL** | **~17 262** |

### Code Review (2026-02-12)

**Review 1** (@rv) : Score 6.5/10 - 15 CRITICAL, 35 MAJOR identifies
**Corrections** (@de) : 100% des issues CRITICAL/MAJOR resolus
- Corrections SQL injection (requetes parametrees + whitelist)
- Singleton engine pattern
- Transaction safety (IntegrityError + rollback)
- Vectorisation transform (remplacement iterrows)
- Fix Arrow/pd.NA pour Parquet
- Cache pre-load (elimination N+1 queries)

**Review 2** (@rv) : Score 7/10 (+0.5) - Toutes corrections validees
**Pipeline re-execute** : 17,262 lignes chargees avec succes

### Commits
- `55cd4d4` : `feat(etl): Pipeline ETL v3.0 complet`
- `ed00419` : `fix(etl): Corrections review @rv - securite, transactions, performance`

---

## Phase 4 : Data Science & ML (6h)

**Agent :** `@ds`
**Statut :** PAS COMMENCEE

### Objectifs
- Analyser les correlations entre indicateurs socio-eco et resultats electoraux
- Entrainer un modele predictif pour 2027
- Evaluer la performance du modele

### Livrables

| Livrable | Fichier | Description |
|----------|---------|-------------|
| **Notebook EDA** | `notebooks/01_exploration.ipynb` | Analyses exploratoires, correlations |
| **Notebook Feature Eng.** | `notebooks/02_feature_engineering.ipynb` | Creation variables |
| **Script Modele ML** | `src/models/train_model.py` | Random Forest + Regression Lineaire baseline |
| **Script Prediction** | `src/models/predict_2027.py` | Generation predictions 2027 |
| **Metriques** | `docs/METRIQUES.md` | MAE, RMSE, R2 |

### Pre-requis valides
- PostgreSQL operationnel avec 17,262 lignes
- 14,484 resultats candidats (2017 + 2022, tours 1 & 2, ~535 communes)
- 45 indicateurs securite (5 categories x 9 annees 2016-2024)
- Pipeline ETL fonctionnel et reproductible

### Donnees Disponibles pour ML
- **Resultats candidats** : Voix, pourcentages par commune/election/tour
- **Participation** : Inscrits, votants, abstentions, blancs/nuls par commune
- **Securite** : 5 indicateurs x 9 ans (tendances temporelles)
- **Geographie** : Population, superficie communes
- **Features derivees possibles** : Evolution participation 2017->2022, tendance criminalite, densite

---

## Phase 5 : Visualisation & Rapport (4h)

**Agent :** `@da`
**Statut :** PAS COMMENCEE

### Livrables

| Livrable | Fichier | Description |
|----------|---------|-------------|
| **Graphiques** | `notebooks/03_visualisation.ipynb` | Cartes choropletres, courbes d'evolution |
| **Rapport synthese** | `docs/RAPPORT_SYNTHESE.md` | Methodologie, resultats, limites |
| **Slides executives** | `docs/PRESENTATION.pdf` | 10 slides max |

---

## Phase 6 : Revue & Qualite (1h)

**Agent :** `@rv`
**Statut :** PARTIELLE

### Realise
- Structure documentation code review (`docs/03-code-review/`)
- 2 revues ETL completes (6.5/10 -> 7/10)
- Mise a jour documentation v3.0

### Restant
- Tests unitaires
- Validation RGPD

---

## Etat d'Avancement Global

| Phase | Statut | Duree | Complete |
|-------|--------|-------|----------|
| **Phase 1** : Cadrage | TERMINEE | 1h | 100% |
| **Phase 2** : Architecture | TERMINEE | 5h/5h | 100% |
| **Phase 3** : Data Engineering | TERMINEE | 12h/8h | 150% |
| **Phase 4** : Data Science | PAS COMMENCEE | 0h/6h | 0% |
| **Phase 5** : Visualisation | PAS COMMENCEE | 0h/4h | 0% |
| **Phase 6** : Revue Qualite | PARTIELLE | 2h/1h | 60% |

**Total consomme :** 20h / 25h (80%)
**Temps restant :** 5h (Phase 4: 6h + Phase 5: 4h - depassement: 5h)

---

## Criteres de Succes

| Critere | Cible | Statut |
|---------|-------|--------|
| **Perimetre** | Gironde (535 communes) | Valide |
| **Donnees ingerees** | 2 sources (Elections + Securite) | 17,262 lignes |
| **Schema BDD** | 17 tables normalisees (3NF) | Deploye |
| **Modele ML** | R2 > 0.65 sur validation | A faire |
| **Predictions 2027** | Generees par commune | A faire |
| **Documentation** | MCD + MLD + ADRs + Rapport | 80% fait |
| **Code qualite** | PEP8 + Docstrings + Reproductible | Review 7/10 |

---

## Prochaine Etape

**Phase 4 - Data Science & Machine Learning**

```bash
@ds Demarre la Phase 4 : Analyse exploratoire, feature engineering,
entrainement Random Forest pour prediction 2027
```
