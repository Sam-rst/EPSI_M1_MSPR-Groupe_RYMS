# Modèle Conceptuel de Données v2.0 - Architecture Scalable
## Electio-Analytics - POC Bordeaux

**Version :** 2.0 (Architecture Scalable)
**Date :** 2026-02-09
**Auteur :** @tech
**Révision :** Optimisé pour ajout dynamique de nouvelles sources de données

---

## 🎯 Objectifs Architecture v2.0

1. **Extensibilité** : Ajout de nouvelles sources sans modifier le schéma
2. **Flexibilité** : Support de métadonnées variables par type d'indicateur
3. **Maintenabilité** : Réduction du nombre de tables
4. **Performance** : Indexation optimisée pour requêtes ML

---

## 📐 Principes de Design

### Pattern : **Hybrid Entity-Attribute-Value (EAV) + Tables spécialisées**

- **Tables spécialisées** pour les données structurées à fort volume (`election_result`)
- **Table générique** pour les indicateurs socio-économiques variables (`indicateur`)
- **JSONB** pour métadonnées flexibles (PostgreSQL)

```
┌──────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE v2.0                         │
│                                                              │
│  ┌─────────────┐        ┌──────────────────────┐           │
│  │  Territoire │◄───────│  Type_Indicateur     │           │
│  │  (Core)     │        │  (Catalog)           │           │
│  └──────┬──────┘        └──────────────────────┘           │
│         │                                                    │
│    ┌────┴────┬──────────────────┬──────────────┐          │
│    │         │                  │              │          │
│    ▼         ▼                  ▼              ▼          │
│  Election  Indicateur       Prediction    Metadata       │
│  Result    (Generic)        (ML Output)   (Flexible)     │
│  (High     (EAV Pattern)                                  │
│  Volume)                                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Entité 1 : `territoire` (INCHANGÉE)

**Description :** Référentiel géographique stable.

```sql
CREATE TABLE territoire (
    id_territoire VARCHAR(20) PRIMARY KEY,
    code_insee VARCHAR(5) NOT NULL,
    type_territoire VARCHAR(20) NOT NULL CHECK (type_territoire IN ('COMMUNE', 'IRIS', 'BUREAU_VOTE', 'ARRONDISSEMENT')),
    nom_territoire VARCHAR(100) NOT NULL,
    geometry GEOMETRY(POLYGON, 4326),  -- PostGIS
    population INTEGER,
    metadata JSONB,  -- Données supplémentaires flexibles
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_territoire_insee ON territoire(code_insee);
CREATE INDEX idx_territoire_type ON territoire(type_territoire);
```

**Avantages :**
- ✅ Structure stable (peu de changements)
- ✅ JSONB pour métadonnées futures (ex: coordonnées GPS, superficie)
- ✅ Indexation géographique (PostGIS) pour cartographie

---

## Entité 2 : `type_indicateur` (NOUVEAU - Catalog Pattern)

**Description :** Catalogue des types d'indicateurs socio-économiques disponibles.

```sql
CREATE TABLE type_indicateur (
    id_type SERIAL PRIMARY KEY,
    code_type VARCHAR(50) UNIQUE NOT NULL,  -- Ex: 'SECURITE_CRIMINALITE', 'EMPLOI_CHOMAGE'
    categorie VARCHAR(50) NOT NULL,  -- Ex: 'SECURITE', 'EMPLOI', 'DEMOGRAPHIE'
    nom_affichage VARCHAR(100) NOT NULL,
    description TEXT,
    unite_mesure VARCHAR(50),  -- Ex: 'faits_constatés', 'pourcentage', 'nombre'
    source_officielle VARCHAR(100),  -- Ex: 'SSMSI', 'INSEE', 'data.gouv.fr'
    frequence VARCHAR(20),  -- Ex: 'ANNUEL', 'TRIMESTRIEL', 'MENSUEL'
    date_debut_disponibilite DATE,
    actif BOOLEAN DEFAULT TRUE,
    schema_metadata JSONB,  -- Schéma attendu pour la colonne metadata de indicateur
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_type_indicateur_categorie ON type_indicateur(categorie);
CREATE INDEX idx_type_indicateur_code ON type_indicateur(code_type);
```

**Exemples de données :**

```sql
INSERT INTO type_indicateur (code_type, categorie, nom_affichage, unite_mesure, source_officielle, frequence)
VALUES
    ('SECURITE_CAMBRIOLAGES', 'SECURITE', 'Cambriolages de logement', 'nombre', 'SSMSI', 'ANNUEL'),
    ('SECURITE_VIOLENCES_INTRAFAM', 'SECURITE', 'Violences intrafamiliales', 'nombre', 'SSMSI', 'ANNUEL'),
    ('EMPLOI_TAUX_CHOMAGE', 'EMPLOI', 'Taux de chômage', 'pourcentage', 'INSEE', 'TRIMESTRIEL'),
    ('DEMOGRAPHIE_POPULATION_ACTIVE', 'DEMOGRAPHIE', 'Population active', 'nombre', 'INSEE', 'ANNUEL'),
    ('ELECTION_PARTICIPATION', 'ELECTION', 'Taux de participation', 'pourcentage', 'MI', 'ELECTION');
```

**Avantages :**
- ✅ **Ajout dynamique** : Nouvelle source = 1 INSERT dans type_indicateur
- ✅ **Documentation intégrée** : Source, unité, fréquence centralisées
- ✅ **Activable/désactivable** : Flag `actif` pour gérer le cycle de vie

---

## Entité 3 : `indicateur` (GÉNÉRIQUE - Remplace Indicateur_Securite + Indicateur_Emploi)

**Description :** Table générique pour TOUS les indicateurs socio-économiques.

```sql
CREATE TABLE indicateur (
    id_indicateur BIGSERIAL PRIMARY KEY,
    id_territoire VARCHAR(20) NOT NULL REFERENCES territoire(id_territoire) ON DELETE CASCADE,
    id_type INTEGER NOT NULL REFERENCES type_indicateur(id_type),
    annee INTEGER NOT NULL,
    periode VARCHAR(20),  -- 'T1', 'T2', 'T3', 'T4' (trimestre) ou 'M01'-'M12' (mois) ou NULL (annuel)
    valeur_numerique DECIMAL(15,4),  -- Valeur principale (taux, nombre, etc.)
    valeur_texte TEXT,  -- Valeur textuelle si nécessaire
    metadata JSONB,  -- Données supplémentaires spécifiques au type
    source_detail VARCHAR(200),  -- Source précise (ex: "SSMSI_2024_GEOGRAPHIE2025")
    fiabilite VARCHAR(20) DEFAULT 'CONFIRME',  -- 'CONFIRME', 'ESTIME', 'PROVISOIRE'
    created_at TIMESTAMP DEFAULT NOW(),

    -- Contrainte unicité : éviter doublons
    CONSTRAINT unique_indicateur UNIQUE (id_territoire, id_type, annee, periode)
);

CREATE INDEX idx_indicateur_territoire ON indicateur(id_territoire);
CREATE INDEX idx_indicateur_type ON indicateur(id_type);
CREATE INDEX idx_indicateur_annee ON indicateur(annee);
CREATE INDEX idx_indicateur_composite ON indicateur(id_territoire, id_type, annee);
CREATE INDEX idx_indicateur_metadata ON indicateur USING GIN (metadata);  -- Index JSONB
```

**Exemples de données :**

```sql
-- Sécurité : Cambriolages Bordeaux 2017
INSERT INTO indicateur (id_territoire, id_type, annee, periode, valeur_numerique, metadata)
VALUES (
    '33063',  -- Code INSEE Bordeaux
    1,  -- SECURITE_CAMBRIOLAGES
    2017,
    NULL,  -- Annuel
    504.0,  -- Nombre de faits
    '{"taux_pour_1000_hab": 1.999, "population_reference": 252040}'::JSONB
);

-- Emploi : Taux de chômage Bordeaux T1 2022
INSERT INTO indicateur (id_territoire, id_type, annee, periode, valeur_numerique, metadata)
VALUES (
    '33063',
    3,  -- EMPLOI_TAUX_CHOMAGE
    2022,
    'T1',
    8.5,  -- Taux en %
    '{"population_active": 125000, "nombre_chomeurs": 10625}'::JSONB
);
```

**Avantages :**
- ✅ **1 seule table** pour tous les indicateurs → moins de joins
- ✅ **JSONB flexible** : Métadonnées variables par type
- ✅ **Requêtes simplifiées** : Filtrage par `id_type`
- ✅ **Scalabilité** : Millions de lignes supportées avec indexation appropriée

---

## Entité 4 : `election_result` (SPÉCIALISÉE - Inchangée)

**Description :** Table spécialisée pour résultats électoraux (volume élevé, schéma stable).

```sql
CREATE TABLE election_result (
    id_result BIGSERIAL PRIMARY KEY,
    id_territoire VARCHAR(20) NOT NULL REFERENCES territoire(id_territoire) ON DELETE CASCADE,
    annee INTEGER NOT NULL,
    tour INTEGER NOT NULL CHECK (tour IN (1, 2)),
    candidat VARCHAR(100) NOT NULL,
    parti VARCHAR(50),
    nombre_voix INTEGER NOT NULL,
    pourcentage_voix DECIMAL(5,2) NOT NULL,
    nombre_inscrits INTEGER NOT NULL,
    nombre_votants INTEGER NOT NULL,
    nombre_exprimes INTEGER NOT NULL,
    taux_participation DECIMAL(5,2) NOT NULL,
    metadata JSONB,  -- Ex: nuance politique, âge candidat
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_election_result UNIQUE (id_territoire, annee, tour, candidat)
);

CREATE INDEX idx_election_territoire ON election_result(id_territoire);
CREATE INDEX idx_election_annee_tour ON election_result(annee, tour);
CREATE INDEX idx_election_candidat ON election_result(candidat);
CREATE INDEX idx_election_composite ON election_result(id_territoire, annee, tour);
```

**Pourquoi table spécialisée ?**
- ✅ Volume élevé (milliers de lignes par élection)
- ✅ Schéma stable (colonnes fixes connues)
- ✅ Requêtes fréquentes et complexes (joins multiples)
- ✅ Performance optimale avec schéma fixe

---

## Entité 5 : `prediction` (ML OUTPUT - Inchangée)

```sql
CREATE TABLE prediction (
    id_prediction BIGSERIAL PRIMARY KEY,
    id_territoire VARCHAR(20) NOT NULL REFERENCES territoire(id_territoire) ON DELETE CASCADE,
    candidat VARCHAR(100) NOT NULL,
    parti VARCHAR(50),
    annee_prediction INTEGER DEFAULT 2027,
    tour INTEGER NOT NULL CHECK (tour IN (1, 2)),
    pourcentage_predit DECIMAL(5,2) NOT NULL,
    intervalle_confiance_inf DECIMAL(5,2),
    intervalle_confiance_sup DECIMAL(5,2),
    modele_utilise VARCHAR(50) NOT NULL,
    version_modele VARCHAR(20),
    metriques_modele JSONB,  -- R², MAE, RMSE, etc.
    features_utilisees JSONB,  -- Liste des features du modèle
    date_generation TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_prediction UNIQUE (id_territoire, candidat, tour, annee_prediction, version_modele)
);

CREATE INDEX idx_prediction_territoire ON prediction(id_territoire);
CREATE INDEX idx_prediction_annee ON prediction(annee_prediction);
```

---

## 🔄 Comparaison v1.0 vs v2.0

| Critère | v1.0 (Ancien) | v2.0 (Scalable) |
|---------|---------------|-----------------|
| **Nb tables indicateurs** | 2 (Securite + Emploi) | 1 (générique) |
| **Ajout nouvelle source** | Créer nouvelle table + migration | 1 INSERT dans `type_indicateur` |
| **Flexibilité métadonnées** | ❌ Colonnes fixes | ✅ JSONB flexible |
| **Maintenance** | ❌ Complexe (N tables) | ✅ Simple (1 table) |
| **Requêtes ML** | ❌ Multiples LEFT JOIN | ✅ 1 JOIN avec filtrage |
| **Performance** | ⚠️ Dégradation avec N tables | ✅ Stable avec indexation |
| **Documentation** | ❌ Éparpillée | ✅ Centralisée (catalog) |

---

## 📊 Requêtes SQL Exemples v2.0

### Exemple 1 : Jointure complète pour ML (simplifié)

```sql
SELECT
    t.id_territoire,
    t.nom_territoire,
    er.annee,
    er.candidat,
    er.pourcentage_voix,

    -- Indicateur criminalité (moyenne annuelle)
    AVG(CASE WHEN ti.categorie = 'SECURITE' THEN i.valeur_numerique END) AS criminalite_moyenne,

    -- Indicateur emploi
    AVG(CASE WHEN ti.code_type = 'EMPLOI_TAUX_CHOMAGE' THEN i.valeur_numerique END) AS taux_chomage,

    -- Indicateur participation
    AVG(CASE WHEN ti.code_type = 'ELECTION_PARTICIPATION' THEN i.valeur_numerique END) AS taux_participation

FROM territoire t
LEFT JOIN election_result er ON t.id_territoire = er.id_territoire
LEFT JOIN indicateur i ON t.id_territoire = i.id_territoire AND i.annee = er.annee
LEFT JOIN type_indicateur ti ON i.id_type = ti.id_type

WHERE er.tour = 2
  AND er.annee IN (2017, 2022)

GROUP BY t.id_territoire, t.nom_territoire, er.annee, er.candidat, er.pourcentage_voix;
```

### Exemple 2 : Ajout dynamique d'une nouvelle source (Revenu Médian)

```sql
-- 1. Déclarer le nouveau type d'indicateur
INSERT INTO type_indicateur (code_type, categorie, nom_affichage, unite_mesure, source_officielle, frequence)
VALUES ('REVENU_MEDIAN', 'ECONOMIE', 'Revenu médian par habitant', 'euros', 'INSEE', 'ANNUEL');

-- 2. Insérer les données
INSERT INTO indicateur (id_territoire, id_type, annee, valeur_numerique, metadata)
SELECT
    '33063',  -- Bordeaux
    (SELECT id_type FROM type_indicateur WHERE code_type = 'REVENU_MEDIAN'),
    2022,
    21500.00,
    '{"source_detail": "INSEE_REVENUS_2022", "unité_compte": "foyers_fiscaux"}'::JSONB;

-- ✅ AUCUNE MODIFICATION DE SCHÉMA NÉCESSAIRE !
```

### Exemple 3 : Filtrer par catégorie d'indicateurs

```sql
-- Récupérer tous les indicateurs de sécurité pour Bordeaux
SELECT
    t.nom_territoire,
    ti.nom_affichage,
    i.annee,
    i.valeur_numerique,
    i.metadata->>'taux_pour_1000_hab' AS taux
FROM indicateur i
JOIN type_indicateur ti ON i.id_type = ti.id_type
JOIN territoire t ON i.id_territoire = t.id_territoire
WHERE t.code_insee = '33063'
  AND ti.categorie = 'SECURITE'
  AND i.annee BETWEEN 2017 AND 2024
ORDER BY i.annee, ti.nom_affichage;
```

---

## 🚀 Stratégie de Migration v1.0 → v2.0

### Option A : Migration complète (recommandée pour production)

```sql
-- 1. Créer nouvelles tables v2.0
-- 2. Migrer données existantes
INSERT INTO indicateur (id_territoire, id_type, annee, periode, valeur_numerique, metadata)
SELECT
    id_territoire,
    (SELECT id_type FROM type_indicateur WHERE code_type = 'SECURITE_' || UPPER(REPLACE(type_fait, ' ', '_'))),
    annee,
    NULL,
    nombre_faits,
    jsonb_build_object('taux_pour_1000_hab', taux_pour_1000_hab, 'source', source)
FROM Indicateur_Securite_OLD;

-- 3. Valider intégrité
-- 4. Supprimer anciennes tables
DROP TABLE Indicateur_Securite_OLD;
DROP TABLE Indicateur_Emploi_OLD;
```

### Option B : Approche hybride (POC)

- Garder `election_result` inchangé
- Créer `indicateur` + `type_indicateur` pour nouvelles données
- Migrer progressivement

---

## ✅ Validation Architecture v2.0

**Critères de succès :**
- ✅ **Scalabilité** : +10 nouvelles sources sans modification schéma
- ✅ **Performance** : Requêtes ML <100ms sur 1M lignes
- ✅ **Flexibilité** : Support métadonnées variables (JSONB)
- ✅ **Maintenabilité** : Réduction 40% du code ETL

**Trade-offs acceptés :**
- ⚠️ Requêtes nécessitent filtrage par `id_type` (mitigé par indexation)
- ⚠️ Validation schéma JSONB en applicatif (non en DB)

---

**Prochaine étape :** @de implémente le schéma v2.0 et adapte les scripts ETL.
