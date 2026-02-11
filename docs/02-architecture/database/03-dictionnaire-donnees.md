# Dictionnaire de Données

**Version :** 2.0
**Date :** 2026-02-10
**Auteur :** @tech
**Statut :** Production-Ready

---

## Vue d'Ensemble

Le dictionnaire de données documente exhaustivement chaque colonne des 5 tables du schéma v2.0 :
- Types de données PostgreSQL
- Contraintes et valeurs par défaut
- Description fonctionnelle
- Exemples de valeurs

---

## Table 1 : `territoire`

**Description :** Référentiel géographique centralisant les divisions territoriales (IRIS, Bureaux de vote, Communes, Arrondissements).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_territoire` | VARCHAR(20) | ✗ | PK | Identifiant unique territoire (code INSEE ou composite) | `'33063'`, `'IRIS_330630101'`, `'BV_33063_001'` |
| 2 | `code_insee` | VARCHAR(5) | ✗ | | Code INSEE de la commune de rattachement | `'33063'` (Bordeaux) |
| 3 | `type_territoire` | VARCHAR(20) | ✗ | CHECK IN | Type géographique (`COMMUNE`, `IRIS`, `BUREAU_VOTE`, `ARRONDISSEMENT`) | `'COMMUNE'`, `'IRIS'` |
| 4 | `nom_territoire` | VARCHAR(100) | ✗ | | Nom lisible pour affichage | `'Bordeaux'`, `'Bordeaux Centre IRIS 0101'` |
| 5 | `geometry` | GEOMETRY(POLYGON, 4326) | ✓ | | Polygone géométrique WGS84 (PostGIS) | `POLYGON((...))`  |
| 6 | `population` | INTEGER | ✓ | ≥ 0 | Population totale (dernière donnée INSEE) | `252040`, `5000`, `800` |
| 7 | `metadata` | JSONB | ✓ | | Métadonnées flexibles (superficie, densité, etc.) | `{"superficie_km2": 49.36, "densite": 5103}` |
| 8 | `created_at` | TIMESTAMP | ✓ | DEFAULT NOW() | Date de création de l'enregistrement | `'2026-02-10 10:30:00'` |
| 9 | `updated_at` | TIMESTAMP | ✓ | DEFAULT NOW() | Date de dernière modification | `'2026-02-10 14:20:00'` |

### Notes
- **`id_territoire`** : Format libre permettant codes INSEE (`33063`) ou composites (`IRIS_330630101`)
- **`geometry`** : Utilise système de coordonnées WGS84 (SRID 4326) - standard GPS
- **`metadata`** : Champs flexibles selon type (ex: `arrondissement_parent` pour IRIS)

---

## Table 2 : `type_indicateur`

**Description :** Catalogue référençant tous les types d'indicateurs socio-économiques disponibles (Sécurité, Emploi, Démographie).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_type` | SERIAL | ✗ | PK | Identifiant auto-incrémenté | `1`, `2`, `3` |
| 2 | `code_type` | VARCHAR(50) | ✗ | UNIQUE | Code identifiant unique du type | `'SECURITE_CAMBRIOLAGES'`, `'EMPLOI_TAUX_CHOMAGE'` |
| 3 | `categorie` | VARCHAR(50) | ✗ | | Catégorie macro regroupant les types | `'SECURITE'`, `'EMPLOI'`, `'DEMOGRAPHIE'` |
| 4 | `nom_affichage` | VARCHAR(100) | ✗ | | Libellé interface utilisateur | `'Cambriolages de logement'`, `'Taux de chômage'` |
| 5 | `description` | TEXT | ✓ | | Description détaillée de l'indicateur | `'Nombre de cambriolages de résidences principales signalés aux forces de sécurité'` |
| 6 | `unite_mesure` | VARCHAR(50) | ✓ | | Unité de la valeur (`nombre`, `pourcentage`, `euros`, etc.) | `'nombre'`, `'pourcentage'`, `'taux_pour_1000_hab'` |
| 7 | `source_officielle` | VARCHAR(100) | ✓ | | Organisme source officiel | `'SSMSI'` (sécurité), `'INSEE'` (emploi/démo) |
| 8 | `frequence` | VARCHAR(20) | ✓ | | Périodicité de mise à jour | `'ANNUEL'`, `'TRIMESTRIEL'`, `'MENSUEL'` |
| 9 | `date_debut_disponibilite` | DATE | ✓ | | Première année où les données sont disponibles | `'2017-01-01'`, `'2015-01-01'` |
| 10 | `actif` | BOOLEAN | ✓ | DEFAULT TRUE | Indicateur activé (permet soft delete) | `TRUE`, `FALSE` |
| 11 | `schema_metadata` | JSONB | ✓ | | Schéma JSON de validation pour `indicateur.metadata` | `{"type": "object", "properties": {...}}` |
| 12 | `created_at` | TIMESTAMP | ✓ | DEFAULT NOW() | Date de création du type | `'2026-02-10 09:00:00'` |

### Notes
- **`code_type`** : Convention de nommage `CATEGORIE_NOM_SPECIFIQUE` (ex: `SECURITE_VOLS_VEHICULES`)
- **`actif`** : Permet de désactiver un type sans le supprimer (règle métier RG-07)
- **`schema_metadata`** : Schéma JSON Schema pour valider les métadonnées dans table `indicateur`

### Exemples de types pré-chargés

| id_type | code_type | categorie | nom_affichage | unite_mesure |
|---------|-----------|-----------|---------------|--------------|
| 1 | `SECURITE_CAMBRIOLAGES` | SECURITE | Cambriolages de logement | nombre |
| 2 | `SECURITE_VOLS_VEHICULES` | SECURITE | Vols de véhicules | nombre |
| 3 | `EMPLOI_TAUX_CHOMAGE` | EMPLOI | Taux de chômage | pourcentage |
| 4 | `DEMO_POPULATION` | DEMOGRAPHIE | Population totale | nombre |

---

## Table 3 : `indicateur`

**Description :** Table générique stockant TOUS les indicateurs socio-économiques (Pattern EAV). Permet l'ajout de nouvelles sources sans modification de schéma.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_indicateur` | BIGSERIAL | ✗ | PK | Identifiant auto-incrémenté | `1`, `2`, `3` |
| 2 | `id_territoire` | VARCHAR(20) | ✗ | FK → territoire | Référence au territoire concerné | `'33063'`, `'IRIS_330630101'` |
| 3 | `id_type` | INTEGER | ✗ | FK → type_indicateur | Référence au type d'indicateur | `1` (cambriolages), `2` (vols) |
| 4 | `annee` | INTEGER | ✗ | [2000,2100] | Année de référence de l'indicateur | `2017`, `2022` |
| 5 | `periode` | VARCHAR(20) | ✓ | | Période infra-annuelle si applicable (`T1`, `M03`, etc.) | `'T1'`, `'M03'`, `NULL` (annuel) |
| 6 | `valeur_numerique` | DECIMAL(15,4) | ✓ | | Valeur principale (nombre, pourcentage, montant) | `504.0`, `8.5`, `252040.0` |
| 7 | `valeur_texte` | TEXT | ✓ | | Valeur qualitative si applicable | `'Élevé'`, `'Stable'`, `NULL` |
| 8 | `metadata` | JSONB | ✓ | | Métadonnées spécifiques au type (validées par `type_indicateur.schema_metadata`) | `{"taux_pour_1000_hab": 2.0, "evolution_n_1": -5.2}` |
| 9 | `source_detail` | VARCHAR(200) | ✓ | | Source précise (version dataset, URL, etc.) | `'SSMSI_2024_GEOGRAPHIE2025'`, `'INSEE_RP2021'` |
| 10 | `fiabilite` | VARCHAR(20) | ✓ | DEFAULT 'CONFIRME' | Niveau de fiabilité (`CONFIRME`, `ESTIME`, `PROVISOIRE`, `REVISION`) | `'CONFIRME'`, `'ESTIME'` |
| 11 | `created_at` | TIMESTAMP | ✓ | DEFAULT NOW() | Date d'insertion de l'enregistrement | `'2026-02-10 11:00:00'` |

### Contrainte d'unicité
**UK :** `(id_territoire, id_type, annee, periode)`
- Évite les doublons : 1 seule valeur par territoire/type/année/période

### Notes
- **`valeur_numerique`** : Colonne principale (80% des cas) - utilisée pour ML
- **`valeur_texte`** : Utilisée pour données qualitatives (rares)
- **`metadata`** : Champs variables selon type (ex: taux normalisés, comparaisons temporelles)
- **`fiabilite`** : Règle métier RG-06 pour qualifier la source

### Exemples de données

| id_indicateur | id_territoire | id_type | annee | periode | valeur_numerique | fiabilite |
|---------------|---------------|---------|-------|---------|------------------|-----------|
| 1 | `33063` | 1 | 2022 | NULL | 504.0 | CONFIRME |
| 2 | `33063` | 3 | 2022 | T1 | 8.5 | ESTIME |
| 3 | `IRIS_330630101` | 4 | 2021 | NULL | 5000.0 | CONFIRME |

---

## Table 4 : `election_result`

**Description :** Résultats électoraux présidentielles 2017 & 2022 (1er et 2nd tours). Table spécialisée pour performance et intégrité.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_result` | BIGSERIAL | ✗ | PK | Identifiant auto-incrémenté | `1`, `2`, `3` |
| 2 | `id_territoire` | VARCHAR(20) | ✗ | FK → territoire | Référence au bureau de vote ou IRIS | `'BV_33063_001'`, `'IRIS_330630101'` |
| 3 | `annee` | INTEGER | ✗ | [2000,2100] | Année de l'élection | `2017`, `2022` |
| 4 | `tour` | INTEGER | ✗ | {1, 2} | Numéro du tour (1 ou 2) | `1`, `2` |
| 5 | `candidat` | VARCHAR(100) | ✗ | | Nom complet du candidat | `'Emmanuel MACRON'`, `'Marine LE PEN'` |
| 6 | `parti` | VARCHAR(50) | ✓ | | Parti politique (sigle) | `'LREM'`, `'RN'`, `'LFI'`, `'LR'` |
| 7 | `nombre_voix` | INTEGER | ✗ | ≥ 0 | Nombre de voix obtenues | `1250`, `450` |
| 8 | `pourcentage_voix` | DECIMAL(5,2) | ✗ | [0,100] | Pourcentage des voix exprimées | `28.45`, `20.22` |
| 9 | `nombre_inscrits` | INTEGER | ✗ | ≥ 0 | Nombre d'inscrits au bureau | `4500` |
| 10 | `nombre_votants` | INTEGER | ✗ | ≥ 0 | Nombre de votants (participations) | `3390` |
| 11 | `nombre_exprimes` | INTEGER | ✗ | ≥ 0 | Nombre de voix exprimées (votes valides) | `3300` |
| 12 | `taux_participation` | DECIMAL(5,2) | ✗ | [0,100] | Taux de participation (%) | `75.33`, `78.50` |
| 13 | `metadata` | JSONB | ✓ | | Métadonnées additionnelles (nuance, étiquette, etc.) | `{"nuance": "EXG", "candidat_sortant": true}` |
| 14 | `created_at` | TIMESTAMP | ✓ | DEFAULT NOW() | Date d'insertion de l'enregistrement | `'2026-02-10 12:00:00'` |

### Contrainte d'unicité
**UK :** `(id_territoire, annee, tour, candidat)`
- 1 seule ligne par candidat/bureau/tour (règle métier RG-02)

### Notes
- **Cohérence votes (RG-03) :** `nombre_voix ≤ nombre_exprimes ≤ nombre_votants ≤ nombre_inscrits`
  - Validé en applicatif (trigger optionnel en v3.0)
- **`candidat`** : Nom complet en MAJUSCULES (standardisé)
- **`parti`** : Sigle officiel ou `NULL` si candidat sans étiquette

### Exemples de données

| id_result | id_territoire | annee | tour | candidat | parti | nombre_voix | pourcentage_voix | taux_participation |
|-----------|---------------|-------|------|----------|-------|-------------|------------------|--------------------|
| 1 | `BV_33063_001` | 2022 | 1 | Emmanuel MACRON | LREM | 450 | 28.45 | 75.33 |
| 2 | `BV_33063_001` | 2022 | 1 | Marine LE PEN | RN | 320 | 20.22 | 75.33 |
| 3 | `BV_33063_001` | 2022 | 2 | Emmanuel MACRON | LREM | 625 | 58.74 | 78.50 |

---

## Table 5 : `prediction`

**Description :** Prédictions électorales 2027 générées par les modèles Machine Learning. Traçabilité complète (modèle, version, métriques).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_prediction` | BIGSERIAL | ✗ | PK | Identifiant auto-incrémenté | `1`, `2`, `3` |
| 2 | `id_territoire` | VARCHAR(20) | ✗ | FK → territoire | Référence au territoire de prédiction | `'IRIS_330630101'`, `'BV_33063_001'` |
| 3 | `candidat` | VARCHAR(100) | ✗ | | Nom du candidat prédit | `'Emmanuel MACRON'`, `'Marine LE PEN'` |
| 4 | `parti` | VARCHAR(50) | ✓ | | Parti politique anticipé | `'RE'`, `'RN'`, `'LFI'` |
| 5 | `annee_prediction` | INTEGER | ✓ | [2025,2050] | Année de l'élection prédite | `2027`, `2032` |
| 6 | `tour` | INTEGER | ✗ | {1, 2} | Tour prédit (1 ou 2) | `1`, `2` |
| 7 | `pourcentage_predit` | DECIMAL(5,2) | ✗ | [0,100] | Pourcentage de voix prédit | `32.15`, `25.30` |
| 8 | `intervalle_confiance_inf` | DECIMAL(5,2) | ✓ | [0,100] | Borne inférieure intervalle confiance 95% | `29.80`, `23.10` |
| 9 | `intervalle_confiance_sup` | DECIMAL(5,2) | ✓ | [0,100] | Borne supérieure intervalle confiance 95% | `34.50`, `27.50` |
| 10 | `modele_utilise` | VARCHAR(50) | ✗ | | Nom de l'algorithme ML | `'RandomForest'`, `'XGBoost'`, `'LinearRegression'` |
| 11 | `version_modele` | VARCHAR(20) | ✓ | | Version du modèle (semantic versioning) | `'v1.2.0'`, `'v2.0.0-beta'` |
| 12 | `metriques_modele` | JSONB | ✓ | | Métriques de performance (R², MAE, RMSE, etc.) | `{"r2": 0.72, "mae": 2.3, "rmse": 3.1}` |
| 13 | `features_utilisees` | JSONB | ✓ | | Liste des features ML utilisées | `["taux_chomage", "criminalite_totale", "population"]` |
| 14 | `date_generation` | TIMESTAMP | ✓ | DEFAULT NOW() | Date/heure de génération de la prédiction | `'2026-02-10 15:00:00'` |

### Contrainte d'unicité
**UK :** `(id_territoire, candidat, tour, annee_prediction, version_modele)`
- Permet versioning des prédictions (plusieurs modèles/versions)

### Notes
- **Traçabilité (RG-05) :** Toutes prédictions référencent le modèle et ses métriques
- **`intervalle_confiance_*`** : Calculé selon `confidence_level` du modèle (95% standard)
- **`metriques_modele`** : Métriques calculées sur jeu de test (cross-validation)
- **`features_utilisees`** : Permet audit des variables explicatives

### Exemples de données

| id_prediction | id_territoire | candidat | tour | pourcentage_predit | IC_inf | IC_sup | modele_utilise | version | R² |
|---------------|---------------|----------|------|--------------------|--------|--------|----------------|---------|-----|
| 1 | `IRIS_330630101` | Emmanuel MACRON | 1 | 32.15 | 29.80 | 34.50 | RandomForest | v1.2.0 | 0.72 |
| 2 | `IRIS_330630101` | Marine LE PEN | 1 | 25.30 | 23.10 | 27.50 | RandomForest | v1.2.0 | 0.72 |
| 3 | `IRIS_330630101` | Emmanuel MACRON | 2 | 58.20 | 55.00 | 61.40 | XGBoost | v2.0.0 | 0.78 |

---

## Types de Données PostgreSQL

### Types Scalaires

| Type SQL | Description | Exemple |
|----------|-------------|---------|
| `VARCHAR(n)` | Chaîne de caractères variable (max n) | `'Bordeaux'` |
| `INTEGER` | Entier 32 bits (-2B à +2B) | `252040` |
| `BIGINT` | Entier 64 bits | `9223372036854775807` |
| `SERIAL` | Auto-incrémenté INTEGER | `1, 2, 3...` |
| `BIGSERIAL` | Auto-incrémenté BIGINT | `1, 2, 3...` |
| `DECIMAL(p,s)` | Nombre décimal (précision p, échelle s) | `28.45` (DECIMAL(5,2)) |
| `BOOLEAN` | Booléen | `TRUE`, `FALSE` |
| `DATE` | Date | `'2017-01-01'` |
| `TIMESTAMP` | Date + heure | `'2026-02-10 10:30:00'` |

### Types Avancés

| Type SQL | Description | Extension | Exemple |
|----------|-------------|-----------|---------|
| `JSONB` | JSON binaire indexable | Core | `{"key": "value"}` |
| `GEOMETRY(POLYGON, 4326)` | Géométrie polygonale WGS84 | PostGIS | `POLYGON((...))` |

---

## Conventions de Nommage

### Tables
- **Format :** `snake_case` (minuscules + underscores)
- **Exemples :** `territoire`, `election_result`, `type_indicateur`

### Colonnes
- **Format :** `snake_case`
- **Exemples :** `id_territoire`, `pourcentage_voix`, `created_at`

### Clés étrangères
- **Préfixe :** `id_` + nom table référencée
- **Exemples :** `id_territoire`, `id_type`

### Contraintes
- **PK :** `pk_<table>`
- **FK :** `fk_<table_enfant>_<table_parent>`
- **UK :** `uk_<table>_<colonnes>`
- **CK :** `ck_<table>_<colonne>`

---

## Métadonnées JSONB - Exemples

### Table `territoire.metadata`
```json
{
  "superficie_km2": 49.36,
  "densite_hab_km2": 5103,
  "arrondissement_parent": "Bordeaux Centre",
  "code_iris_complet": "330630101"
}
```

### Table `indicateur.metadata`
```json
{
  "taux_pour_1000_hab": 2.0,
  "evolution_annee_precedente": -5.2,
  "rang_national": 45,
  "confiance_estimation": "HAUTE"
}
```

### Table `election_result.metadata`
```json
{
  "nuance": "EXG",
  "candidat_sortant": true,
  "nombre_blancs": 50,
  "nombre_nuls": 40
}
```

### Table `prediction.metriques_modele`
```json
{
  "r2": 0.72,
  "mae": 2.3,
  "rmse": 3.1,
  "cv_score_mean": 0.68,
  "cv_score_std": 0.05,
  "train_score": 0.85
}
```

### Table `prediction.features_utilisees`
```json
[
  "taux_chomage_2022",
  "criminalite_totale_2022",
  "population_2021",
  "densite_hab_km2",
  "evolution_demographique_5ans",
  "macron_2022_tour1_pct"
]
```

---

**Prochaine étape :** Consulter les [Règles de Gestion](04-regles-gestion.md) pour comprendre les règles métier implémentées.
