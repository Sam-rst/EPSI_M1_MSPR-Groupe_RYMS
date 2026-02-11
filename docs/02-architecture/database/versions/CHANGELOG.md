# Historique des Versions - Schéma Base de Données

Ce fichier documente l'évolution du schéma de base de données Electio-Analytics.

---

## [v2.0] - 2026-02-10 - Architecture Scalable (ACTUELLE)

### 🎯 Objectifs
- Extensibilité maximale pour ajout dynamique de nouvelles sources
- Réduction du nombre de tables (maintenance simplifiée)
- Performance optimisée pour requêtes Machine Learning

### ✨ Changements Majeurs

#### Architecture
- **Pattern EAV Hybride** : Introduction du pattern Entity-Attribute-Value pour les indicateurs
- **Table générique `indicateur`** : Remplace `indicateur_securite` + `indicateur_emploi`
- **Table catalogue `type_indicateur`** : Nouveau catalogue centralisé des types d'indicateurs

#### Tables Modifiées
| Table | v1.0 | v2.0 | Changement |
|-------|------|------|------------|
| `territoire` | ✅ | ✅ | **Inchangée** (ajout colonne `metadata` JSONB) |
| `election_result` | ✅ | ✅ | **Inchangée** (ajout colonne `metadata` JSONB) |
| `indicateur_securite` | ✅ | ❌ | **SUPPRIMÉE** (fusionnée dans `indicateur`) |
| `indicateur_emploi` | ✅ | ❌ | **SUPPRIMÉE** (fusionnée dans `indicateur`) |
| `type_indicateur` | ❌ | ✅ | **NOUVELLE** (catalogue types) |
| `indicateur` | ❌ | ✅ | **NOUVELLE** (table générique EAV) |
| `prediction` | ✅ | ✅ | **Inchangée** (ajout colonnes métriques JSONB) |

#### Schéma
```
v1.0 : 5 tables (Territoire, Election_Result, Indicateur_Securite, Indicateur_Emploi, Prediction)
v2.0 : 5 tables (Territoire, Type_Indicateur, Indicateur, Election_Result, Prediction)
```

#### Avantages v2.0
- ✅ **Extensibilité** : Ajout nouvelle source = 1 INSERT dans `type_indicateur` (vs ALTER TABLE en v1.0)
- ✅ **Maintenance** : 1 table `indicateur` au lieu de N tables par source
- ✅ **Flexibilité** : Métadonnées JSONB variables selon type (vs colonnes fixes)
- ✅ **Performance** : Indexation GIN sur JSONB optimisée
- ✅ **Documentation** : Catalogue centralisé des sources (`type_indicateur`)

#### Trade-offs
- ⚠️ Requêtes nécessitent filtrage par `id_type` (mitigé par index composites)
- ⚠️ Validation schéma JSONB en applicatif (non en DB)

### 📝 Migration v1.0 → v2.0

#### Script de Migration
```sql
-- 1. Créer nouvelles tables v2.0
CREATE TABLE type_indicateur (...);
CREATE TABLE indicateur (...);

-- 2. Migrer données Indicateur_Securite
INSERT INTO type_indicateur (code_type, categorie, ...)
VALUES ('SECURITE_CAMBRIOLAGES', 'SECURITE', ...);

INSERT INTO indicateur (id_territoire, id_type, annee, valeur_numerique, metadata)
SELECT
    id_territoire,
    (SELECT id_type FROM type_indicateur WHERE code_type = 'SECURITE_' || UPPER(REPLACE(type_fait, ' ', '_'))),
    annee,
    nombre_faits,
    jsonb_build_object('taux_pour_1000_hab', taux_pour_1000_hab)
FROM indicateur_securite_OLD;

-- 3. Migrer données Indicateur_Emploi
INSERT INTO indicateur (...)
SELECT ... FROM indicateur_emploi_OLD;

-- 4. Valider intégrité
SELECT * FROM validate_database_integrity();

-- 5. Supprimer anciennes tables
DROP TABLE indicateur_securite_OLD;
DROP TABLE indicateur_emploi_OLD;
```

### 🔗 Références
- **Documentation v2.0** : [README.md](../README.md)
- **MCD v2.0** : [01-mcd.md](../01-mcd.md)
- **Script migration** : [001_initial_schema.sql](../../../../src/database/migrations/001_initial_schema.sql)

---

## [v1.0] - 2026-02-09 - Schéma Initial

### 🎯 Objectifs
- Schéma relationnel classique normalisé (3FN)
- Tables séparées par type d'indicateur (sécurité, emploi)
- Structure simple pour POC

### 📊 Tables Créées (5)
1. **`territoire`** : Référentiel géographique (IRIS, Bureaux de vote)
2. **`election_result`** : Résultats électoraux 2017 & 2022
3. **`indicateur_securite`** : Indicateurs SSMSI (criminalité)
4. **`indicateur_emploi`** : Indicateurs INSEE (chômage, revenus)
5. **`prediction`** : Prédictions ML 2027

### ⚙️ Caractéristiques
- **Normalisation** : 3FN (Troisième Forme Normale)
- **Contraintes** : CHECK, FK (CASCADE), UNIQUE
- **Indexes** : 12 indexes B-Tree
- **Volumétrie** : ~26 650 lignes estimées (Bordeaux)

### 📁 Limitations Identifiées
- ❌ **Rigidité** : Ajout nouvelle source = ALTER TABLE ou nouvelle table
- ❌ **Scalabilité** : N tables pour N sources d'indicateurs
- ❌ **Complexité** : Multiples LEFT JOIN pour requêtes ML
- ❌ **Documentation** : Sources éparpillées (pas de catalogue)

### 🔗 Archive
- **MCD v1.0** : [versions/v1.0/MCD.md](v1.0/MCD.md)

---

## 📋 Conventions de Versioning

### Numérotation Sémantique
```
MAJOR.MINOR.PATCH

- MAJOR : Changement incompatible (breaking change)
  Exemple : Suppression table, renommage colonne clé

- MINOR : Ajout fonctionnalité rétrocompatible
  Exemple : Nouvelle table, nouvelle colonne NULL

- PATCH : Correction bug ou optimisation
  Exemple : Index ajouté, contrainte modifiée
```

### Exemples
- `v2.0.0` → Architecture EAV (breaking change)
- `v2.1.0` → Ajout table `indicateur_demographie` (compatible)
- `v2.0.1` → Optimisation index GIN (patch)

---

## 🚀 Roadmap Futures Versions

### v2.1.0 (Planifiée Q2 2026)
- [ ] Table `indicateur_demographie` (âge, CSP, revenus)
- [ ] Support multi-élections (Législatives, Municipales)
- [ ] Hiérarchie géographique explicite (`id_territoire_parent`)

### v2.2.0 (Planifiée Q3 2026)
- [ ] Historisation prédictions (table `prediction_history`)
- [ ] Audit trail complet (triggers sur toutes tables)
- [ ] Partitioning `election_result` par année (si >1M lignes)

### v3.0.0 (Exploration)
- [ ] Support données temps réel (streaming Kafka)
- [ ] Graph database pour relations sociales (Neo4j)
- [ ] Data lake pour données non structurées (Delta Lake)

---

**Dernière mise à jour :** 2026-02-10
**Mainteneur :** @tech
