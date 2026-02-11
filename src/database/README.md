# Module Database - Electio-Analytics

**Module :** `src/database/`
**Stack :** PostgreSQL 15 + PostGIS + SQLAlchemy 2.0 + Alembic
**Architecture :** MCD v2.0 (Architecture Scalable)
**Auteur :** @tech

---

## Description

Module de gestion base de données pour Electio-Analytics.

**Fonctionnalités :**
- Connexion PostgreSQL avec pool de connexions
- Migrations automatiques avec Alembic
- 5 modèles ORM SQLAlchemy
- Support PostGIS pour données géospatiales

---

## Structure

```
src/database/
├── README.md                 ← Vous êtes ici
├── config.py                 ← Configuration connexion PostgreSQL
├── alembic.ini               ← Configuration Alembic
├── migrations/
│   ├── env.py                ← Environnement migrations
│   └── versions/             ← Fichiers migrations
│       └── 20260211_1129_7b72b070fd66_initial_schema.py
└── models/                   ← Modèles SQLAlchemy ORM
    ├── __init__.py           ← Export tous les modèles
    ├── base.py               ← Base déclarative
    ├── territoire.py         ← Référentiel géographique
    ├── type_indicateur.py    ← Types d'indicateurs
    ├── indicateur.py         ← Indicateurs socio-économiques
    ├── election_result.py    ← Résultats électoraux
    └── prediction.py         ← Prédictions ML 2027
```

---

## Quick Start

### 1. Démarrer PostgreSQL (Docker)

```bash
# Démarrer conteneur
docker-compose up -d

# Vérifier
docker-compose ps

# Logs
docker logs electio_postgres
```

### 2. Appliquer les migrations

```bash
cd src/database
alembic upgrade head
```

### 3. Vérifier les tables

```bash
docker exec electio_postgres psql -U admin -d electio_analytics -c "\dt"
```

**Sortie attendue :**
```
 public | alembic_version | table | admin
 public | election_result | table | admin
 public | indicateur      | table | admin
 public | prediction      | table | admin
 public | territoire      | table | admin
 public | type_indicateur | table | admin
```

---

## Configuration

### Variables d'environnement (`.env`)

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=electio_analytics
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password_2024!

# Options connexion (optionnel)
DB_ECHO_SQL=False
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

### Utilisation Python

```python
from src.database.config import get_engine, get_session
import pandas as pd

# Engine (pour Pandas)
engine = get_engine()
df = pd.read_sql("SELECT * FROM territoire LIMIT 10", engine)

# Session ORM
with get_session() as session:
    result = session.execute("SELECT COUNT(*) FROM type_indicateur")
    count = result.fetchone()[0]
```

---

## Modèles ORM

### 1. Territoire

**Table :** `territoire`

```python
from src.database.models import Territoire

territoire = Territoire(
    id_territoire='33063',
    code_insee='33063',
    type_territoire='COMMUNE',
    nom_territoire='Bordeaux',
    population=252040
)
```

**Colonnes clés :**
- `geometry` : Polygon PostGIS (SRID 4326)
- `metadata_` : JSONB

### 2. TypeIndicateur

**Table :** `type_indicateur`

```python
from src.database.models import TypeIndicateur

type_ind = TypeIndicateur(
    code_type='CRIMINALITE_TOTALE',
    categorie='SECURITE',
    nom_affichage='Criminalité totale',
    unite_mesure='nombre'
)
```

### 3. Indicateur (Pattern EAV)

**Table :** `indicateur`

```python
from src.database.models import Indicateur

indicateur = Indicateur(
    id_territoire='33063',
    id_type=1,
    annee=2022,
    valeur_numerique=504.0,
    fiabilite='CONFIRME'
)
```

### 4. ElectionResult

**Table :** `election_result`

```python
from src.database.models import ElectionResult

result = ElectionResult(
    id_territoire='BV_33063_001',
    annee=2022,
    tour=1,
    candidat='Emmanuel MACRON',
    nombre_voix=450,
    pourcentage_voix=28.45
)
```

### 5. Prediction

**Table :** `prediction`

```python
from src.database.models import Prediction

prediction = Prediction(
    id_territoire='IRIS_330630101',
    candidat='Emmanuel MACRON',
    tour=1,
    annee_prediction=2027,
    pourcentage_predit=32.15,
    modele_utilise='RandomForest'
)
```

---

## Alembic - Migrations

### Workflow Standard

```bash
cd src/database

# 1. Modifier modèles ORM

# 2. Générer migration
alembic revision --autogenerate -m "description"

# 3. Appliquer
alembic upgrade head

# 4. Vérifier
alembic current
```

### Commandes Principales

| Commande | Action |
|----------|--------|
| `alembic current` | Version actuelle |
| `alembic history` | Historique |
| `alembic upgrade head` | Tout appliquer |
| `alembic upgrade +1` | Suivante |
| `alembic downgrade -1` | Annuler dernière |
| `alembic show <rev>` | Détails révision |

---

## Architecture v2.0

### Tables

| Table | Rows (estimé) | Description |
|-------|---------------|-------------|
| `territoire` | ~100 | Référentiel géographique |
| `type_indicateur` | ~20 | Catalogue indicateurs |
| `indicateur` | ~4,000 | Données socio-économiques |
| `election_result` | ~2,000 | Résultats 2017 & 2022 |
| `prediction` | ~500 | Prédictions ML 2027 |

### Avantages

- ✅ **Extensibilité :** Ajout source = 1 INSERT `type_indicateur`
- ✅ **Flexibilité :** JSONB pour métadonnées variables
- ✅ **Performance :** Index GIST (PostGIS), GIN (JSONB), BTREE
- ✅ **Maintenabilité :** 5 tables au lieu de N

---

## Exemples Requêtes

### Dataset ML complet

```sql
SELECT
    t.id_territoire,
    t.nom_territoire,
    er.candidat,
    er.pourcentage_voix,

    -- Pivot indicateurs
    AVG(CASE WHEN ti.categorie = 'SECURITE'
        THEN i.valeur_numerique END) AS criminalite,
    AVG(CASE WHEN ti.code_type = 'EMPLOI_TAUX_CHOMAGE'
        THEN i.valeur_numerique END) AS chomage

FROM territoire t
LEFT JOIN election_result er ON t.id_territoire = er.id_territoire
LEFT JOIN indicateur i ON t.id_territoire = i.id_territoire
LEFT JOIN type_indicateur ti ON i.id_type = ti.id_type

WHERE er.tour = 2 AND er.annee IN (2017, 2022)
GROUP BY t.id_territoire, t.nom_territoire, er.candidat, er.pourcentage_voix;
```

---

## Troubleshooting

### ❌ "password authentication failed"

**Solution :**
```python
# Vérifier config.py charge .env
from dotenv import load_dotenv
load_dotenv()
```

### ❌ "relation already exists"

**Solution :**
```bash
# Nettoyer + réappliquer
docker exec electio_postgres psql -U admin -d electio_analytics \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

docker exec electio_postgres psql -U admin -d electio_analytics \
  -c "CREATE EXTENSION postgis; CREATE EXTENSION btree_gin;"

cd src/database && alembic upgrade head
```

### ❌ "geoalchemy2 is not defined"

**Solution :**
```python
# Ajouter dans migrations/versions/*.py
import geoalchemy2
```

---

## Documentation Complète

**Guide détaillé :** [`docs/04-setup-installation/SETUP_DATABASE.md`](../../docs/04-setup-installation/SETUP_DATABASE.md)

**MCD v2.0 :** [`docs/02-architecture/database/`](../../docs/02-architecture/database/)

---

## Références

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/)
- [PostGIS](https://postgis.net/documentation/)

---

**Dernière mise à jour :** 2026-02-11
**Auteur :** @tech (Claude Sonnet 4.5)
