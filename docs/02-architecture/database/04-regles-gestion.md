# Règles de Gestion

**Version :** 2.0
**Date :** 2026-02-10
**Auteur :** @tech
**Statut :** Production-Ready

---

## Vue d'Ensemble

Les règles de gestion définissent les contraintes métier qui régissent les données et leur cohérence. Elles sont implémentées via :
- **Contraintes SQL** (CHECK, UNIQUE, FK)
- **Logique applicative** (validation Python/SQLAlchemy)
- **Triggers PostgreSQL** (future v3.0)

---

## RG-01 : Hiérarchie Géographique

### Énoncé
Un bureau de vote appartient à exactement 1 IRIS, qui appartient à 1 commune. Les relations hiérarchiques doivent être respectées.

### Règle Détaillée
```
BUREAU_VOTE (1) ----appartient à----> (1) IRIS
IRIS (1) -----------appartient à----> (1) COMMUNE
ARRONDISSEMENT (1) -appartient à----> (1) COMMUNE (pour grandes villes)
```

### Implémentation Actuelle (v2.0)
**Table :** `territoire`
- **Colonne :** `type_territoire` définit le niveau géographique
- **Limitation :** Pas de colonne `id_territoire_parent` (architecture plate)

**Contrainte implicite :**
- Tous les territoires d'un même `code_insee` partagent la même commune

### Validation Applicative
```python
# Exemple Python (src/database/models.py)
def valider_hierarchie(id_territoire: str, code_insee: str, type_territoire: str):
    """Valide la cohérence géographique"""
    if type_territoire == 'IRIS':
        assert id_territoire.startswith(f'IRIS_{code_insee}')
    elif type_territoire == 'BUREAU_VOTE':
        assert id_territoire.startswith(f'BV_{code_insee}_')
    # ...
```

### Évolution Future (v3.0)
**Nouvelle colonne :** `id_territoire_parent` pour arborescence explicite

```sql
ALTER TABLE territoire ADD COLUMN id_territoire_parent VARCHAR(20)
    REFERENCES territoire(id_territoire);

-- Exemple de hiérarchie
INSERT INTO territoire VALUES
    ('33063', '33063', 'COMMUNE', 'Bordeaux', ..., NULL), -- Racine
    ('IRIS_330630101', '33063', 'IRIS', '...', ..., '33063'), -- Parent = Bordeaux
    ('BV_33063_001', '33063', 'BUREAU_VOTE', '...', ..., 'IRIS_330630101'); -- Parent = IRIS
```

**Avantages :**
- Requêtes hiérarchiques simplifiées (WITH RECURSIVE)
- Agrégation automatique (IRIS → Commune)
- Contrainte référentielle stricte

---

## RG-02 : Unicité Résultats Électoraux

### Énoncé
Un candidat ne peut avoir qu'un seul résultat par territoire, année et tour. Les doublons sont strictement interdits.

### Règle Détaillée
```
POUR chaque (territoire, année, tour, candidat) :
    => 1 SEULE ligne dans election_result
```

**Cas d'erreur :**
```sql
-- ❌ ERREUR : Violation contrainte d'unicité
INSERT INTO election_result (id_territoire, annee, tour, candidat, ...)
VALUES ('BV_33063_001', 2022, 1, 'Emmanuel MACRON', ...);

INSERT INTO election_result (id_territoire, annee, tour, candidat, ...)
VALUES ('BV_33063_001', 2022, 1, 'Emmanuel MACRON', ...); -- DOUBLON
```

### Implémentation
**Contrainte :** `UNIQUE (id_territoire, annee, tour, candidat)`

```sql
CREATE TABLE election_result (
    -- ...
    UNIQUE (id_territoire, annee, tour, candidat)
);
```

**Index associé :** `uk_election_result_unique` (créé automatiquement par PostgreSQL)

### Gestion des Corrections
Si un résultat doit être corrigé :
1. **UPDATE** : Modifier la ligne existante
2. **DELETE + INSERT** : Supprimer puis réinsérer (historique perdu)

**Recommandation :** Utiliser `updated_at` pour tracer les corrections (future v3.0)

---

## RG-03 : Cohérence des Votes

### Énoncé
Les nombres de votes doivent respecter la hiérarchie suivante :
```
nombre_voix ≤ nombre_exprimes ≤ nombre_votants ≤ nombre_inscrits
```

### Règle Détaillée
| Colonne | Description | Relation |
|---------|-------------|----------|
| `nombre_inscrits` | Total inscrits au bureau | Valeur maximale |
| `nombre_votants` | Votants effectifs | ≤ `nombre_inscrits` |
| `nombre_exprimes` | Votes valides (hors blancs/nuls) | ≤ `nombre_votants` |
| `nombre_voix` | Voix pour le candidat | ≤ `nombre_exprimes` |

**Validation :**
```
nombre_voix <= nombre_exprimes <= nombre_votants <= nombre_inscrits
```

### Implémentation Actuelle (v2.0)
**Contraintes partielles :**
```sql
CHECK (nombre_voix >= 0)
CHECK (nombre_inscrits >= 0)
CHECK (nombre_votants >= 0)
CHECK (nombre_exprimes >= 0)
```

**Validation applicative :**
```python
def valider_coherence_votes(result: dict):
    """Valide la cohérence des nombres de votes"""
    assert result['nombre_voix'] <= result['nombre_exprimes'], "Voix > Exprimés"
    assert result['nombre_exprimes'] <= result['nombre_votants'], "Exprimés > Votants"
    assert result['nombre_votants'] <= result['nombre_inscrits'], "Votants > Inscrits"
```

### Évolution Future (v3.0)
**Trigger PostgreSQL :**
```sql
CREATE OR REPLACE FUNCTION check_coherence_votes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.nombre_voix > NEW.nombre_exprimes THEN
        RAISE EXCEPTION 'RG-03 : nombre_voix (%) > nombre_exprimes (%)',
            NEW.nombre_voix, NEW.nombre_exprimes;
    END IF;
    IF NEW.nombre_exprimes > NEW.nombre_votants THEN
        RAISE EXCEPTION 'RG-03 : nombre_exprimes (%) > nombre_votants (%)',
            NEW.nombre_exprimes, NEW.nombre_votants;
    END IF;
    IF NEW.nombre_votants > NEW.nombre_inscrits THEN
        RAISE EXCEPTION 'RG-03 : nombre_votants (%) > nombre_inscrits (%)',
            NEW.nombre_votants, NEW.nombre_inscrits;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_coherence_votes
    BEFORE INSERT OR UPDATE ON election_result
    FOR EACH ROW EXECUTE FUNCTION check_coherence_votes();
```

---

## RG-04 : Extensibilité Indicateurs

### Énoncé
L'ajout d'une nouvelle source socio-économique (ex: pollution, éducation) ne doit pas nécessiter de modification du schéma de base de données.

### Règle Détaillée
**Principe :** Pattern EAV (Entity-Attribute-Value) hybride
- **Table catalogue :** `type_indicateur` (définit les types)
- **Table générique :** `indicateur` (stocke les valeurs)
- **Métadonnées flexibles :** JSONB pour champs variables

### Implémentation
**Ajout d'un nouveau type :**
```sql
-- Étape 1 : Créer le type dans le catalogue
INSERT INTO type_indicateur (
    code_type, categorie, nom_affichage, description,
    unite_mesure, source_officielle, frequence, actif
) VALUES (
    'EDUCATION_TAUX_REUSSITE_BAC',
    'EDUCATION',
    'Taux de réussite au baccalauréat',
    'Pourcentage d élèves ayant obtenu le baccalauréat',
    'pourcentage',
    'DEPP',
    'ANNUEL',
    TRUE
);
-- Retourne : id_type = 21

-- Étape 2 : Insérer les données
INSERT INTO indicateur (
    id_territoire, id_type, annee, periode,
    valeur_numerique, metadata, source_detail, fiabilite
) VALUES (
    '33063', 21, 2022, NULL,
    89.5, '{"mention_tb_pct": 15.2}',
    'DEPP_BACCALAUREAT_2022', 'CONFIRME'
);
```

**Avantages :**
- ✅ Pas d'ALTER TABLE
- ✅ Schéma stable
- ✅ Requêtes ML génériques

**Trade-offs :**
- ⚠️ Jointure obligatoire avec `type_indicateur` pour connaître le type
- ⚠️ Validation JSONB en applicatif

### Schéma de Validation JSONB
**Colonne :** `type_indicateur.schema_metadata`
```json
{
  "type": "object",
  "properties": {
    "taux_pour_1000_hab": {"type": "number"},
    "evolution_n_1": {"type": "number"}
  },
  "required": ["taux_pour_1000_hab"]
}
```

---

## RG-05 : Traçabilité Prédictions

### Énoncé
Chaque prédiction doit référencer explicitement :
1. Le modèle utilisé (`modele_utilise`)
2. La version du modèle (`version_modele`)
3. Les métriques de performance (`metriques_modele`)
4. Les features ML utilisées (`features_utilisees`)

### Règle Détaillée
**Objectif :** Audit et reproductibilité des prédictions ML

**Contraintes :**
- `modele_utilise` : NOT NULL (obligatoire)
- `version_modele` : Recommandé (semantic versioning `vX.Y.Z`)
- `metriques_modele` : JSONB avec R², MAE, RMSE minimum
- `features_utilisees` : JSONB array de noms de features

### Implémentation
```sql
CREATE TABLE prediction (
    -- ...
    modele_utilise      VARCHAR(50)     NOT NULL,
    version_modele      VARCHAR(20),
    metriques_modele    JSONB,
    features_utilisees  JSONB,
    -- ...
);
```

**Exemple de données :**
```json
{
  "metriques_modele": {
    "r2": 0.72,
    "mae": 2.3,
    "rmse": 3.1,
    "cv_score_mean": 0.68,
    "train_score": 0.85
  },
  "features_utilisees": [
    "taux_chomage_2022",
    "criminalite_totale_2022",
    "population_2021",
    "densite_hab_km2",
    "macron_2022_tour1_pct"
  ]
}
```

### Validation Applicative
```python
def valider_tracabilite_prediction(pred: dict):
    """Valide la traçabilité ML"""
    assert pred['modele_utilise'] is not None, "Modèle obligatoire"

    # Valider métriques minimales
    if pred['metriques_modele']:
        metriques = pred['metriques_modele']
        assert 'r2' in metriques or 'mae' in metriques, "Métriques insuffisantes"

    # Valider format features
    if pred['features_utilisees']:
        assert isinstance(pred['features_utilisees'], list), "Features doit être une liste"
```

---

## RG-06 : Fiabilité des Données

### Énoncé
Toutes les données d'indicateurs doivent être qualifiées par un niveau de fiabilité : `CONFIRME`, `ESTIME`, `PROVISOIRE`, `REVISION`.

### Règle Détaillée
| Niveau | Description | Usage |
|--------|-------------|-------|
| `CONFIRME` | Donnée officielle validée | Données INSEE définitives |
| `ESTIME` | Estimation statistique | Projections démographiques |
| `PROVISOIRE` | Donnée préliminaire | Chiffres trimestriels avant révision |
| `REVISION` | Révision d'une donnée antérieure | Correction erreur source |

### Implémentation
**Colonne :** `indicateur.fiabilite`
```sql
fiabilite VARCHAR(20) DEFAULT 'CONFIRME'
    CHECK (fiabilite IN ('CONFIRME', 'ESTIME', 'PROVISOIRE', 'REVISION'))
```

### Exemples
```sql
-- Donnée officielle INSEE
INSERT INTO indicateur (..., fiabilite) VALUES (..., 'CONFIRME');

-- Projection démographique
INSERT INTO indicateur (..., fiabilite) VALUES (..., 'ESTIME');

-- Chiffres trimestriels provisoires
INSERT INTO indicateur (..., fiabilite) VALUES (..., 'PROVISOIRE');
```

### Utilisation en ML
**Recommandation :** Filtrer `fiabilite = 'CONFIRME'` pour entraînement modèle
```python
# Requête Python/SQLAlchemy
query = session.query(Indicateur).filter(
    Indicateur.fiabilite == 'CONFIRME',
    Indicateur.annee.between(2017, 2022)
)
```

---

## RG-07 : Soft Delete des Types d'Indicateurs

### Énoncé
Les types d'indicateurs ne sont jamais supprimés physiquement de la base, mais désactivés via la colonne `actif = FALSE`.

### Règle Détaillée
**Objectif :** Préserver l'intégrité référentielle et l'historique

**Contrainte FK :**
```sql
FOREIGN KEY (id_type) REFERENCES type_indicateur(id_type)
    ON DELETE RESTRICT  -- Impossible de supprimer si indicateurs existent
```

**Alternative :** Soft delete via `actif = FALSE`

### Implémentation
**Colonne :** `type_indicateur.actif`
```sql
actif BOOLEAN DEFAULT TRUE
```

**Désactivation d'un type :**
```sql
-- ❌ ERREUR : Suppression physique impossible si indicateurs existent
DELETE FROM type_indicateur WHERE id_type = 5;
-- ERROR: update or delete on table "type_indicateur" violates foreign key constraint

-- ✅ Solution : Soft delete
UPDATE type_indicateur SET actif = FALSE WHERE id_type = 5;
```

### Filtrage en Requêtes
```sql
-- Lister uniquement les types actifs
SELECT * FROM type_indicateur WHERE actif = TRUE;

-- Lister tous les types (y compris désactivés)
SELECT * FROM type_indicateur;
```

### Validation Applicative
```python
# Empêcher l'insertion d'indicateurs avec type inactif
def valider_type_actif(id_type: int):
    type_ind = session.query(TypeIndicateur).get(id_type)
    if not type_ind.actif:
        raise ValueError(f"Type {id_type} est désactivé (actif=FALSE)")
```

---

## Récapitulatif

| Règle | Implémentation | Statut v2.0 | Évolution v3.0 |
|-------|----------------|-------------|----------------|
| **RG-01** Hiérarchie géographique | `type_territoire` | ✅ Partiel | Colonne `id_territoire_parent` |
| **RG-02** Unicité résultats | `UNIQUE (terr, année, tour, candidat)` | ✅ Complet | - |
| **RG-03** Cohérence votes | Validation applicative | ✅ Partiel | Trigger PostgreSQL |
| **RG-04** Extensibilité indicateurs | Pattern EAV + JSONB | ✅ Complet | - |
| **RG-05** Traçabilité prédictions | Colonnes `modele_*`, `metriques_*` | ✅ Complet | - |
| **RG-06** Fiabilité données | Colonne `fiabilite` + CHECK | ✅ Complet | - |
| **RG-07** Soft delete types | Colonne `actif` + RESTRICT | ✅ Complet | - |

---

**Prochaine étape :** Consulter les [Contraintes d'Intégrité](05-contraintes-integrite.md) pour détails techniques des contraintes SQL.
