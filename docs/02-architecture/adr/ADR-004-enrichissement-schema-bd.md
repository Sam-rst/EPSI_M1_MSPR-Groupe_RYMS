# ADR-004 : Enrichissement Schéma Base de Données v3.0

**Date :** 2026-02-11

**Statut :** ✅ ACCEPTÉ

**Décideurs :** @tech (Tech Lead), @de (Data Engineer), @ds (Data Scientist)

**Contexte :** Passage du schéma actuel (4 tables) à un schéma enrichi (14 tables) pour améliorer la qualité des prédictions ML

---

## Contexte et Problème

### Schéma Actuel (v2.0) - Limitations

**4 tables :**
- `territoire` (référentiel géographique unique)
- `election_result` (résultats par candidat avec redondances)
- `indicateur` (indicateurs socio-économiques)
- `type_indicateur` (catalogue types indicateurs)

**Problèmes identifiés :**

1. **Manque normalisation candidats**
   - Candidat stocké en string libre : `"Emmanuel MACRON"`
   - Impossible de tracker entre élections (typos, variations)
   - Pas de métadonnées (âge, profession, historique)

2. **Manque normalisation partis**
   - Parti stocké en string libre : `"LREM"`
   - Pas de classification idéologique (gauche/droite)
   - Impossible de tracker fusions/changements de nom

3. **Redondance données participation**
   - `nombre_inscrits`, `nombre_votants`, `nombre_exprimes` répétés pour chaque candidat
   - 12 candidats × 3 colonnes = 36 valeurs redondantes par bureau/tour

4. **Granularités non gérées**
   - Un seul niveau territorial (actuellement COMMUNE)
   - Pas de support multi-granularités (certains datasets = CANTON, d'autres = BUREAU)

5. **Features ML limitées**
   - ~10 features exploitables uniquement
   - Pas d'historique candidat, pas de profil idéologique
   - Qualité prédictions limitée (R² estimé : 0.45-0.50)

---

## Décision

### Adoption Schéma Enrichi v3.0

**14 tables organisées en 4 domaines :**

1. **Hiérarchie Géographique (6 tables)**
   - `region`, `departement`, `canton`, `commune`, `arrondissement`, `bureau_vote`
   - Support multi-granularités
   - Canton et Commune = granularités parallèles (pas de liaison)

2. **Référentiels Candidats & Partis (3 tables)**
   - `candidat` (métadonnées riches : âge, profession, biographie)
   - `parti` (classification idéologique, position économique/sociale)
   - `candidat_parti` (affiliations temporelles avec historique)

3. **Événements Électoraux (3 tables)**
   - `type_election` (PRES, LEG, MUN, EUR, REG)
   - `election` (événement avec contexte)
   - `election_territoire` (référentiel granularités disponibles) **[NOUVEAU]**

4. **Résultats Électoraux (2 tables)**
   - `resultat_participation` (stats générales : inscrits, votants, abstentions, etc.)
   - `resultat_candidat` (voix par candidat)
   - **Séparation** pour éliminer redondances

---

## Justification

### Bénéfices Techniques

| Critère | Avant (v2.0) | Après (v3.0) | Gain |
|---------|--------------|--------------|------|
| **Features ML** | ~10 | ~35 | +250% |
| **R² estimé** | 0.45-0.50 | 0.70-0.75 | +50% |
| **Redondance données** | 36 valeurs/bureau | 0 (3NF) | -100% |
| **Multi-granularités** | Non supporté | BUREAU/CANTON/COMMUNE/DEPT | ✅ |
| **Tracking candidats** | Non | Oui (historique, momentum) | ✅ |
| **Profil idéologique** | Non | Oui (position économique/sociale) | ✅ |

### Bénéfices ML (@ds)

**Nouvelles features exploitables :**

```python
# Candidat (7 nouvelles)
features_candidat = [
    'age',                              # Calculable avec date_naissance
    'nb_elections_precedentes',         # Tracking historique
    'score_moyen_historique',           # Moyenne N-1, N-2
    'evolution_score_N_vs_N-1',         # Momentum
    'profession_encoded',               # One-hot encoding
    'changement_parti',                 # Binaire 0/1
]

# Parti (6 nouvelles) - TRÈS PRÉDICTIVES
features_parti = [
    'position_economique',              # -1.0 (gauche) → +1.0 (droite)
    'position_sociale',                 # -1.0 (libéral) → +1.0 (conservateur)
    'classification_ideologique',       # Categorical
    'distance_ideologique_gagnant_N-1', # Proximité vs gagnant précédent
    'anciennete_parti',                 # Âge du parti
]

# Participation (8 nouvelles)
features_participation = [
    'taux_abstention_local',
    'taux_blancs_nuls_local',
    'evolution_participation_vs_N-1',
    'ecart_vs_national',                # Engagement local
    'volatilite_participation',         # Variance sur 3 élections
]
```

**Cas d'usage ML concrets :**
- Prédiction score candidat 2027 avec R² > 0.70 (vs 0.45 actuellement)
- Clustering profils territoires (urbain progressiste, rural conservateur, etc.)
- Feature importance analysis (identifier variables les plus prédictives)

### Complexité Acceptable

**Effort migration :** 3 sprints (3 semaines)
- Sprint 1 : Tables candidat/parti
- Sprint 2 : Hiérarchie géographique + élections
- Sprint 3 : Résultats (participation + candidats)

**ROI estimé :** +15-25% qualité prédictions pour 3 semaines d'effort

---

## Conséquences

### Positives

1. ✅ **Qualité ML significativement améliorée** (+50% R²)
2. ✅ **Données normalisées 3NF** (pas de redondance)
3. ✅ **Extensibilité maximale** (support multi-types élections, multi-granularités)
4. ✅ **Traçabilité complète** (référentiel `election_territoire`)
5. ✅ **Analyses fines possibles** (clusters, importance features, etc.)

### Négatives

1. ⚠️ **Complexité accrue** (14 tables vs 4)
   - Mitigation : Vue consolidée `v_resultats_complets` pour simplifier requêtes
2. ⚠️ **Migration données** (3 semaines effort)
   - Mitigation : Migration progressive, cohabitation ancien/nouveau schéma
3. ⚠️ **Jointures multiples** (impact performance)
   - Mitigation : Index optimisés, FK composites, PostgreSQL performant
4. ⚠️ **Métadonnées incomplètes** (certains candidats sans date_naissance)
   - Mitigation : Imputation + flag `has_missing_data`

---

## Alternatives Considérées

### Alternative 1 : Schéma Actuel + Colonnes Calculées

**Description :** Ajouter colonnes calculées dans `election_result`

```sql
ALTER TABLE election_result
ADD COLUMN candidat_age INTEGER,
ADD COLUMN parti_position_economique NUMERIC;
```

**Rejet :**
- ❌ Ne résout pas la redondance (inscrits/votants toujours dupliqués)
- ❌ Pas de normalisation (candidats/partis toujours en string)
- ❌ Pas de tracking temporel (impossible de calculer momentum)

### Alternative 2 : Enrichissement Partiel (Candidat uniquement)

**Description :** Créer uniquement table `candidat`, garder le reste inchangé

**Rejet :**
- ❌ Gain ML insuffisant (~15 features au lieu de 35)
- ❌ Redondance participation non résolue
- ❌ Multi-granularités non supportées

### Alternative 3 : Schéma Enrichi Complet ✅ RETENU

**Justification :** Seule option qui résout TOUS les problèmes identifiés

---

## Stratégie de Migration

### Phase 1 : Création Tables (Non-breaking)

```sql
-- Créer nouvelles tables en parallèle de l'existant
CREATE TABLE candidat (...);
CREATE TABLE parti (...);
CREATE TABLE region (...);
CREATE TABLE departement (...);
-- etc.
```

**Avantage :** Pas d'impact sur l'existant

### Phase 2 : Migration Données

```python
def migrate_to_v3():
    # 1. Extraire candidats uniques depuis election_result
    extract_and_create_candidates()

    # 2. Créer partis depuis election_result.parti
    extract_and_create_parties()

    # 3. Migrer territoire → hiérarchie géographique
    migrate_territories_to_hierarchy()

    # 4. Créer événements élections
    create_election_events()

    # 5. Déclarer granularités dans election_territoire
    create_election_territoire_entries()

    # 6. Migrer résultats : election_result → (resultat_participation + resultat_candidat)
    migrate_results_to_split_tables()
```

### Phase 3 : Cohabitation & Tests

- Durée : 1-2 semaines
- Double écriture : charger dans ancien ET nouveau schéma
- Validation cohérence
- Tests performance

### Phase 4 : Bascule

```sql
-- Renommer anciennes tables
ALTER TABLE territoire RENAME TO territoire_old;
ALTER TABLE election_result RENAME TO election_result_old;

-- Supprimer après validation (J+30)
DROP TABLE territoire_old CASCADE;
DROP TABLE election_result_old CASCADE;
```

---

## Métriques de Succès

### Critères d'Acceptation

| Métrique | Cible | Mesure |
|----------|-------|--------|
| **Features ML disponibles** | ≥30 | COUNT DISTINCT features |
| **R² score modèle** | ≥0.70 | Validation croisée 5-fold |
| **MAE prédiction** | ≤3% | Écart moyen prédiction vs réel |
| **Temps requête consolidée** | <500ms | `SELECT * FROM v_resultats_complets LIMIT 1000` |
| **Redondance données** | 0 | Audit normalisation 3NF |
| **Couverture métadonnées candidats** | ≥80% | % candidats avec date_naissance |

### Validation Post-Migration

```sql
-- Test 1 : Pas de redondance participation
SELECT COUNT(DISTINCT (id_election, id_territoire, type_territoire, tour))
FROM resultat_participation;
-- Résultat attendu = nombre total territoires × tours

-- Test 2 : Cohérence inscrits/votants
SELECT *
FROM resultat_participation
WHERE nombre_inscrits != nombre_votants + nombre_abstentions;
-- Résultat attendu = 0 lignes

-- Test 3 : Tous les résultats ont un territoire déclaré
SELECT COUNT(*)
FROM resultat_candidat rc
LEFT JOIN election_territoire et
  ON rc.id_election = et.id_election
  AND rc.id_territoire = et.id_territoire
  AND rc.type_territoire = et.type_territoire
WHERE et.id_election_territoire IS NULL;
-- Résultat attendu = 0
```

---

## Références

- [MCD v2.0](../database/MCD-v2.md) - Diagramme entité-association complet
- [Expertise Enrichissement](../database/EXPERTISE-ENRICHISSEMENT-SCHEMA.md) - Analyse technique détaillée
- [Analyse Data Science](../database/ANALYSE-DS-SCHEMA-v2.md) - Impact ML et ROI

---

**Décision finale :** ✅ **ACCEPTÉ** - Migration vers schéma enrichi v3.0

**Prochaines étapes :**
1. Créer migrations Alembic (Sprint 1-2-3)
2. Migrer données existantes
3. Enrichir métadonnées candidats/partis
4. Valider métriques de succès
5. Basculer vers nouveau schéma

**Date d'application :** 2026-02-11
**Responsables :** @tech, @de, @ds
