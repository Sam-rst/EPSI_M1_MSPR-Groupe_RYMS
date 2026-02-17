# A2 - Architecture Business Intelligence

> **Competence C2 :** Definir une architecture business intelligence a partir des orientations strategiques afin de mettre a disposition des utilisateurs metiers les donnees structurees d'un SI.

---

## 1. Choix technologiques (5 ADRs)

| ADR | Decision | Alternative ecartee | Justification |
|-----|----------|---------------------|---------------|
| ADR-001 | **PostgreSQL** | MongoDB, SQLite | SQL avance, integrite ACID, PostGIS, compatibilite Pandas |
| ADR-002 | **Random Forest** | XGBoost, LSTM, SVM | Non-lineaire, feature importance, peu de tuning, POC 25h |
| ADR-003 | **ETL modulaire (Option 3)** | Fichiers plats, Option 1/2 | Separation config/core/utils, testabilite, standards enterprise |
| ADR-004 | **Schema v3.0** | Schema v1/v2 | Systeme polymorphe de territoire, normalisation 3NF |
| ADR-005 | **Perimetre Gironde** | Bordeaux seul, National | Volume maitrisable (534 communes), richesse statistique |

## 2. Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE BI                            │
├──────────────┬──────────────────┬───────────────────────────┤
│   SOURCES    │    TRAITEMENT    │       RESTITUTION          │
│              │                  │                             │
│ geo.api ─────┤                  │  Notebook exploration ──── │
│              │  EXTRACT ────────┤  Notebook ML ───────────── │
│ data.gouv ──┤  TRANSFORM ──────┤  Notebook visualisation ── │
│              │  LOAD ──────────┤  Cartes Folium ──────────── │
│ SSMSI ──────┤                  │  Rapport de synthese ───── │
│              │  PostgreSQL 15   │                             │
│              │  (17 tables)     │  Predictions 2027          │
│              │  Docker Compose  │  (3 745 lignes)            │
└──────────────┴──────────────────┴───────────────────────────┘
```

## 3. Schema de donnees (MCD v3.0)

**17 tables** organisees en 5 domaines :

| Domaine | Tables | Lignes |
|---------|--------|--------|
| Geographie | Region, Departement, Commune, Canton, Arrondissement, Bureau | 537 |
| Candidats | Candidat, Parti, CandidatParti | 56 |
| Elections | TypeElection, Election, ElectionTerritoire | 1 076 |
| Resultats | ResultatParticipation, ResultatCandidat | 16 630 |
| Indicateurs + ML | TypeIndicateur, Indicateur, Prediction | 3 795 |
| **Total** | **17 tables** | **~21 000** |

**Innovation architecturale** : systeme polymorphe `(id_territoire, type_territoire)` permettant de stocker resultats, indicateurs et predictions a n'importe quel niveau geographique sans jointures multiples.

## 4. Stack technique

| Couche | Technologie | Version |
|--------|-------------|---------|
| Langage | Python | 3.12 |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | 1.16+ |
| BDD | PostgreSQL + PostGIS | 15 |
| ML | Scikit-Learn | 1.5+ |
| Visualisation | Matplotlib, Seaborn, Folium | - |
| Infrastructure | Docker Compose | - |
| Packages | UV | - |

**Fichiers de reference :**
- Architecture complete : `docs/02-architecture/ARCHITECTURE.md`
- ADRs : `docs/02-architecture/adr/ADR-001` a `ADR-005`
- MCD/MLD : `docs/02-architecture/database/01-mcd.md`, `02-mld.md`
- Dictionnaire : `docs/02-architecture/database/03-dictionnaire-donnees.md`
