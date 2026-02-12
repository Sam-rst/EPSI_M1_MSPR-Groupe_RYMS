# Setup Base de Donnees PostgreSQL + Alembic

**Projet :** Electio-Analytics
**Version :** 3.0
**Date :** 2026-02-12
**Auteur :** @tech

---

## Table des matieres

- [1. Prerequis](#1-prerequis)
- [2. Installation PostgreSQL avec Docker](#2-installation-postgresql-avec-docker)
- [3. Creation du schema (Alembic)](#3-creation-du-schema-alembic)
- [4. Lancer le pipeline ETL](#4-lancer-le-pipeline-etl)
- [5. Commandes Alembic](#5-commandes-alembic)
- [6. Troubleshooting](#6-troubleshooting)

---

## 1. Prerequis

- **Docker Desktop** installe et demarre
- **Python 3.11** avec UV package manager
- **Variables d'environnement** configurees dans `.env`

```bash
# Verifier Docker
docker --version        # Docker version 27.4.0+
docker compose version  # Docker Compose version v2.31.0+

# Verifier UV
uv --version            # uv 0.9.x+

# Verifier Python
python --version        # Python 3.11.x
```

---

## 2. Installation PostgreSQL avec Docker

### 2.1. Configuration

Le projet utilise **PostgreSQL 15** avec l'extension **PostGIS**.

**Fichier `.env` :**
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=electio_analytics
POSTGRES_USER=admin
POSTGRES_PASSWORD=votre_mot_de_passe_ici
```

### 2.2. Demarrage

```bash
# Demarrer PostgreSQL
docker compose up -d

# Verifier le statut (doit etre "healthy")
docker compose ps

# Tester la connexion
docker exec electio_postgres psql -U admin -d electio_analytics -c "SELECT version();"
```

**Sortie attendue :**
```
PostgreSQL 15.8 (Debian 15.8-1.pgdg110+1) on x86_64-pc-linux-gnu
```

### 2.3. Extensions installees

Le script `scripts/init-db.sql` installe automatiquement :
- `postgis` : Donnees geospatiales
- `uuid-ossp` : Generation UUID
- `btree_gin` : Index GIN optimises

---

## 3. Creation du schema (Alembic)

### 3.1. Structure des fichiers

```
src/database/
├── alembic.ini              # Configuration Alembic
├── config.py                # Configuration connexion DB
├── migrations/
│   ├── env.py               # Environnement migrations
│   └── versions/            # 4 fichiers de migration
│       ├── 7b72b070fd66_initial_schema.py         # v2.0 (historique)
│       ├── a14be11ce7ab_nullable_election_columns.py
│       ├── 5c74986a8b20_remove_obsolete_v2_tables.py
│       └── 691a1578615b_create_schema_v3_0.py     # v3.0 (17 tables)
└── models/                  # 17 modeles ORM SQLAlchemy
    ├── __init__.py
    ├── base.py
    ├── region.py
    ├── departement.py
    ├── commune.py
    ├── canton.py
    ├── arrondissement.py
    ├── bureau_vote.py
    ├── type_election.py
    ├── election.py
    ├── candidat.py
    ├── parti.py
    ├── candidat_parti.py
    ├── election_territoire.py
    ├── resultat_participation.py
    ├── resultat_candidat.py
    ├── type_indicateur.py
    ├── indicateur.py
    └── prediction.py
```

### 3.2. Appliquer les migrations

```bash
# Depuis la racine du projet
uv run alembic -c src/database/alembic.ini upgrade head
```

**Sortie attendue :**
```
INFO  Running upgrade  -> 7b72b070fd66, initial_schema
INFO  Running upgrade 7b72b070fd66 -> a14be11ce7ab, nullable_election_columns
INFO  Running upgrade a14be11ce7ab -> 5c74986a8b20, Remove obsolete v2 tables
INFO  Running upgrade 5c74986a8b20 -> 691a1578615b, Create schema v3.0
```

### 3.3. Verification des tables creees

```bash
docker exec electio_postgres psql -U admin -d electio_analytics -c "\dt public.*"
```

**17 tables v3.0 :**

| Domaine | Tables |
|---------|--------|
| **Geographie** (6) | region, departement, commune, canton, arrondissement, bureau_vote |
| **References electorales** (2) | type_election, election |
| **References politiques** (3) | candidat, parti, candidat_parti |
| **Resultats** (3) | election_territoire, resultat_participation, resultat_candidat |
| **Indicateurs** (2) | type_indicateur, indicateur |
| **ML** (1) | prediction |

---

## 4. Lancer le pipeline ETL

```bash
# Pipeline complet : Extract + Transform + Load
uv run python -m src.etl.main
```

**Resultat attendu : 17 262 lignes chargees en ~130s**

| Table | Lignes |
|-------|--------|
| region | 1 |
| departement | 1 |
| commune | 534 |
| type_election | 1 |
| election | 2 |
| candidat | 16 |
| parti | 11 |
| candidat_parti | 16 |
| election_territoire | 1 073 |
| resultat_participation | 2 146 |
| resultat_candidat | 14 484 |
| type_indicateur | 5 |
| indicateur | 45 |

---

## 5. Commandes Alembic

### 5.1. Commandes principales

| Commande | Description |
|----------|-------------|
| `uv run alembic -c src/database/alembic.ini current` | Version actuelle |
| `uv run alembic -c src/database/alembic.ini history` | Historique migrations |
| `uv run alembic -c src/database/alembic.ini upgrade head` | Appliquer toutes les migrations |
| `uv run alembic -c src/database/alembic.ini downgrade -1` | Annuler derniere migration |

### 5.2. Generer une nouvelle migration

```bash
# Apres modification des modeles ORM dans src/database/models/
uv run alembic -c src/database/alembic.ini revision --autogenerate -m "description"

# Verifier le fichier genere, puis appliquer
uv run alembic -c src/database/alembic.ini upgrade head
```

---

## 6. Troubleshooting

### 6.1. "Connection refused" port 5432

```bash
# Verifier que Docker est demarre
docker compose ps
# Si "Exited" : docker compose up -d
```

### 6.2. "password authentication failed"

Verifier que `.env` contient le bon mot de passe et que `docker compose` a ete relance apres modification :
```bash
docker compose down && docker compose up -d
```

### 6.3. "relation already exists" (migration echouee)

```bash
# Reset complet de la base
docker compose down -v
docker compose up -d
# Attendre 10s que PostgreSQL demarre
uv run alembic -c src/database/alembic.ini upgrade head
```

### 6.4. Reinitialiser completement

```bash
# Supprimer le conteneur et les donnees
docker compose down -v
docker volume rm epsi_m1_mspr-groupe_ryms_postgres_data 2>/dev/null

# Redemarrer
docker compose up -d

# Appliquer les migrations
uv run alembic -c src/database/alembic.ini upgrade head

# Relancer l'ETL
uv run python -m src.etl.main
```

---

**Derniere mise a jour :** 2026-02-12
**Schema :** v3.0 (17 tables)
