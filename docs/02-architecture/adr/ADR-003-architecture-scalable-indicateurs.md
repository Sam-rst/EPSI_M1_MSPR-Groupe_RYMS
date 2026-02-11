# ADR-003 : Architecture Scalable pour Indicateurs Socio-Économiques

**Date :** 2026-02-09
**Statut :** ✅ ACCEPTÉ
**Décideurs :** @tech, @pm
**Impact :** Architecture de base de données

---

## Contexte

Le MCD v1.0 utilisait des tables séparées pour chaque type d'indicateur (`Indicateur_Securite`, `Indicateur_Emploi`). Cette approche présente des limitations :

- **Rigidité** : Ajout d'une nouvelle source = créer une nouvelle table + migration
- **Maintenance** : N tables = complexité croissante
- **Requêtes ML** : Multiples LEFT JOIN nécessaires
- **Documentation** : Métadonnées éparpillées

**Besoin identifié :** Architecture extensible pour ajouter dynamiquement de nouvelles sources sans modification de schéma.

---

## Décision

Adoption d'une **architecture hybride** combinant :

1. **Tables spécialisées** pour données à fort volume et schéma stable (`election_result`)
2. **Table générique `indicateur`** pour tous les indicateurs socio-économiques (pattern EAV allégé)
3. **Table catalogue `type_indicateur`** pour la documentation centralisée
4. **JSONB PostgreSQL** pour métadonnées flexibles

### Schéma retenu

```
territoire (référentiel géographique stable)
    ↓
    ├── election_result (spécialisée, schéma fixe)
    ├── indicateur (générique, JSONB flexible)
    │       ↓
    │   type_indicateur (catalogue, documentation)
    └── prediction (ML output)
```

---

## Alternatives Considérées

### Option A : Tables séparées par type (Status Quo)

**Avantages :**
- ✅ Schéma explicite par type
- ✅ Validation forte en DDL

**Inconvénients :**
- ❌ Non scalable (N tables pour N types)
- ❌ Maintenance complexe
- ❌ Requêtes ML compliquées

**Verdict :** ❌ Rejeté (limitations POC identifiées)

### Option B : EAV pur (Entity-Attribute-Value)

**Avantages :**
- ✅ Extrême flexibilité
- ✅ 1 seule table

**Inconvénients :**
- ❌ Performance dégradée (trop de joins)
- ❌ Requêtes complexes
- ❌ Perte de typage fort

**Verdict :** ❌ Rejeté (over-engineering)

### Option C : Hybrid EAV + Tables spécialisées (RETENU)

**Avantages :**
- ✅ Scalabilité : +N sources sans migration
- ✅ Performance : Tables spécialisées pour gros volumes
- ✅ Flexibilité : JSONB pour métadonnées
- ✅ Documentation : Catalogue centralisé

**Inconvénients :**
- ⚠️ Validation JSONB en applicatif
- ⚠️ Requêtes nécessitent filtrage `id_type`

**Verdict :** ✅ ACCEPTÉ (balance optimale)

---

## Conséquences

### Positives

1. **Extensibilité :** Ajout d'une nouvelle source :
   ```sql
   INSERT INTO type_indicateur (...) VALUES (...);  -- 1 ligne !
   ```

2. **Maintenance simplifiée :**
   - v1.0 : 5 tables indicateurs → v2.0 : 1 table + 1 catalogue

3. **Requêtes ML simplifiées :**
   ```sql
   -- Avant (v1.0) : 3 LEFT JOIN sur tables différentes
   -- Après (v2.0) : 1 JOIN avec filtrage
   FROM indicateur JOIN type_indicateur USING (id_type)
   ```

4. **Documentation centralisée :**
   - Unités, sources, fréquences dans `type_indicateur`

### Négatives

1. **Validation JSONB :**
   - Schéma `metadata` validé en Python (ETL), pas en DB
   - Mitigé par : Scripts de validation dans `src/etl/load/`

2. **Légère complexité requêtes :**
   - Filtrage par `id_type` nécessaire
   - Mitigé par : Indexation appropriée

3. **Migration existante :**
   - Nécessite migration des données v1.0 vers v2.0
   - Mitigé par : Scripts de migration fournis

---

## Implémentation

### Phase 1 : Création schéma v2.0 ✅
- Créer `type_indicateur`, `indicateur`
- Garder `election_result`, `territoire`, `prediction`

### Phase 2 : ETL adapté (en cours)
- @de adapte scripts `load/` pour insérer dans table générique
- Validation schéma JSONB

### Phase 3 : Tests & validation
- Tests volumétrie (1M lignes)
- Benchmarks requêtes ML

### Phase 4 : Migration v1.0 → v2.0 (si nécessaire)
- Script SQL fourni dans [MCD v2.0](../database/versions/v2.0/MCD.md)

---

## Métriques de Succès

| Métrique | Cible | Statut |
|----------|-------|--------|
| Temps ajout nouvelle source | <5min (vs 2h en v1.0) | ⏳ À valider |
| Performance requête ML | <100ms sur 1M lignes | ⏳ À tester |
| Réduction code ETL | -40% lignes | ⏳ À mesurer |
| Nb tables indicateurs | 1 (vs 5+ en v1.0) | ✅ Atteint |

---

## Références

- [MCD v2.0 (Architecture Scalable)](../database/versions/v2.0/MCD.md) : Schéma complet v2.0
- [MCD v1.0 (Schéma Initial)](../database/versions/v1.0/MCD.md) : Schéma v1.0 (référence historique)
- PostgreSQL JSONB Best Practices : https://www.postgresql.org/docs/current/datatype-json.html

---

## Révisions

| Date | Auteur | Changement |
|------|--------|------------|
| 2026-02-09 | @tech | Création ADR-003 |
