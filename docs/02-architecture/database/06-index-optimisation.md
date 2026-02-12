# Index et Optimisation

> **OBSOLETE** : Ce document decrit le schema v2.0 (5 tables). Le schema actuel est v3.0 (17 tables).
> Voir [MLD v3.0](02-mld.md) pour les index a jour.

**Version :** 2.0 (OBSOLETE - schema v3.0 deploye)
**Date :** 2026-02-10
**Auteur :** @tech
**Statut :** Archive

---

## Vue d'Ensemble

Le schéma v2.0 implémente **18 indexes** pour optimiser :
- **Requêtes ML** (jointures multi-tables)
- **Filtrage géographique** (PostGIS spatial)
- **Recherche JSONB** (métadonnées)
- **Contraintes d'intégrité** (PK, UK, FK)

---

## 1. Index par Table

### Table : `territoire` (4 indexes)

#### IDX-01 : Clé Primaire (Automatique)
```sql
CREATE UNIQUE INDEX territoire_pkey ON territoire (id_territoire);
```
- **Type :** B-Tree
- **Colonnes :** `id_territoire`
- **Usage :** Jointures FK (PRIMARY KEY)
- **Taille estimée :** <1 KB (130 lignes)

---

#### IDX-02 : Code INSEE
```sql
CREATE INDEX idx_territoire_insee ON territoire (code_insee);
```
- **Type :** B-Tree
- **Colonnes :** `code_insee`
- **Usage :** Recherche par commune
- **Cardinalité :** Faible (~1-130 valeurs)
- **Sélectivité :** Moyenne (plusieurs territoires par commune)

**Requête optimisée :**
```sql
-- Lister tous les territoires de Bordeaux
SELECT * FROM territoire WHERE code_insee = '33063';
-- Index Scan using idx_territoire_insee
```

---

#### IDX-03 : Type Territoire
```sql
CREATE INDEX idx_territoire_type ON territoire (type_territoire);
```
- **Type :** B-Tree
- **Colonnes :** `type_territoire`
- **Usage :** Filtrage par type (IRIS, BUREAU_VOTE, etc.)
- **Cardinalité :** Très faible (4 valeurs)
- **Sélectivité :** Faible

**Requête optimisée :**
```sql
-- Lister tous les IRIS
SELECT * FROM territoire WHERE type_territoire = 'IRIS';
-- Index Scan using idx_territoire_type
```

---

#### IDX-04 : Géométrie Spatiale (PostGIS)
```sql
CREATE INDEX idx_territoire_geometry ON territoire USING GIST (geometry);
```
- **Type :** GiST (Generalized Search Tree)
- **Colonnes :** `geometry`
- **Usage :** Requêtes spatiales (intersection, contenance, distance)
- **Extension :** PostGIS

**Requêtes optimisées :**
```sql
-- Trouver territoires contenant un point GPS
SELECT * FROM territoire
WHERE ST_Contains(geometry, ST_SetSRID(ST_MakePoint(-0.5805, 44.8378), 4326));
-- Index Scan using idx_territoire_geometry

-- Territoires dans un rayon de 5km
SELECT * FROM territoire
WHERE ST_DWithin(geometry::geography, ST_SetSRID(ST_MakePoint(-0.5805, 44.8378), 4326)::geography, 5000);
-- Index Scan using idx_territoire_geometry
```

---

### Table : `type_indicateur` (3 indexes)

#### IDX-05 : Clé Primaire (Automatique)
```sql
CREATE UNIQUE INDEX type_indicateur_pkey ON type_indicateur (id_type);
```
- **Type :** B-Tree
- **Colonnes :** `id_type`
- **Usage :** Jointures FK
- **Taille estimée :** <1 KB (50 lignes)

---

#### IDX-06 : Code Type (Contrainte UNIQUE)
```sql
CREATE UNIQUE INDEX idx_type_indicateur_code ON type_indicateur (code_type);
```
- **Type :** B-Tree
- **Colonnes :** `code_type`
- **Usage :** Recherche par code (UNIQUE constraint)
- **Cardinalité :** Élevée (50 valeurs uniques)
- **Sélectivité :** Très élevée (1 ligne par code)

**Requête optimisée :**
```sql
-- Récupérer un type par code
SELECT * FROM type_indicateur WHERE code_type = 'SECURITE_CAMBRIOLAGES';
-- Index Scan using idx_type_indicateur_code
```

---

#### IDX-07 : Catégorie
```sql
CREATE INDEX idx_type_indicateur_categorie ON type_indicateur (categorie);
```
- **Type :** B-Tree
- **Colonnes :** `categorie`
- **Usage :** Filtrage par catégorie (SECURITE, EMPLOI, etc.)
- **Cardinalité :** Faible (~10 valeurs)
- **Sélectivité :** Faible

**Requête optimisée :**
```sql
-- Lister tous les types de sécurité
SELECT * FROM type_indicateur WHERE categorie = 'SECURITE';
-- Index Scan using idx_type_indicateur_categorie
```

---

### Table : `indicateur` (6 indexes)

#### IDX-08 : Clé Primaire (Automatique)
```sql
CREATE UNIQUE INDEX indicateur_pkey ON indicateur (id_indicateur);
```
- **Type :** B-Tree
- **Colonnes :** `id_indicateur`
- **Usage :** Jointures FK
- **Taille estimée :** ~500 KB (15 000 lignes)

---

#### IDX-09 : Territoire (FK)
```sql
CREATE INDEX idx_indicateur_territoire ON indicateur (id_territoire);
```
- **Type :** B-Tree
- **Colonnes :** `id_territoire`
- **Usage :** Jointures avec `territoire`
- **Cardinalité :** Moyenne (130 territoires)
- **Sélectivité :** Moyenne (~115 lignes/territoire)

**Requête optimisée :**
```sql
-- Tous les indicateurs de Bordeaux
SELECT * FROM indicateur WHERE id_territoire = '33063';
-- Index Scan using idx_indicateur_territoire
```

---

#### IDX-10 : Type (FK)
```sql
CREATE INDEX idx_indicateur_type ON indicateur (id_type);
```
- **Type :** B-Tree
- **Colonnes :** `id_type`
- **Usage :** Jointures avec `type_indicateur`
- **Cardinalité :** Faible (50 types)
- **Sélectivité :** Faible (~300 lignes/type)

**Requête optimisée :**
```sql
-- Tous les indicateurs de type "cambriolages"
SELECT * FROM indicateur WHERE id_type = 1;
-- Index Scan using idx_indicateur_type
```

---

#### IDX-11 : Année
```sql
CREATE INDEX idx_indicateur_annee ON indicateur (annee);
```
- **Type :** B-Tree
- **Colonnes :** `annee`
- **Usage :** Filtrage temporel
- **Cardinalité :** Faible (~6 années)
- **Sélectivité :** Faible (~2500 lignes/année)

**Requête optimisée :**
```sql
-- Indicateurs 2022
SELECT * FROM indicateur WHERE annee = 2022;
-- Index Scan using idx_indicateur_annee
```

---

#### IDX-12 : Index Composite ML
```sql
CREATE INDEX idx_indicateur_composite ON indicateur (id_territoire, id_type, annee);
```
- **Type :** B-Tree Composite
- **Colonnes :** `(id_territoire, id_type, annee)`
- **Usage :** Requêtes ML complexes (jointures multi-critères)
- **Cardinalité :** Élevée (combinaison unique)
- **Sélectivité :** Très élevée

**Requêtes optimisées :**
```sql
-- Requête ML typique : 1 territoire, 1 type, 1 année
SELECT valeur_numerique FROM indicateur
WHERE id_territoire = '33063' AND id_type = 1 AND annee = 2022;
-- Index Scan using idx_indicateur_composite

-- Jointure optimisée (covering index partiel)
SELECT t.nom_territoire, i.valeur_numerique
FROM indicateur i
JOIN territoire t USING (id_territoire)
WHERE i.id_territoire = '33063' AND i.id_type = 1 AND i.annee BETWEEN 2017 AND 2022;
-- Index Scan using idx_indicateur_composite + territoire_pkey
```

**Avantages :**
- ✅ Réduit lectures disque (skip scan optimisé)
- ✅ Couvre les 3 colonnes les plus filtrées
- ✅ Ordre optimal (territoire > type > année)

---

#### IDX-13 : Métadonnées JSONB
```sql
CREATE INDEX idx_indicateur_metadata ON indicateur USING GIN (metadata);
```
- **Type :** GIN (Generalized Inverted Index)
- **Colonnes :** `metadata`
- **Usage :** Recherche dans métadonnées JSONB
- **Cardinalité :** Très élevée (valeurs variables)

**Requêtes optimisées :**
```sql
-- Recherche clé JSONB
SELECT * FROM indicateur WHERE metadata ? 'taux_pour_1000_hab';
-- Bitmap Index Scan on idx_indicateur_metadata

-- Recherche valeur JSONB
SELECT * FROM indicateur WHERE metadata @> '{"evolution_n_1": -5.2}';
-- Bitmap Index Scan on idx_indicateur_metadata

-- Extraction valeur
SELECT metadata->>'taux_pour_1000_hab' AS taux
FROM indicateur WHERE metadata->>'taux_pour_1000_hab' IS NOT NULL;
-- Bitmap Index Scan on idx_indicateur_metadata
```

---

#### IDX-14 : Contrainte UNIQUE Composite
```sql
CREATE UNIQUE INDEX uk_indicateur_unique ON indicateur (id_territoire, id_type, annee, periode);
```
- **Type :** B-Tree Composite
- **Colonnes :** `(id_territoire, id_type, annee, periode)`
- **Usage :** Contrainte d'unicité (RG-02)
- **Sélectivité :** Très élevée (combinaison unique)

---

### Table : `election_result` (5 indexes)

#### IDX-15 : Clé Primaire (Automatique)
```sql
CREATE UNIQUE INDEX election_result_pkey ON election_result (id_result);
```
- **Type :** B-Tree
- **Colonnes :** `id_result`
- **Usage :** Jointures FK
- **Taille estimée :** ~200 KB (6 500 lignes)

---

#### IDX-16 : Territoire (FK)
```sql
CREATE INDEX idx_election_territoire ON election_result (id_territoire);
```
- **Type :** B-Tree
- **Colonnes :** `id_territoire`
- **Usage :** Jointures avec `territoire`
- **Cardinalité :** Moyenne (130 territoires)
- **Sélectivité :** Moyenne (~50 lignes/territoire)

---

#### IDX-17 : Année et Tour
```sql
CREATE INDEX idx_election_annee_tour ON election_result (annee, tour);
```
- **Type :** B-Tree Composite
- **Colonnes :** `(annee, tour)`
- **Usage :** Filtrage électoral (ex: "Tous candidats 2022 tour 1")
- **Cardinalité :** Faible (4 combinaisons : 2017/T1, 2017/T2, 2022/T1, 2022/T2)
- **Sélectivité :** Faible (~1625 lignes/combinaison)

**Requête optimisée :**
```sql
-- Résultats 2022 tour 1
SELECT * FROM election_result WHERE annee = 2022 AND tour = 1;
-- Index Scan using idx_election_annee_tour
```

---

#### IDX-18 : Candidat
```sql
CREATE INDEX idx_election_candidat ON election_result (candidat);
```
- **Type :** B-Tree
- **Colonnes :** `candidat`
- **Usage :** Recherche par candidat (ex: "Emmanuel MACRON sur tous bureaux")
- **Cardinalité :** Faible (~15 candidats)
- **Sélectivité :** Faible (~430 lignes/candidat)

**Requête optimisée :**
```sql
-- Tous résultats de Macron
SELECT * FROM election_result WHERE candidat = 'Emmanuel MACRON';
-- Index Scan using idx_election_candidat
```

---

#### IDX-19 : Index Composite ML
```sql
CREATE INDEX idx_election_composite ON election_result (id_territoire, annee, tour);
```
- **Type :** B-Tree Composite
- **Colonnes :** `(id_territoire, annee, tour)`
- **Usage :** Requêtes ML (jointure avec indicateurs)
- **Cardinalité :** Élevée
- **Sélectivité :** Très élevée

**Requête optimisée :**
```sql
-- Jointure ML : Résultats + Indicateurs pour 1 territoire, 1 année, 1 tour
SELECT
    e.candidat,
    e.pourcentage_voix,
    i.valeur_numerique AS indicateur_valeur
FROM election_result e
JOIN indicateur i ON e.id_territoire = i.id_territoire AND e.annee = i.annee
WHERE e.id_territoire = '33063' AND e.annee = 2022 AND e.tour = 1;
-- Index Scan using idx_election_composite + idx_indicateur_composite
```

---

#### IDX-20 : Contrainte UNIQUE Composite
```sql
CREATE UNIQUE INDEX uk_election_result_unique ON election_result (id_territoire, annee, tour, candidat);
```
- **Type :** B-Tree Composite
- **Colonnes :** `(id_territoire, annee, tour, candidat)`
- **Usage :** Contrainte d'unicité (RG-02)
- **Sélectivité :** Très élevée (combinaison unique)

---

### Table : `prediction` (4 indexes)

#### IDX-21 : Clé Primaire (Automatique)
```sql
CREATE UNIQUE INDEX prediction_pkey ON prediction (id_prediction);
```
- **Type :** B-Tree
- **Colonnes :** `id_prediction`
- **Usage :** Jointures FK
- **Taille estimée :** ~100 KB (2 600 lignes)

---

#### IDX-22 : Territoire (FK)
```sql
CREATE INDEX idx_prediction_territoire ON prediction (id_territoire);
```
- **Type :** B-Tree
- **Colonnes :** `id_territoire`
- **Usage :** Jointures avec `territoire`
- **Cardinalité :** Moyenne (130 territoires)
- **Sélectivité :** Moyenne (~20 lignes/territoire)

---

#### IDX-23 : Année Prédiction
```sql
CREATE INDEX idx_prediction_annee ON prediction (annee_prediction);
```
- **Type :** B-Tree
- **Colonnes :** `annee_prediction`
- **Usage :** Filtrage par année prédite
- **Cardinalité :** Faible (1-5 années)
- **Sélectivité :** Faible (~520 lignes/année)

**Requête optimisée :**
```sql
-- Toutes prédictions 2027
SELECT * FROM prediction WHERE annee_prediction = 2027;
-- Index Scan using idx_prediction_annee
```

---

#### IDX-24 : Modèle Utilisé
```sql
CREATE INDEX idx_prediction_modele ON prediction (modele_utilise);
```
- **Type :** B-Tree
- **Colonnes :** `modele_utilise`
- **Usage :** Filtrage par modèle ML
- **Cardinalité :** Faible (5-10 modèles)
- **Sélectivité :** Faible (~260 lignes/modèle)

**Requête optimisée :**
```sql
-- Prédictions RandomForest
SELECT * FROM prediction WHERE modele_utilise = 'RandomForest';
-- Index Scan using idx_prediction_modele
```

---

#### IDX-25 : Contrainte UNIQUE Composite
```sql
CREATE UNIQUE INDEX uk_prediction_unique ON prediction (id_territoire, candidat, tour, annee_prediction, version_modele);
```
- **Type :** B-Tree Composite
- **Colonnes :** `(id_territoire, candidat, tour, annee_prediction, version_modele)`
- **Usage :** Contrainte d'unicité (versioning prédictions)
- **Sélectivité :** Très élevée (combinaison unique)

---

## 2. Récapitulatif des Index

### Par Type d'Index

| Type | Nombre | Usage Principal |
|------|--------|-----------------|
| **B-Tree Simple** | 13 | Recherche égalité, jointures FK |
| **B-Tree Composite** | 8 | Requêtes multi-critères, contraintes UNIQUE |
| **GIN (JSONB)** | 1 | Recherche dans métadonnées |
| **GiST (Spatial)** | 1 | Requêtes géographiques PostGIS |
| **TOTAL** | **23** | (18 fonctionnels + 5 PK automatiques) |

### Par Table

| Table | Nombre Index | Taille Estimée |
|-------|--------------|----------------|
| `territoire` | 4 | ~5 KB |
| `type_indicateur` | 3 | ~2 KB |
| `indicateur` | 6 | ~800 KB |
| `election_result` | 5 | ~400 KB |
| `prediction` | 4 | ~200 KB |
| **TOTAL** | **22** | **~1.4 MB** |

---

## 3. Stratégies d'Optimisation

### 3.1 Index Composites

**Principe :** Créer index multi-colonnes pour requêtes fréquentes

**Règle d'ordre des colonnes :**
1. **Égalité (=)** : Colonnes avec filtre égalité en premier
2. **Range (BETWEEN, >, <)** : Colonnes avec range en dernier
3. **Cardinalité** : Colonnes haute cardinalité avant faible cardinalité

**Exemple :**
```sql
-- ✅ BON : égalité (territoire, type) puis range (annee)
CREATE INDEX idx_indicateur_composite ON indicateur (id_territoire, id_type, annee);

-- ❌ MAUVAIS : range en premier
CREATE INDEX idx_mauvais ON indicateur (annee, id_territoire, id_type);
```

**Requêtes optimisées :**
- `WHERE id_territoire = X AND id_type = Y` → Index Scan
- `WHERE id_territoire = X AND id_type = Y AND annee = Z` → Index Scan
- `WHERE id_territoire = X AND id_type = Y AND annee BETWEEN A AND B` → Index Scan

---

### 3.2 Index GIN sur JSONB

**Usage :** Recherche dans métadonnées variables

**Opérateurs supportés :**
| Opérateur | Description | Exemple |
|-----------|-------------|---------|
| `?` | Clé existe | `metadata ? 'taux_pour_1000_hab'` |
| `?&` | Toutes clés existent | `metadata ?& ARRAY['key1', 'key2']` |
| `?\|` | Au moins une clé existe | `metadata ?\| ARRAY['key1', 'key2']` |
| `@>` | Contient JSON | `metadata @> '{"key": "value"}'` |
| `<@` | Contenu dans JSON | `'{"key": "value"}' <@ metadata` |

**Exemple :**
```sql
-- Indicateurs avec taux normalisé
SELECT * FROM indicateur WHERE metadata @> '{"taux_pour_1000_hab": 2.0}';
-- Bitmap Index Scan on idx_indicateur_metadata
```

---

### 3.3 Index Spatial (GiST)

**Usage :** Requêtes géographiques PostGIS

**Fonctions optimisées :**
- `ST_Contains(geometry, point)` : Point dans polygone
- `ST_Intersects(geometry1, geometry2)` : Intersection
- `ST_DWithin(geography1, geography2, distance)` : Distance
- `ST_Distance(geometry1, geometry2)` : Calcul distance

**Exemple :**
```sql
-- Territoires contenant un point GPS
SELECT nom_territoire FROM territoire
WHERE ST_Contains(geometry, ST_SetSRID(ST_MakePoint(-0.5805, 44.8378), 4326));
-- Index Scan using idx_territoire_geometry
```

---

### 3.4 Covering Index (Future)

**Principe :** Index contient toutes colonnes nécessaires (pas de lecture table)

**Exemple v3.0 :**
```sql
CREATE INDEX idx_indicateur_covering ON indicateur (id_territoire, id_type, annee)
    INCLUDE (valeur_numerique, fiabilite);

-- Requête couverte par l'index (Index-Only Scan)
SELECT valeur_numerique FROM indicateur
WHERE id_territoire = '33063' AND id_type = 1 AND annee = 2022;
-- Index-Only Scan using idx_indicateur_covering
```

---

### 3.5 Partitioning (Future >10M lignes)

**Principe :** Diviser tables en partitions (par année, type, etc.)

**Exemple v3.0 :**
```sql
-- Partitionner election_result par année
CREATE TABLE election_result (
    -- colonnes...
) PARTITION BY RANGE (annee);

CREATE TABLE election_result_2017 PARTITION OF election_result
    FOR VALUES FROM (2017) TO (2018);

CREATE TABLE election_result_2022 PARTITION OF election_result
    FOR VALUES FROM (2022) TO (2023);
```

**Avantages :**
- ✅ Requêtes plus rapides (scan 1 partition vs toute table)
- ✅ Maintenance facilitée (VACUUM par partition)
- ✅ Archivage simple (DROP partition ancienne)

---

## 4. Analyse de Performance

### 4.1 Plans d'Exécution

**Commande :** `EXPLAIN ANALYZE`
```sql
EXPLAIN ANALYZE
SELECT * FROM indicateur WHERE id_territoire = '33063' AND annee = 2022;
```

**Résultat attendu :**
```
Index Scan using idx_indicateur_composite on indicateur (cost=0.29..8.31 rows=1 width=...)
  Index Cond: ((id_territoire = '33063') AND (annee = 2022))
  Planning Time: 0.123 ms
  Execution Time: 0.045 ms
```

**Métriques clés :**
- **Index Scan** : Utilise index (✅ bon)
- **Seq Scan** : Scan complet table (❌ mauvais si table volumineuse)
- **Execution Time** : Temps réel
- **rows** : Nombre lignes estimées

---

### 4.2 Statistiques Requêtes

**Extension :** `pg_stat_statements`
```sql
CREATE EXTENSION pg_stat_statements;

-- Top 10 requêtes lentes
SELECT
    query,
    calls,
    total_exec_time / 1000 AS total_sec,
    mean_exec_time / 1000 AS mean_sec
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

### 4.3 Maintenance Index

#### Rebuild Index (Fragmentation)
```sql
REINDEX INDEX idx_indicateur_composite;
```

#### Statistiques à jour
```sql
ANALYZE indicateur;
```

#### Vacuum régulier
```sql
VACUUM ANALYZE indicateur;
```

---

## 5. Benchmarks PostgreSQL 15 (SSD)

### Volumétrie POC Bordeaux (~24 300 lignes)

| Requête | Temps (ms) | Index Utilisé | Commentaire |
|---------|------------|---------------|-------------|
| `SELECT * FROM territoire LIMIT 10` | <1 | `territoire_pkey` | Lecture simple |
| `SELECT * FROM indicateur WHERE id_territoire = '33063'` | 2-5 | `idx_indicateur_territoire` | ~115 lignes |
| `SELECT * FROM election_result WHERE annee = 2022 AND tour = 1` | 3-8 | `idx_election_annee_tour` | ~1600 lignes |
| `JOIN election_result + indicateur (1000 lignes)` | 5-10 | Index composites | Jointure optimisée |
| `Requête ML complète (v_dataset_ml)` | 50-100 | Vue pré-calculée | 6 tables jointes |
| `INSERT bulk indicateur (1000 lignes)` | 200-300 | - | Avec validation contraintes |
| `Recherche JSONB metadata @> '{...}'` | 10-20 | `idx_indicateur_metadata` | Index GIN |
| `ST_Contains(geometry, point)` | 5-15 | `idx_territoire_geometry` | Requête spatiale |

### Recommandations

| Métrique | Seuil Acceptable | Seuil Critique | Action si Dépassé |
|----------|------------------|----------------|-------------------|
| **Temps requête SELECT** | <50 ms | >500 ms | Ajouter index, analyser plan |
| **Temps requête JOIN** | <100 ms | >1000 ms | Index composites, vues matérialisées |
| **Temps INSERT bulk** | <500 ms/1000 lignes | >5000 ms | Désactiver temporairement triggers |
| **Taille index** | <10% taille table | >50% taille table | Évaluer pertinence index |

---

## 6. Recommandations Production

### 6.1 Monitoring Continu

**Extension :** `pg_stat_statements`
```sql
-- Activer
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
```

**Dashboard Grafana :**
- Temps moyen requêtes
- Nombre index scans vs seq scans
- Cache hit ratio (>95%)

---

### 6.2 Maintenance Automatisée

**Autovacuum :**
```sql
autovacuum = on
autovacuum_naptime = 1min
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
```

**Cron quotidien :**
```bash
# 03h00 : Vacuum et analyse
0 3 * * * psql -d electio_analytics -c "VACUUM ANALYZE;"
```

---

### 6.3 Backup et Restauration

**Dump quotidien :**
```bash
pg_dump -U admin -d electio_analytics -Fc -f backup_$(date +%Y%m%d).dump
```

**Archivage WAL :**
```sql
wal_level = replica
archive_mode = on
archive_command = 'cp %p /mnt/backup/wal/%f'
```

---

**Prochaine étape :** Consulter [Volumétrie et Performance](07-volumetrie-performance.md) pour estimations détaillées.
