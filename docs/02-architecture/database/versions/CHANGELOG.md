# Historique des Versions - Schéma Base de Données

Ce fichier documente l'évolution du schéma de base de données Electio-Analytics.

---

## [v3.0] - 2026-02-12 - Hiérarchie Géographique + Système Polymorphe ⭐ (ACTUELLE)

### 🎯 Objectifs
- Hiérarchie géographique explicite multi-niveaux
- Référentiels candidats et partis avec profils complets
- Séparation participation vs résultats par candidat
- Système polymorphe de territoire sans FK classiques
- Support multi-granularités électorales dynamiques

### ✨ Changements Majeurs

#### Architecture
- **Hiérarchie géographique** : 6 tables (Region → Departement → Canton/Commune → Arrondissement → Bureau)
- **Entités politiques** : Candidat, Parti, CandidatParti (affiliations temporelles)
- **Séparation résultats** : ResultatParticipation (stats globales) + ResultatCandidat (par candidat)
- **Système polymorphe** : id_territoire + type_territoire (sans FK) pour flexibilité maximale

#### Tables Supprimées
| Table v2.0 | Statut v3.0 | Remplacée par |
|------------|-------------|---------------|
| `territoire` | ❌ SUPPRIMÉE | Hiérarchie géo (region, departement, canton, commune, arrondissement, bureau_vote) |
| `election_result` | ❌ SUPPRIMÉE | resultat_participation + resultat_candidat |

#### Tables Ajoutées (14 nouvelles)
| Domaine | Tables | Rôle |
|---------|--------|------|
| **Géographique** | region, departement, canton, commune, arrondissement, bureau_vote | Hiérarchie multi-niveaux |
| **Candidats/Partis** | candidat, parti, candidat_parti | Référentiels normalisés + affiliations |
| **Élections** | type_election, election, election_territoire | Typologie + tracking granularités |
| **Résultats** | resultat_participation, resultat_candidat | Séparation stats vs candidats |

#### Tables Modifiées
| Table | v2.0 | v3.0 | Changement |
|-------|------|------|------------|
| `type_indicateur` | ✅ | ✅ | **Inchangée** |
| `indicateur` | ✅ | ✅ | **Modifiée** : +type_territoire, -FK territoire |
| `prediction` | ✅ | ✅ | **Modifiée** : +type_territoire, -FK territoire |

#### Schéma
```
v2.0 : 5 tables
v3.0 : 19 tables (×3.8 expansion)
```

#### Avantages v3.0
- ✅ **Clarté** : Hiérarchie géographique explicite et intuitive
- ✅ **Features ML** : ×2.3 features exploitables (~35 vs ~15)
- ✅ **Flexibilité** : Support multi-granularités sans contraintes rigides
- ✅ **Normalisation** : Candidats/Partis séparés avec profils enrichis
- ✅ **Performance** : Colonnes calculées (COMPUTED) pour pourcentages
- ✅ **Traçabilité** : ElectionTerritoire track les granularités disponibles

#### Simplifications
- ❌ **Geometry supprimée** : Colonne PostGIS retirée (peut être rajoutée ultérieurement)

### 📝 Migration v2.0 → v3.0

#### Breaking Changes
- ❌ **Incompatibilité totale** : Schéma complètement refondu
- ❌ **Tables centrales supprimées** : territoire, election_result

#### Procédure
```bash
# 1. Backup base v2.0
pg_dump electio_analytics > backup_v2.0_$(date +%Y%m%d).sql

# 2. Cleanup tables v2.0
alembic upgrade 5c74986a8b20  # Migration cleanup

# 3. Déploiement v3.0
alembic upgrade head  # Migration 691a1578615b

# 4. Validation
python -c "from database.config import get_session; from sqlalchemy import inspect; \
    print(f'Tables: {len(inspect(get_session().bind).get_table_names())}')"  # Devrait afficher 19
```

#### Migration Données (si nécessaire)
Script ETL à créer pour migrer les données v2.0 → v3.0 :
- Territoire → Décomposition en hiérarchie géographique
- Election_Result → Séparation en resultat_participation + resultat_candidat

### 🔗 Références
- **Documentation v3.0** : [README.md](../README.md)
- **MCD v3.0** : [versions/v3.0/MCD.md](v3.0/MCD.md)
- **Migrations** : [691a1578615b](../../../../src/database/migrations/versions/)

---

## [v2.0] - 2026-02-10 - Architecture Scalable (OBSOLÈTE)

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

## [v1.0] - 2026-02-09 - Schéma Initial (OBSOLÈTE)

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

### v3.1.0 (Planifiée Q2 2026)
- [ ] Rajout colonne `geometry` PostGIS si besoin analyses spatiales
- [ ] Table `indicateur_demographie` étendue (âge, CSP, revenus)
- [ ] Support multi-élections complètes (Législatives, Municipales, Régionales)
- [ ] Import données historiques élections 2012-2022

### v3.2.0 (Planifiée Q3 2026)
- [ ] Historisation prédictions (table `prediction_history`)
- [ ] Audit trail complet (triggers sur toutes tables)
- [ ] Partitioning `resultat_candidat` par année (si >1M lignes)

### v4.0.0 (Exploration 2027)
- [ ] Support données temps réel (streaming Kafka)
- [ ] Graph database pour relations sociales/politiques (Neo4j)
- [ ] Data lake pour données non structurées (Delta Lake)

---

**Dernière mise à jour :** 2026-02-12
**Mainteneur :** @tech
