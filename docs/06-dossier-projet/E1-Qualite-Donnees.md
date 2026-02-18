# E1 - Qualite des Donnees

> **Competence C8 :** Assurer la qualite des donnees en utilisant les outils de gestion de la qualite pour garantir l'exactitude, la coherence, la synchronisation et la tracabilite des donnees.

---

## 1. Strategie qualite

```mermaid
flowchart LR
    A["SOURCES\nAPIs publiques\ndata.gouv.fr"] --> B["VALIDATION ETL\n14 validators Python\ncolonnes, types,\nbornes, unicite"]
    B --> C["CONTRAINTES BDD\nFK, UNIQUE,\nCHECK 0-100%"]
    C --> D["CODE REVIEW\n2 revues\n7/10"]

    style A fill:#3498db,color:#fff
    style B fill:#f39c12,color:#fff
    style C fill:#2ecc71,color:#fff
    style D fill:#9b59b6,color:#fff
```

## 2. Validation ETL (14 fonctions)

Implementees dans `src/etl/load/utils/validators.py` :

| Validation | Garantie |
|------------|----------|
| `validate_csv_exists` | Le fichier source existe |
| `validate_dataframe_not_empty` | Le dataset n'est pas vide |
| `validate_required_columns` | Toutes les colonnes attendues sont presentes |
| `validate_no_nulls` | Pas de valeurs NULL sur les colonnes obligatoires |
| `validate_year_range` | Annees dans les bornes attendues |
| `validate_positive_values` | Valeurs numeriques positives |
| `validate_percentage_range` | Pourcentages entre 0 et 100 |
| `validate_unique_key` | Cles primaires uniques (pas de doublons) |
| `validate_elections_data` | Coherence donnees electorales |
| `validate_participation_data` | Somme votants + abstentions = inscrits |
| `validate_indicateurs_data` | Indicateurs securite coherents |
| `validate_geographie_data` | Codes INSEE valides |

## 3. Contraintes en base de donnees

| Type | Nombre | Exemples |
|------|--------|---------|
| PRIMARY KEY | 17 | `commune.id_commune`, `prediction.id_prediction` |
| FOREIGN KEY | 12 | `commune.id_departement → departement` |
| UNIQUE | 8 | `(territoire, candidat, tour, annee, version)` |
| CHECK | 10 | `pourcentage BETWEEN 0 AND 100`, `tour IN (1,2)` |
| NOT NULL | ~50 | Colonnes obligatoires |
| INDEX | 15 | Composites sur `(id_territoire, type_territoire)` |

## 4. Traitements qualite appliques

| Probleme detecte | Traitement | Impact |
|-------------------|-----------|--------|
| IDs territoire 7 chars vs 5 chars | Normalisation `str[2:]` | 14 484 lignes corrigees |
| Pourcentages NULL (0 voix) | `fillna(0)` | 745 lignes |
| Nombres format francais | Parsing `1.234,56` → `1234.56` | Indicateurs securite |
| Doublons potentiels | Contraintes UNIQUE en BDD | Prevention automatique |

## 5. Revues de code

| Revue | Score | Problemes | Resolution |
|-------|-------|-----------|------------|
| Review 1 | 6.5/10 | 15 CRITICAL + 35 MAJOR | Corrections appliquees |
| Review 2 | **7/10** | Tous CRITICAL/MAJOR resolus | Valide |

Corrections majeures : requetes parametrees (SQL injection), singleton engine, transaction safety, vectorisation transform.

## 6. Tracabilite

| Element | Mecanisme |
|---------|-----------|
| Sources de donnees | Documentees dans `SOURCES_DONNEES.md` avec URLs et licences |
| Versions schema | 4 migrations Alembic tracees |
| Predictions ML | Version modele (`v1.0.0`), metriques et features en JSONB |
| Modifications code | Git (historique complet des commits) |

**Fichiers de reference :**
- Validators : `src/etl/load/utils/validators.py`
- Contraintes : `docs/02-architecture/database/05-contraintes-integrite.md`
- Code review : `docs/03-code-review/`
