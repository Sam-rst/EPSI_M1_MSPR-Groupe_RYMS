# Évolutions Futures

**Version :** 2.0 → 3.0
**Date :** 2026-02-10
**Auteur :** @tech
**Statut :** Roadmap

---

## Vue d'Ensemble

Ce document présente la roadmap des évolutions du schéma de base de données pour la version 3.0 et au-delà. Les fonctionnalités sont classées par priorité et complexité.

**Objectifs v3.0 :**
- Améliorer la traçabilité et l'audit
- Supporter des hiérarchies géographiques explicites
- Optimiser les performances pour volumétries >1M lignes
- Étendre à d'autres types d'élections (législatives, municipales)

---

## 1. Fonctionnalités Planifiées

### Tableau Récapitulatif

| # | Fonctionnalité | Priorité | Complexité | Effort (j/h) | Version Cible |
|---|----------------|----------|------------|--------------|---------------|
| 1 | [Hiérarchie géographique explicite](#11-hiérarchie-géographique-explicite) | ⭐⭐⭐ | Moyenne | 3j | v3.0 |
| 2 | [Historisation prédictions](#12-historisation-prédictions) | ⭐⭐ | Faible | 1j | v3.0 |
| 3 | [Indicateurs dérivés calculés](#13-indicateurs-dérivés-calculés) | ⭐⭐⭐ | Élevée | 5j | v3.0 |
| 4 | [Support multi-élections](#14-support-multi-élections) | ⭐⭐ | Moyenne | 3j | v3.0 |
| 5 | [Audit trail complet](#15-audit-trail-complet) | ⭐ | Faible | 2j | v3.1 |
| 6 | [Partitioning par année](#16-partitioning-par-année) | ⭐ | Moyenne | 2j | v3.1 |
| 7 | [Full-Text Search](#17-full-text-search) | ⭐ | Faible | 1j | v3.1 |
| 8 | [Permissions granulaires](#18-permissions-granulaires) | ⭐⭐ | Moyenne | 3j | v3.2 |
| 9 | [Agrégation temps réel](#19-agrégation-temps-réel) | ⭐ | Moyenne | 2j | v3.2 |
| 10 | [API GraphQL native](#110-api-graphql-native) | ⭐ | Élevée | 5j | v4.0 |

**Légende Priorité :**
- ⭐⭐⭐ : Critique (bloquant pour production)
- ⭐⭐ : Importante (améliore fortement l'usage)
- ⭐ : Nice-to-have (confort, non bloquant)

**Légende Complexité :**
- **Faible :** Ajout colonnes, indexes, vues simples
- **Moyenne :** Nouvelles tables, triggers, migrations complexes
- **Élevée :** Refonte architecture, logique métier lourde

---

## 1.1 Hiérarchie Géographique Explicite

### Problème Actuel
La hiérarchie `BUREAU_VOTE → IRIS → COMMUNE` est implicite (via `code_insee`). Impossible d'agréger facilement les résultats d'un IRIS vers sa commune parente.

### Solution v3.0
Ajouter colonne `id_territoire_parent` pour créer une arborescence explicite.

#### Migration SQL
```sql
-- Étape 1 : Ajouter colonne parent
ALTER TABLE territoire ADD COLUMN id_territoire_parent VARCHAR(20);

-- Étape 2 : Contrainte référentielle (self-join)
ALTER TABLE territoire
    ADD CONSTRAINT fk_territoire_parent
    FOREIGN KEY (id_territoire_parent) REFERENCES territoire(id_territoire)
    ON DELETE RESTRICT;

-- Étape 3 : Peupler hiérarchie
UPDATE territoire SET id_territoire_parent = code_insee
WHERE type_territoire IN ('IRIS', 'BUREAU_VOTE', 'ARRONDISSEMENT');

-- Étape 4 : Index pour requêtes récursives
CREATE INDEX idx_territoire_parent ON territoire (id_territoire_parent);
```

#### Exemples de Hiérarchie
```
33063 (COMMUNE Bordeaux) ← racine (parent = NULL)
  ├── IRIS_330630101 (parent = 33063)
  │   ├── BV_33063_001 (parent = IRIS_330630101)
  │   └── BV_33063_002 (parent = IRIS_330630101)
  └── IRIS_330630102 (parent = 33063)
      └── BV_33063_003 (parent = IRIS_330630102)
```

#### Requêtes Optimisées

**Agréger résultats IRIS → Commune :**
```sql
WITH RECURSIVE hierarchie AS (
    -- Bureaux de vote
    SELECT id_territoire, id_territoire_parent, nom_territoire, 1 AS niveau
    FROM territoire WHERE type_territoire = 'BUREAU_VOTE'

    UNION ALL

    -- Remontée récursive
    SELECT t.id_territoire, t.id_territoire_parent, t.nom_territoire, h.niveau + 1
    FROM territoire t
    JOIN hierarchie h ON t.id_territoire = h.id_territoire_parent
)
SELECT
    h.id_territoire AS commune,
    SUM(e.nombre_voix) AS total_voix_commune
FROM hierarchie h
JOIN election_result e ON h.id_territoire = e.id_territoire
WHERE h.niveau = (SELECT MAX(niveau) FROM hierarchie)
GROUP BY h.id_territoire;
```

**Lister descendants d'un territoire :**
```sql
WITH RECURSIVE descendants AS (
    -- Point de départ
    SELECT id_territoire FROM territoire WHERE id_territoire = '33063'

    UNION ALL

    -- Enfants récursifs
    SELECT t.id_territoire
    FROM territoire t
    JOIN descendants d ON t.id_territoire_parent = d.id_territoire
)
SELECT * FROM descendants;
```

### Bénéfices
- ✅ Agrégations géographiques simplifiées
- ✅ Requêtes récursives optimisées (WITH RECURSIVE)
- ✅ Validation hiérarchie via contrainte FK

### Risques
- ⚠️ Migration complexe (recalcul hiérarchie pour données existantes)
- ⚠️ Performance requêtes récursives (limiter profondeur)

---

## 1.2 Historisation Prédictions

### Problème Actuel
Pas de traçabilité des modifications de prédictions. Si un modèle est retrain et génère de nouvelles prédictions, les anciennes sont perdues.

### Solution v3.0
Créer table `prediction_history` pour versioning complet.

#### Nouvelle Table
```sql
CREATE TABLE prediction_history (
    id_history              BIGSERIAL       PRIMARY KEY,
    id_prediction           BIGINT          NOT NULL,  -- Référence prediction
    version_modele          VARCHAR(20)     NOT NULL,
    pourcentage_predit      DECIMAL(5,2)    NOT NULL,
    intervalle_confiance_inf DECIMAL(5,2),
    intervalle_confiance_sup DECIMAL(5,2),
    metriques_modele        JSONB,
    features_utilisees      JSONB,
    date_generation         TIMESTAMP       NOT NULL,
    date_archivage          TIMESTAMP       DEFAULT NOW(),

    FOREIGN KEY (id_prediction) REFERENCES prediction(id_prediction)
        ON DELETE CASCADE
);

CREATE INDEX idx_prediction_history_id ON prediction_history (id_prediction);
CREATE INDEX idx_prediction_history_version ON prediction_history (version_modele);
```

#### Trigger d'Archivage Automatique
```sql
CREATE OR REPLACE FUNCTION archive_prediction()
RETURNS TRIGGER AS $$
BEGIN
    -- Archiver ancienne version avant UPDATE
    INSERT INTO prediction_history (
        id_prediction, version_modele, pourcentage_predit,
        intervalle_confiance_inf, intervalle_confiance_sup,
        metriques_modele, features_utilisees, date_generation
    )
    VALUES (
        OLD.id_prediction, OLD.version_modele, OLD.pourcentage_predit,
        OLD.intervalle_confiance_inf, OLD.intervalle_confiance_sup,
        OLD.metriques_modele, OLD.features_utilisees, OLD.date_generation
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_archive_prediction
    BEFORE UPDATE ON prediction
    FOR EACH ROW EXECUTE FUNCTION archive_prediction();
```

#### Requêtes

**Comparer prédictions v1.0 vs v2.0 :**
```sql
SELECT
    p.candidat,
    h1.pourcentage_predit AS v1_0_predit,
    h2.pourcentage_predit AS v2_0_predit,
    (h2.pourcentage_predit - h1.pourcentage_predit) AS evolution
FROM prediction p
LEFT JOIN prediction_history h1 ON p.id_prediction = h1.id_prediction
    AND h1.version_modele = 'v1.0.0'
LEFT JOIN prediction_history h2 ON p.id_prediction = h2.id_prediction
    AND h2.version_modele = 'v2.0.0'
WHERE p.id_territoire = 'IRIS_330630101' AND p.tour = 1;
```

### Bénéfices
- ✅ Traçabilité complète des versions modèles
- ✅ Comparaison A/B entre modèles
- ✅ Audit des modifications

---

## 1.3 Indicateurs Dérivés Calculés

### Problème Actuel
Features ML calculées (ex: évolution temporelle, ratios) sont recalculées à chaque entraînement. Pas de stockage persistant.

### Solution v3.0
Créer table `indicateur_derive` pour stocker features pré-calculées.

#### Nouvelle Table
```sql
CREATE TABLE indicateur_derive (
    id_derive               BIGSERIAL       PRIMARY KEY,
    id_territoire           VARCHAR(20)     NOT NULL,
    code_derive             VARCHAR(50)     NOT NULL,  -- Ex: 'EVOLUTION_CHOMAGE_5ANS'
    annee                   INTEGER         NOT NULL,
    valeur_numerique        DECIMAL(15,4),
    methode_calcul          TEXT,           -- Formule ou description
    depends_on              JSONB,          -- Liste id_indicateur sources
    date_calcul             TIMESTAMP       DEFAULT NOW(),

    FOREIGN KEY (id_territoire) REFERENCES territoire(id_territoire)
        ON DELETE CASCADE,
    UNIQUE (id_territoire, code_derive, annee)
);

CREATE INDEX idx_derive_territoire ON indicateur_derive (id_territoire);
CREATE INDEX idx_derive_code ON indicateur_derive (code_derive);
CREATE INDEX idx_derive_annee ON indicateur_derive (annee);
```

#### Exemples de Dérivés

**Évolution taux chômage 2017 → 2022 :**
```sql
INSERT INTO indicateur_derive (id_territoire, code_derive, annee, valeur_numerique, methode_calcul, depends_on)
SELECT
    i2022.id_territoire,
    'EVOLUTION_CHOMAGE_5ANS',
    2022,
    (i2022.valeur_numerique - i2017.valeur_numerique) AS evolution,
    'chomage_2022 - chomage_2017',
    jsonb_build_array(i2017.id_indicateur, i2022.id_indicateur)
FROM indicateur i2022
JOIN indicateur i2017 ON i2022.id_territoire = i2017.id_territoire
    AND i2017.annee = 2017 AND i2017.id_type = 3  -- Taux chômage
WHERE i2022.annee = 2022 AND i2022.id_type = 3;
```

**Ratio criminalité / population :**
```sql
INSERT INTO indicateur_derive (id_territoire, code_derive, annee, valeur_numerique, methode_calcul)
SELECT
    i_crime.id_territoire,
    'CRIMINALITE_POUR_1000_HAB',
    i_crime.annee,
    (i_crime.valeur_numerique / NULLIF(t.population, 0)) * 1000,
    'crimes / population * 1000'
FROM indicateur i_crime
JOIN territoire t ON i_crime.id_territoire = t.id_territoire
WHERE i_crime.id_type = 1;  -- Cambriolages
```

### Bénéfices
- ✅ Features ML pré-calculées (gain temps entraînement)
- ✅ Traçabilité méthodes de calcul
- ✅ Dépendances explicites (`depends_on`)

### Processus ETL
```python
# Workflow ETL
1. Extraction indicateurs sources
2. Calcul features dérivées (Pandas/NumPy)
3. Insertion dans indicateur_derive
4. Trigger MAJ modèles ML si nouvelles features
```

---

## 1.4 Support Multi-Élections

### Problème Actuel
Table `election_result` dédiée présidentielles. Pas de support législatives, municipales, européennes.

### Solution v3.0
Refactoriser en architecture générique avec table `type_election`.

#### Nouvelles Tables

**Table Catalogue :**
```sql
CREATE TABLE type_election (
    id_type_election        SERIAL          PRIMARY KEY,
    code_type               VARCHAR(30)     NOT NULL UNIQUE,  -- 'PRESIDENTIELLE', 'LEGISLATIVE', etc.
    nom_affichage           VARCHAR(100)    NOT NULL,
    niveau_territorial      VARCHAR(20),     -- 'NATIONAL', 'CIRCONSCRIPTION', 'COMMUNE'
    nombre_tours_max        INTEGER         DEFAULT 2,
    actif                   BOOLEAN         DEFAULT TRUE,
    created_at              TIMESTAMP       DEFAULT NOW()
);

INSERT INTO type_election (code_type, nom_affichage, niveau_territorial, nombre_tours_max) VALUES
    ('PRESIDENTIELLE', 'Présidentielle', 'NATIONAL', 2),
    ('LEGISLATIVE', 'Législatives', 'CIRCONSCRIPTION', 2),
    ('MUNICIPALE', 'Municipales', 'COMMUNE', 2),
    ('EUROPEENNE', 'Européennes', 'NATIONAL', 1),
    ('DEPARTEMENTALE', 'Départementales', 'CANTON', 2);
```

**Table Résultats Refactorisée :**
```sql
CREATE TABLE election_result_v3 (
    id_result               BIGSERIAL       PRIMARY KEY,
    id_type_election        INTEGER         NOT NULL,
    id_territoire           VARCHAR(20)     NOT NULL,
    annee                   INTEGER         NOT NULL,
    tour                    INTEGER         NOT NULL,
    candidat                VARCHAR(100)    NOT NULL,
    parti                   VARCHAR(50),
    nombre_voix             INTEGER         NOT NULL,
    pourcentage_voix        DECIMAL(5,2)    NOT NULL,
    nombre_inscrits         INTEGER         NOT NULL,
    nombre_votants          INTEGER         NOT NULL,
    nombre_exprimes         INTEGER         NOT NULL,
    taux_participation      DECIMAL(5,2)    NOT NULL,
    metadata                JSONB,
    created_at              TIMESTAMP       DEFAULT NOW(),

    FOREIGN KEY (id_type_election) REFERENCES type_election(id_type_election),
    FOREIGN KEY (id_territoire) REFERENCES territoire(id_territoire)
        ON DELETE CASCADE,
    UNIQUE (id_type_election, id_territoire, annee, tour, candidat)
);
```

#### Migration v2 → v3
```sql
-- Peupler type_election
INSERT INTO type_election (id_type_election, code_type, nom_affichage)
VALUES (1, 'PRESIDENTIELLE', 'Présidentielle');

-- Migrer données existantes
INSERT INTO election_result_v3 (
    id_type_election, id_territoire, annee, tour, candidat, parti,
    nombre_voix, pourcentage_voix, nombre_inscrits, nombre_votants,
    nombre_exprimes, taux_participation, metadata, created_at
)
SELECT
    1,  -- PRESIDENTIELLE
    id_territoire, annee, tour, candidat, parti,
    nombre_voix, pourcentage_voix, nombre_inscrits, nombre_votants,
    nombre_exprimes, taux_participation, metadata, created_at
FROM election_result;

-- Renommer tables
DROP TABLE election_result;
ALTER TABLE election_result_v3 RENAME TO election_result;
```

### Bénéfices
- ✅ Architecture extensible (nouvelles élections sans ALTER TABLE)
- ✅ Catalogue centralisé (`type_election`)
- ✅ Comparaisons inter-élections facilitées

---

## 1.5 Audit Trail Complet

### Objectif
Tracer TOUTES modifications (INSERT, UPDATE, DELETE) sur tables critiques.

### Solution v3.1
Trigger générique + table `audit_log`.

#### Table Audit
```sql
CREATE TABLE audit_log (
    id_log                  BIGSERIAL       PRIMARY KEY,
    table_name              VARCHAR(50)     NOT NULL,
    operation               VARCHAR(10)     NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    row_id                  VARCHAR(50)     NOT NULL,  -- PK de la ligne modifiée
    old_values              JSONB,
    new_values              JSONB,
    changed_by              VARCHAR(100),   -- Utilisateur PostgreSQL
    changed_at              TIMESTAMP       DEFAULT NOW()
);

CREATE INDEX idx_audit_table ON audit_log (table_name);
CREATE INDEX idx_audit_operation ON audit_log (operation);
CREATE INDEX idx_audit_changed_at ON audit_log (changed_at);
```

#### Trigger Générique
```sql
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, operation, row_id, old_values, changed_by)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id_territoire::TEXT, row_to_json(OLD), current_user);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, operation, row_id, old_values, new_values, changed_by)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id_territoire::TEXT, row_to_json(OLD), row_to_json(NEW), current_user);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, operation, row_id, new_values, changed_by)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id_territoire::TEXT, row_to_json(NEW), current_user);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Appliquer à toutes tables
CREATE TRIGGER trg_audit_territoire AFTER INSERT OR UPDATE OR DELETE ON territoire
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER trg_audit_indicateur AFTER INSERT OR UPDATE OR DELETE ON indicateur
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
-- ... (répéter pour election_result, prediction, etc.)
```

#### Requêtes

**Historique modifications territoire :**
```sql
SELECT
    operation,
    old_values->>'nom_territoire' AS ancien_nom,
    new_values->>'nom_territoire' AS nouveau_nom,
    changed_by,
    changed_at
FROM audit_log
WHERE table_name = 'territoire' AND row_id = '33063'
ORDER BY changed_at DESC;
```

### Bénéfices
- ✅ Conformité RGPD (traçabilité modifications)
- ✅ Debug (retrouver modifications erronées)
- ✅ Audit sécurité

### Risques
- ⚠️ Volume audit_log important (archivage nécessaire)
- ⚠️ Performance légèrement impactée (trigger synchrone)

---

## 1.6 Partitioning par Année

### Objectif
Optimiser requêtes et maintenance pour volumétries >1M lignes.

### Solution v3.1
Partitionner `election_result` et `indicateur` par `annee`.

#### Exemple Partitioning
```sql
-- Convertir table existante en table partitionnée
CREATE TABLE election_result_partitioned (
    LIKE election_result INCLUDING ALL
) PARTITION BY RANGE (annee);

-- Créer partitions
CREATE TABLE election_result_2017 PARTITION OF election_result_partitioned
    FOR VALUES FROM (2017) TO (2018);

CREATE TABLE election_result_2022 PARTITION OF election_result_partitioned
    FOR VALUES FROM (2022) TO (2023);

CREATE TABLE election_result_2027 PARTITION OF election_result_partitioned
    FOR VALUES FROM (2027) TO (2028);

-- Partition par défaut (futures années)
CREATE TABLE election_result_default PARTITION OF election_result_partitioned
    DEFAULT;

-- Migrer données
INSERT INTO election_result_partitioned SELECT * FROM election_result;

-- Renommer
DROP TABLE election_result;
ALTER TABLE election_result_partitioned RENAME TO election_result;
```

#### Requêtes Optimisées
```sql
-- Scan 1 seule partition (vs toute table)
SELECT * FROM election_result WHERE annee = 2022;
-- Seq Scan on election_result_2022 (partition pruning)
```

### Bénéfices
- ✅ Requêtes filtrées par année jusqu'à 10× plus rapides
- ✅ Maintenance partitionnée (VACUUM par partition)
- ✅ Archivage simplifié (`DROP PARTITION`)

---

## 1.7 Full-Text Search

### Objectif
Recherche textuelle dans `nom_territoire`, `candidat`, `nom_affichage` (type_indicateur).

### Solution v3.1
Index GIN sur colonnes texte avec `tsvector`.

#### Implémentation
```sql
-- Ajouter colonne tsvector
ALTER TABLE territoire ADD COLUMN search_vector tsvector;

-- Peupler index
UPDATE territoire SET search_vector =
    to_tsvector('french', coalesce(nom_territoire, ''));

-- Index GIN
CREATE INDEX idx_territoire_fts ON territoire USING GIN (search_vector);

-- Trigger MAJ automatique
CREATE OR REPLACE FUNCTION territoire_search_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('french', coalesce(NEW.nom_territoire, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_territoire_search
    BEFORE INSERT OR UPDATE ON territoire
    FOR EACH ROW EXECUTE FUNCTION territoire_search_trigger();
```

#### Requêtes
```sql
-- Recherche "Bordeaux Centre"
SELECT nom_territoire FROM territoire
WHERE search_vector @@ to_tsquery('french', 'bordeaux & centre');

-- Recherche floue (similitude)
SELECT nom_territoire, similarity(nom_territoire, 'Bordeux') AS score
FROM territoire
WHERE nom_territoire % 'Bordeux'  -- Opérateur trigram
ORDER BY score DESC LIMIT 5;
```

---

## 1.8 Permissions Granulaires

### Objectif
Restreindre accès par rôle (lecture seule, data analyst, admin).

### Solution v3.2
Rôles PostgreSQL + Row-Level Security (RLS).

#### Rôles
```sql
-- Lecture seule (public API)
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE electio_analytics TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- Data Analyst (lecture + écriture indicateurs/prédictions)
CREATE ROLE data_analyst;
GRANT readonly TO data_analyst;
GRANT INSERT, UPDATE ON indicateur, prediction TO data_analyst;

-- Admin (tous droits)
CREATE ROLE admin_electio;
GRANT ALL PRIVILEGES ON DATABASE electio_analytics TO admin_electio;
```

#### Row-Level Security (RLS)
```sql
-- Activer RLS sur indicateur
ALTER TABLE indicateur ENABLE ROW LEVEL SECURITY;

-- Politique : data_analyst voit uniquement données fiabilité "CONFIRME"
CREATE POLICY pol_analyst_confirmed ON indicateur
    FOR SELECT
    TO data_analyst
    USING (fiabilite = 'CONFIRME');

-- Admin voit tout
CREATE POLICY pol_admin_all ON indicateur
    FOR ALL
    TO admin_electio
    USING (true);
```

---

## 1.9 Agrégation Temps Réel

### Objectif
Vues matérialisées avec refresh incrémental pour dashboards temps réel.

### Solution v3.2
Extension `timescaledb` ou vues matérialisées CONCURRENTLY.

#### Vue Matérialisée Incrémentale
```sql
CREATE MATERIALIZED VIEW mv_stats_elections AS
SELECT
    annee,
    tour,
    candidat,
    SUM(nombre_voix) AS total_voix_france,
    AVG(pourcentage_voix) AS moyenne_pct,
    COUNT(DISTINCT id_territoire) AS nb_territoires
FROM election_result
GROUP BY annee, tour, candidat;

-- Index pour refresh rapide
CREATE UNIQUE INDEX idx_mv_stats ON mv_stats_elections (annee, tour, candidat);

-- Refresh incrémental (sans lock)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stats_elections;
```

---

## 1.10 API GraphQL Native

### Objectif
Requêtes GraphQL directement depuis PostgreSQL (via PostGraphile).

### Solution v4.0
Extension `postgraphile` pour API auto-générée.

#### Exemple Requête GraphQL
```graphql
query {
  allTerritoires(condition: {typeterritoire: "IRIS"}) {
    nodes {
      idTerritoire
      nomTerritoire
      electionResultsByIdTerritoire(condition: {annee: 2022, tour: 1}) {
        nodes {
          candidat
          pourcentageVoix
        }
      }
    }
  }
}
```

---

## 2. Roadmap Timeline

```
2026-Q2 : v2.0 (actuel)
  │
  ├─ 2026-Q3 : v3.0 RELEASE
  │    ├─ Hiérarchie géographique explicite
  │    ├─ Historisation prédictions
  │    ├─ Indicateurs dérivés
  │    └─ Support multi-élections
  │
  ├─ 2026-Q4 : v3.1
  │    ├─ Audit trail complet
  │    ├─ Partitioning par année
  │    └─ Full-Text Search
  │
  ├─ 2027-Q1 : v3.2
  │    ├─ Permissions granulaires
  │    └─ Agrégation temps réel
  │
  └─ 2027-Q3 : v4.0
       └─ API GraphQL native
```

---

## 3. Critères de Succès

### Métriques Clés v3.0

| Métrique | v2.0 (actuel) | v3.0 (objectif) | Gain |
|----------|---------------|-----------------|------|
| **Requêtes ML complexes** | 50-100 ms | <30 ms | ×2-3 |
| **Agrégation géographique** | 500 ms (applicatif) | <50 ms (SQL récursif) | ×10 |
| **Volumétrie supportée** | <1M lignes | <10M lignes | ×10 |
| **Types élections** | 1 (présidentielles) | 5+ (toutes élections) | ×5 |
| **Traçabilité** | Partielle (timestamps) | Complète (audit_log) | 100% |

---

**Conclusion :** La roadmap v3.0 positionne le schéma pour un passage à l'échelle national tout en améliorant traçabilité et performances.
