# B1 - Pipeline ETL (Strategie Big Data)

> **Competence C3 :** Definir une strategie big data (de la collecte aux traitements des donnees) afin d'aider l'entreprise a mieux comprendre ses clients et a creer de nouveaux services.

---

## 1. Strategie collecte → traitement

```
EXTRACT                    TRANSFORM                  LOAD
─────────────────          ─────────────────          ─────────────────
3 APIs publiques      →    Nettoyage/Normalisation →  PostgreSQL 15

geo.api.gouv.fr            JSON → CSV communes        17 tables
(REST JSON, 200 KB)        (534 lignes)               Schema v3.0

data.gouv.fr               Parquet → CSV agrege       21 007 lignes
(JSON+Parquet, 151 MB)     (participation + candidats)

SSMSI                      CSV → CSV filtre           Contraintes FK
(CSV gzip, 34 MB)          (Bordeaux 2016-2024)       UNIQUE, CHECK
```

## 2. Architecture modulaire (ADR-003)

```
src/etl/
├── extract/                    # Phase 1 : Collecte
│   ├── config/settings.py      # URLs API, chemins de sortie
│   ├── core/
│   │   ├── geographie.py       # geo.api.gouv.fr → 3 JSON
│   │   ├── elections.py        # data.gouv.fr → 4 JSON + 1 Parquet
│   │   └── securite.py         # SSMSI → 1 CSV gzip
│   ├── utils/download.py       # Streaming avec barre de progression
│   └── main.py                 # Orchestrateur extract
│
├── transform/                  # Phase 2 : Nettoyage
│   ├── config/settings.py      # Chemins, mappings colonnes
│   ├── core/
│   │   ├── geographie.py       # JSON → CSV (regions, depts, communes)
│   │   ├── elections.py        # Agregation participation, pivot candidats
│   │   └── securite.py         # Filtrage Gironde, mapping types
│   ├── utils/parsing.py        # Parsing nombres francais (1.234,56)
│   └── main.py                 # Orchestrateur transform
│
├── load/                       # Phase 3 : Chargement BDD
│   ├── config/settings.py      # Tailles de batch, chemins CSV
│   ├── core/
│   │   ├── geographie.py       # Region, Departement, Commune
│   │   ├── candidats.py        # Candidat, Parti, CandidatParti
│   │   ├── elections.py        # ElectionTerritoire, Resultats
│   │   └── indicateurs.py      # Batch loading (1000 lignes/batch)
│   ├── utils/validators.py     # 14 fonctions de validation
│   └── main.py                 # Orchestrateur load (respect ordre FK)
│
└── main.py                     # Orchestrateur global E→T→L
```

**Principe** : chaque source = 1 fichier dans `core/`. Ajout d'une nouvelle source = 1 fichier, sans toucher aux autres.

## 3. Traitements appliques

| Etape | Traitement | Exemple |
|-------|-----------|---------|
| Parsing | Nombres francais → float | `1.234,56` → `1234.56` |
| Normalisation | IDs territoire 7 chars → 5 chars | `33XXXXX` → `XXXXX` |
| Gestion NULL | Pourcentages manquants → 0% | 745 lignes avec 0 voix |
| Agregation | Somme voix par commune/candidat | Bureau → Commune |
| Validation | Colonnes, types, bornes, unicite | 14 validators |

## 4. Resultats

| Metrique | Valeur |
|----------|--------|
| Donnees brutes collectees | 185 MB (3 sources) |
| Donnees nettoyees | 3 MB (8 fichiers CSV) |
| Lignes chargees en BDD | 21 007 |
| Tables alimentees | 17 |
| Temps d'execution ETL | ~5 min |

**Fichiers de reference :**
- Code ETL : `src/etl/`
- Documentation : `src/etl/README.md`
- ADR architecture : `docs/02-architecture/adr/ADR-003-architecture-modulaire-etl.md`
