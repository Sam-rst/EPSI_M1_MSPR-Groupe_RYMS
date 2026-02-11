# Setup Base de Données PostgreSQL + Alembic

**Projet :** Electio-Analytics
**Version :** 1.0.0
**Date :** 2026-02-11
**Auteur :** @tech

---

## Table des matières

- [1. Prérequis](#1-prérequis)
- [2. Installation PostgreSQL avec Docker](#2-installation-postgresql-avec-docker)
- [3. Configuration Alembic](#3-configuration-alembic)
- [4. Première migration](#4-première-migration)
- [5. Commandes Alembic](#5-commandes-alembic)
- [6. Troubleshooting](#6-troubleshooting)

---

## 1. Prérequis

- **Docker Desktop** installé et démarré
- **Python 3.9+** avec UV package manager
- **Variables d'environnement** configurées dans `.env`

```bash
# Vérifier Docker
docker --version  # Docker version 27.4.0+
docker-compose --version  # Docker Compose version v2.31.0+
```

---

## 2. Installation PostgreSQL avec Docker

### 2.1. Fichiers de configuration

Le projet utilise **PostgreSQL 15.8** avec l'extension **PostGIS** pour les données géospatiales.

**Fichier `docker-compose.yml` :**
```yaml
services:
  postgres:
    image: postgis/postgis:15-3.4
    container_name: electio_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-electio_analytics}
      POSTGRES_USER: ${POSTGRES_USER:-admin}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secure_password}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - electio_network

volumes:
  postgres_data:

networks:
  electio_network:
```

**Fichier `.env` :**
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=electio_analytics
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password_2024!
```

### 2.2. Démarrage PostgreSQL

```bash
# Démarrer PostgreSQL
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Logs PostgreSQL
docker logs electio_postgres

# Tester la connexion
docker exec electio_postgres psql -U admin -d electio_analytics -c "SELECT version();"
```

**Sortie attendue :**
```
PostgreSQL 15.8 (Debian 15.8-1.pgdg110+1) on x86_64-pc-linux-gnu
```

### 2.3. Extensions installées

```bash
docker exec electio_postgres psql -U admin -d electio_analytics -c "SELECT extname FROM pg_extension;"
```

**Extensions :**
- `postgis` : Données géospatiales (POLYGON, POINT, etc.)
- `uuid-ossp` : Génération UUID
- `btree_gin` : Index GIN optimisés

---

## 3. Configuration Alembic

### 3.1. Structure des fichiers

```
src/database/
├── alembic.ini              # Configuration Alembic
├── migrations/
│   ├── env.py               # Environnement migrations
│   └── versions/            # Fichiers migrations
│       └── 20260211_1129_7b72b070fd66_initial_schema.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── territoire.py
│   ├── type_indicateur.py
│   ├── indicateur.py
│   ├── election_result.py
│   └── prediction.py
└── config.py                # Configuration connexion DB
```

### 3.2. Configuration `alembic.ini`

**Fichier :** `src/database/alembic.ini`

```ini
[alembic]
script_location = %(here)s/migrations
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
prepend_sys_path = .

# URL base de données (surchargée par env.py)
sqlalchemy.url = driver://user:pass@localhost/dbname
```

### 3.3. Configuration `env.py`

**Points clés :**
- Chargement automatique du fichier `.env` avec `python-dotenv`
- Import de tous les modèles ORM via `from src.database.models import Base`
- Récupération de l'URL PostgreSQL depuis `DatabaseConfig`

**Fichier :** `src/database/migrations/env.py`

```python
from dotenv import load_dotenv
from src.database.models import Base
from src.database.config import DatabaseConfig

# Métadonnées SQLAlchemy
target_metadata = Base.metadata

def get_url():
    return DatabaseConfig.get_database_url()
```

---

## 4. Première migration

### 4.1. Génération migration initiale

```bash
cd src/database
alembic revision --autogenerate -m "initial_schema"
```

**Sortie :**
```
INFO  [alembic.autogenerate.compare] Detected added table 'territoire'
INFO  [alembic.autogenerate.compare] Detected added table 'type_indicateur'
INFO  [alembic.autogenerate.compare] Detected added table 'election_result'
INFO  [alembic.autogenerate.compare] Detected added table 'indicateur'
INFO  [alembic.autogenerate.compare] Detected added table 'prediction'

Generating .../versions/20260211_1129_7b72b070fd66_initial_schema.py ... done
```

### 4.2. Corrections manuelles nécessaires

**⚠️ Import manquant :** Ajouter `import geoalchemy2` dans le fichier de migration.

**Fichier :** `src/database/migrations/versions/20260211_1129_*.py`

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2  # ← AJOUTER CETTE LIGNE
```

**⚠️ Suppression table PostGIS :** Commenter la ligne `op.drop_table('spatial_ref_sys')`.

```python
# spatial_ref_sys est une table système PostGIS - ne pas supprimer
# op.drop_table('spatial_ref_sys')
```

**⚠️ Index geometry auto-créé :** GeoAlchemy2 crée automatiquement un index GIST sur les colonnes `Geometry`. Supprimer la ligne `op.create_index('idx_territoire_geometry', ...)` si présente.

```python
# Index geometry créé automatiquement par GeoAlchemy2
# op.create_index('idx_territoire_geometry', 'territoire', ['geometry'], ...)
```

### 4.3. Application de la migration

```bash
cd src/database
alembic upgrade head
```

**Sortie :**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 7b72b070fd66, initial_schema
```

### 4.4. Vérification des tables créées

```bash
docker exec electio_postgres psql -U admin -d electio_analytics -c "\dt"
```

**Tables créées :**
```
 Schema |      Name       | Type  | Owner
--------+-----------------+-------+-------
 public | alembic_version | table | admin
 public | election_result | table | admin
 public | indicateur      | table | admin
 public | prediction      | table | admin
 public | territoire      | table | admin
 public | type_indicateur | table | admin
```

### 4.5. Vérification structure table

```bash
docker exec electio_postgres psql -U admin -d electio_analytics -c "\d territoire"
```

**Détails :**
- **Colonnes :** id_territoire, code_insee, type_territoire, nom_territoire, geometry (PostGIS), population, metadata (JSONB)
- **Index :** PK btree, idx_territoire_geometry (GIST auto), idx_territoire_insee, idx_territoire_type
- **Contraintes :** CHECK sur type_territoire et population
- **Relations :** FK vers election_result, indicateur, prediction

---

## 5. Commandes Alembic

### 5.1. Workflow standard

```bash
# Se placer dans le répertoire database
cd src/database

# 1. Modifier les modèles ORM dans src/database/models/

# 2. Générer une nouvelle migration
alembic revision --autogenerate -m "description_changement"

# 3. Vérifier le fichier généré dans migrations/versions/

# 4. Appliquer la migration
alembic upgrade head

# 5. Vérifier le statut
alembic current
```

### 5.2. Commandes principales

| Commande | Description |
|----------|-------------|
| `alembic current` | Afficher la version actuelle |
| `alembic history` | Historique des migrations |
| `alembic upgrade head` | Appliquer toutes les migrations |
| `alembic upgrade +1` | Appliquer la prochaine migration |
| `alembic downgrade -1` | Annuler la dernière migration |
| `alembic downgrade base` | Revenir à la base vide |
| `alembic revision -m "msg"` | Créer migration vide |
| `alembic revision --autogenerate -m "msg"` | Générer migration auto |
| `alembic show <revision>` | Détails d'une révision |

### 5.3. Commandes avancées

```bash
# Générer SQL sans exécuter (dry-run)
alembic upgrade head --sql

# Créer migration sans détection automatique
alembic revision -m "manual_migration"

# Downgrade vers une révision spécifique
alembic downgrade 7b72b070fd66

# Historique avec détails
alembic history --verbose

# Marquer comme appliquée sans exécuter
alembic stamp head
```

---

## 6. Troubleshooting

### 6.1. Erreur : "password authentication failed"

**Cause :** Fichier `.env` non chargé ou mot de passe incorrect.

**Solution :**
```python
# Vérifier config.py charge bien dotenv
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
```

### 6.2. Erreur : "relation already exists"

**Cause :** Migration partiellement appliquée ou état incohérent.

**Solution :**
```bash
# Nettoyer le schéma public
docker exec electio_postgres psql -U admin -d electio_analytics -c \
  "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Réinstaller extensions
docker exec electio_postgres psql -U admin -d electio_analytics -c \
  "CREATE EXTENSION postgis; CREATE EXTENSION \"uuid-ossp\"; CREATE EXTENSION btree_gin;"

# Réappliquer migration
cd src/database && alembic upgrade head
```

### 6.3. Erreur : "geoalchemy2 is not defined"

**Cause :** Import manquant dans le fichier de migration.

**Solution :**
```python
# Ajouter dans migrations/versions/*.py
import geoalchemy2
```

### 6.4. Erreur : "cannot drop table spatial_ref_sys"

**Cause :** Migration essaie de supprimer une table système PostGIS.

**Solution :**
```python
# Commenter dans la fonction upgrade()
# op.drop_table('spatial_ref_sys')
```

### 6.5. Redémarrage complet PostgreSQL

```bash
# Arrêter et supprimer conteneur + volumes
docker-compose down -v

# Supprimer volume de données
docker volume rm epsi_m1_mspr-groupe_ryms_postgres_data

# Redémarrer
docker-compose up -d

# Attendre 10s puis appliquer migration
sleep 10
cd src/database && alembic upgrade head
```

---

## 7. Bonnes pratiques

### 7.1. Avant chaque migration

- ✅ Lire les modèles ORM modifiés
- ✅ Vérifier que PostgreSQL est démarré
- ✅ Tester en environnement local avant production
- ✅ Commiter le fichier de migration dans Git

### 7.2. Nommage des migrations

**Format :** `YYYYMMDD_HHMM_<revision>_<slug>`

**Exemples :**
- `20260211_1129_7b72b070fd66_initial_schema`
- `20260215_1430_a1b2c3d4_add_column_x`
- `20260220_0900_e5f6g7h8_create_index_y`

### 7.3. Révision manuelle systématique

**Toujours vérifier le fichier généré avant `upgrade` :**
- Import `geoalchemy2` si colonnes Geometry
- Pas de drop sur tables système PostGIS
- Pas de duplication d'index auto-créés (GeoAlchemy2)
- Contraintes CHECK correctes
- Relations FK cohérentes

---

## 8. Références

- **Alembic Documentation :** https://alembic.sqlalchemy.org/
- **SQLAlchemy ORM :** https://docs.sqlalchemy.org/
- **GeoAlchemy2 :** https://geoalchemy-2.readthedocs.io/
- **PostGIS :** https://postgis.net/documentation/

---

**Dernière mise à jour :** 2026-02-11
**Auteur :** @tech (Claude Sonnet 4.5)
