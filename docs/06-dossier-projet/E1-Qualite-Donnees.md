# E1 - Qualité des Données

> **Compétence C8 :** Assurer la qualité des données en utilisant les outils de gestion de la qualité pour garantir l'exactitude, la cohérence, la synchronisation et la traçabilité des données.

---

## 1. Stratégie qualité

```mermaid
flowchart LR
    A["SOURCES\nAPIs publiques\ndata.gouv.fr"] --> B["VALIDATION ETL\n14 validators Python\ncolonnes, types,\nbornes, unicité"]
    B --> C["CONTRAINTES BDD\nFK, UNIQUE,\nCHECK 0-100%"]
    C --> D["CODE REVIEW\n2 revues\n7/10"]

    style A fill:#3498db,color:#fff
    style B fill:#f39c12,color:#fff
    style C fill:#2ecc71,color:#fff
    style D fill:#9b59b6,color:#fff
```

## 2. Validation ETL (14 fonctions)

Implémentées dans `src/etl/load/utils/validators.py` :

| Validation | Garantie |
|------------|----------|
| `validate_csv_exists` | Le fichier source existe |
| `validate_dataframe_not_empty` | Le dataset n'est pas vide |
| `validate_required_columns` | Toutes les colonnes attendues sont présentes |
| `validate_no_nulls` | Pas de valeurs NULL sur les colonnes obligatoires |
| `validate_year_range` | Années dans les bornes attendues |
| `validate_positive_values` | Valeurs numériques positives |
| `validate_percentage_range` | Pourcentages entre 0 et 100 |
| `validate_unique_key` | Clés primaires uniques (pas de doublons) |
| `validate_elections_data` | Cohérence données électorales |
| `validate_participation_data` | Somme votants + abstentions = inscrits |
| `validate_indicateurs_data` | Indicateurs sécurité cohérents |
| `validate_geographie_data` | Codes INSEE valides |

## 3. Contraintes en base de données

| Type | Nombre | Exemples |
|------|--------|---------|
| PRIMARY KEY | 17 | `commune.id_commune`, `prediction.id_prediction` |
| FOREIGN KEY | 12 | `commune.id_departement → departement` |
| UNIQUE | 8 | `(territoire, candidat, tour, annee, version)` |
| CHECK | 10 | `pourcentage BETWEEN 0 AND 100`, `tour IN (1,2)` |
| NOT NULL | ~50 | Colonnes obligatoires |
| INDEX | 15 | Composites sur `(id_territoire, type_territoire)` |

## 4. Traitements qualité appliqués

| Problème détecté | Traitement | Impact |
|-------------------|-----------|--------|
| IDs territoire 7 chars vs 5 chars | Normalisation `str[2:]` | 14 484 lignes corrigées |
| Pourcentages NULL (0 voix) | `fillna(0)` | 745 lignes |
| Nombres format français | Parsing `1.234,56` → `1234.56` | Indicateurs sécurité |
| Doublons potentiels | Contraintes UNIQUE en BDD | Prévention automatique |

## 5. Revues de code

| Revue | Score | Problèmes | Résolution |
|-------|-------|-----------|------------|
| Review 1 | 6.5/10 | 15 CRITICAL + 35 MAJOR | Corrections appliquées |
| Review 2 | **7/10** | Tous CRITICAL/MAJOR résolus | Validé |

Corrections majeures : requêtes paramétrées (SQL injection), singleton engine, transaction safety, vectorisation transform.

## 6. Traçabilité

| Élément | Mécanisme |
|---------|-----------|
| Sources de données | Documentées dans `SOURCES_DONNEES.md` avec URLs et licences |
| Versions schéma | 4 migrations Alembic tracées |
| Prédictions ML | Version modèle (`v1.0.0`), métriques et features en JSONB |
| Modifications code | Git (historique complet des commits) |

**Fichiers de référence :**
- Validators : `src/etl/load/utils/validators.py`
- Contraintes : `docs/02-architecture/database/05-contraintes-integrite.md`
- Code review : `docs/03-code-review/`
