# Module Load - ETL Electio-Analytics

**Module :** `src/etl/load/`
**Stack :** SQLAlchemy 2.0 + PostgreSQL 15 + Batch Loading
**Auteur :** @de (Data Engineer)
**Supervisé par :** @tech (Tech Lead)

---

## Vue d'ensemble

Module de chargement des données transformées dans PostgreSQL.

**Fonctionnalités :**
- Validation des données avant insertion
- Chargement par batch (1000 lignes/batch)
- Détection automatique des doublons
- Mapping automatique code_type → id_type
- Gestion des transactions SQLAlchemy

---

## Structure

```
src/etl/load/
├── README.md                 ← Vous êtes ici
├── __init__.py               ← Export pipeline principal
├── main.py                   ← Orchestrateur Load
├── config/
│   ├── __init__.py           ← Export configuration
│   └── settings.py           ← Constantes et catalogue
├── core/
│   ├── __init__.py           ← Export fonctions core
│   ├── type_indicateur.py    ← Chargement catalogue
│   ├── territoire.py         ← Chargement Bordeaux
│   ├── elections.py          ← Chargement résultats électoraux
│   └── indicateurs.py        ← Chargement indicateurs
└── utils/
    ├── __init__.py           ← Export validators
    └── validators.py         ← Validations pré-insertion
```

---

## Quick Start

### 1. Prérequis

- PostgreSQL démarré (`docker-compose up -d`)
- Migrations appliquées (`alembic upgrade head`)
- Données transformées disponibles dans `data/processed/`

### 2. Exécution complète

```bash
# Lancer tout le pipeline Load
python -m src.etl.load.main
```

### 3. Exécution étape par étape

```python
from src.etl.load import (
    run_load_types_indicateurs,
    run_load_territoire,
    run_load_elections,
    run_load_securite,
)

# 1. Charger catalogue types d'indicateurs
run_load_types_indicateurs()

# 2. Charger territoire Bordeaux
run_load_territoire()

# 3. Charger résultats électoraux
run_load_elections()

# 4. Charger indicateurs de sécurité
run_load_securite()
```

---

## Modules Core

### 1. `type_indicateur.py` ✅

Charge le catalogue statique de types d'indicateurs depuis `config.TYPES_INDICATEURS`.

**Usage :**
```bash
python -m src.etl.load.core.type_indicateur
```

**Données chargées :**
- 5 types de sécurité (CRIMINALITE_TOTALE, VOLS_SANS_VIOLENCE, VOLS_AVEC_VIOLENCE, ATTEINTES_AUX_BIENS, ATTEINTES_AUX_PERSONNES)
- Catégorie : SECURITE
- Source : SSMSI
- Fréquence : ANNUEL

**Table cible :** `type_indicateur`

---

### 2. `territoire.py` ✅

Charge le territoire Bordeaux depuis les constantes de configuration.

**Usage :**
```bash
python -m src.etl.load.core.territoire
```

**Données chargées :**
- Code INSEE : 33063
- Nom : Bordeaux
- Type : COMMUNE
- Population : 252,040 habitants (2023)

**Table cible :** `territoire`

---

### 3. `elections.py` ✅

Charge les résultats électoraux depuis CSV transformé.

**Usage :**
```bash
python -m src.etl.load.core.elections
```

**Entrée :**
- `data/processed/elections/resultats_elections_bordeaux.csv`

**Colonnes requises :**
- id_territoire, annee, tour, candidat, nombre_voix, pourcentage_voix

**Validations :**
- Années valides : [2017, 2022]
- Tours valides : [1, 2]
- Pourcentages : [0, 100]
- Clé unique : (id_territoire, annee, tour, candidat)

**Table cible :** `election_result`

---

### 4. `indicateurs.py` ✅

Charge les indicateurs socio-économiques depuis CSV transformé.

**Usage :**
```bash
python -m src.etl.load.core.indicateurs
```

**Entrée :**
- `data/processed/indicateurs/delinquance_bordeaux.csv`

**Colonnes requises :**
- id_territoire, code_type, annee, valeur_numerique

**Validations :**
- Années valides : [2016-2024]
- Valeurs : >= 0
- Clé unique : (id_territoire, code_type, annee)
- Mapping automatique : code_type → id_type

**Table cible :** `indicateur`

---

## Utilitaires de Validation

### Validations génériques

| Fonction | Description |
|----------|-------------|
| `validate_csv_exists` | Vérifie existence fichier CSV |
| `validate_dataframe_not_empty` | Vérifie DataFrame non vide |
| `validate_required_columns` | Vérifie colonnes requises |
| `validate_no_nulls` | Vérifie absence de NULL |
| `validate_year_range` | Vérifie années valides |
| `validate_positive_values` | Vérifie valeurs >= 0 |
| `validate_percentage_range` | Vérifie pourcentages [0, 100] |
| `validate_unique_key` | Vérifie absence de doublons |

### Validations spécifiques

| Fonction | Description |
|----------|-------------|
| `validate_elections_data` | Validation complète résultats électoraux |
| `validate_indicateurs_data` | Validation complète indicateurs |

---

## Configuration

### Chemins CSV

Définis dans `config/settings.py` :

```python
ELECTIONS_CSV = PROJECT_ROOT / "data/processed/elections/resultats_elections_bordeaux.csv"
SECURITE_CSV = PROJECT_ROOT / "data/processed/indicateurs/delinquance_bordeaux.csv"
```

### Paramètres Batch

```python
BATCH_SIZE = 1000  # Lignes par batch
VERBOSE = True     # Mode verbose
```

### Années valides

```python
ANNEES_ELECTIONS_VALIDES = [2017, 2022]
ANNEES_INDICATEURS_VALIDES = list(range(2016, 2025))
TOURS_VALIDES = [1, 2]
```

---

## Ordre d'exécution

**IMPORTANT** : L'ordre est critique en raison des contraintes Foreign Key.

```
1. type_indicateur (référentiel)
   └─> Aucune dépendance

2. territoire (référentiel)
   └─> Aucune dépendance

3. election_result (données)
   └─> Dépend de : territoire (FK id_territoire)

4. indicateur (données)
   └─> Dépend de : territoire (FK id_territoire)
   └─> Dépend de : type_indicateur (FK id_type)
```

---

## Gestion des erreurs

### Doublons

Les doublons sont détectés automatiquement avant insertion :

```python
existing = session.query(ElectionResult).filter(
    ElectionResult.id_territoire == row["id_territoire"],
    ElectionResult.annee == row["annee"],
    ElectionResult.tour == row["tour"],
    ElectionResult.candidat == row["candidat"],
).first()

if existing:
    continue  # Passer la ligne
```

### Validation échouée

Si la validation échoue, une `ValueError` est levée :

```python
validate_elections_data(df, "resultats_elections_bordeaux.csv")
# ValueError: Années invalides dans source : [2023, 2024]
```

### Type inconnu

Si un `code_type` n'existe pas dans `type_indicateur` :

```python
if code_type not in type_mapping:
    print(f"⚠️  Type inconnu ignoré : {code_type}")
    continue
```

---

## Exemple de sortie

```
================================================================================
                    ETL LOAD - ELECTIO-ANALYTICS
================================================================================
📅 Date : 2026-02-11 14:30:15
🎯 Cible : PostgreSQL (electio_analytics)
================================================================================

📋 ÉTAPE 1/4 : Chargement des types d'indicateurs...

================================================================================
CHARGEMENT DES TYPES D'INDICATEURS
================================================================================

📊 Nombre de types avant : 0

📥 Chargement de 5 types depuis la configuration...
✅ Inséré : CRIMINALITE_TOTALE (Criminalité totale)
✅ Inséré : VOLS_SANS_VIOLENCE (Vols sans violence)
✅ Inséré : VOLS_AVEC_VIOLENCE (Vols avec violence)
✅ Inséré : ATTEINTES_AUX_BIENS (Atteintes aux biens)
✅ Inséré : ATTEINTES_AUX_PERSONNES (Atteintes aux personnes)

📊 Nombre de types après : 5
✅ Types insérés : 5

================================================================================
✅ CHARGEMENT TYPES D'INDICATEURS TERMINÉ
================================================================================

🗺️  ÉTAPE 2/4 : Chargement du territoire...

================================================================================
CHARGEMENT DU TERRITOIRE BORDEAUX
================================================================================

📊 Nombre de territoires avant : 0

📥 Chargement de la commune : Bordeaux (33063)...
✅ Inséré : 33063 - Bordeaux (252,040 habitants)

📊 Nombre de territoires après : 1
✅ Territoires insérés : 1

================================================================================
✅ CHARGEMENT TERRITOIRE TERMINÉ
================================================================================

🗳️  ÉTAPE 3/4 : Chargement des résultats électoraux...

================================================================================
CHARGEMENT DES RÉSULTATS ÉLECTORAUX
================================================================================

📊 Nombre de résultats avant : 0

📥 Chargement depuis : resultats_elections_bordeaux.csv
📂 Lecture du fichier : .../resultats_elections_bordeaux.csv
📊 Lignes lues : 24
✅ Validation réussie

📦 Batch 1/1 (24 lignes)...
✅ Batch 1 : 24 insérées

📊 Nombre de résultats après : 24
✅ Résultats insérés : 24

================================================================================
✅ CHARGEMENT RÉSULTATS ÉLECTORAUX TERMINÉ
================================================================================

🚨 ÉTAPE 4/4 : Chargement des indicateurs de sécurité...

================================================================================
CHARGEMENT DES INDICATEURS DE SÉCURITÉ
================================================================================

📊 Nombre d'indicateurs avant : 0

📥 Chargement depuis : delinquance_bordeaux.csv
📂 Lecture du fichier : .../delinquance_bordeaux.csv
📊 Lignes lues : 45
✅ Validation réussie
📋 Types d'indicateurs chargés : 5

📦 Batch 1/1 (45 lignes)...
✅ Batch 1 : 45 insérées

📊 Nombre d'indicateurs après : 45
✅ Indicateurs insérés : 45

================================================================================
✅ CHARGEMENT INDICATEURS DE SÉCURITÉ TERMINÉ
================================================================================

================================================================================
📊 RÉSUMÉ DU CHARGEMENT
================================================================================

TYPES_INDICATEURS
  - Insérés : 5
  - Source : config.TYPES_INDICATEURS

TERRITOIRE
  - Insérés : 1
  - Source : config (Bordeaux)

ELECTIONS
  - Insérés : 24
  - Source : resultats_elections_bordeaux.csv

SECURITE
  - Insérés : 45
  - Source : delinquance_bordeaux.csv

================================================================================
✅ TOTAL LIGNES INSÉRÉES : 75
⏱️  DURÉE : 2.34s
================================================================================

================================================================================
✅ PIPELINE LOAD TERMINÉ AVEC SUCCÈS
================================================================================
⏱️  Durée totale : 2.34 secondes
================================================================================
```

---

## Troubleshooting

### ❌ FileNotFoundError: Fichier CSV introuvable

**Cause :** Données transformées manquantes

**Solution :**
```bash
# Vérifier existence fichiers
ls data/processed/elections/
ls data/processed/indicateurs/

# Exécuter Transform si nécessaire
python -m src.etl.transform.transform_elections
python -m src.etl.transform.transform_securite
```

### ❌ ValueError: Type inconnu

**Cause :** `code_type` non défini dans `TYPES_INDICATEURS`

**Solution :**
```python
# Ajouter le type dans config/settings.py
TYPES_INDICATEURS.append({
    "code_type": "NOUVEAU_TYPE",
    "categorie": "SECURITE",
    "nom_affichage": "Nouveau type",
    "unite_mesure": "nombre",
    "source_officielle": "SOURCE",
    "frequence": "ANNUEL",
})
```

### ❌ IntegrityError: Foreign key violation

**Cause :** Ordre d'exécution incorrect

**Solution :**
```python
# Toujours charger dans cet ordre :
run_load_types_indicateurs()  # 1
run_load_territoire()          # 2
run_load_elections()           # 3
run_load_securite()            # 4
```

---

## Prochaines étapes

- [ ] Ajouter support indicateurs INSEE (emploi, revenus)
- [ ] Implémenter chargement IRIS (géométries PostGIS)
- [ ] Ajouter chargement bureaux de vote
- [ ] Créer script de rollback (vider tables)

---

## Références

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Batch Insert Pattern](https://docs.sqlalchemy.org/en/20/faq/performance.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow)

---

**Dernière mise à jour :** 2026-02-11
**Auteur :** @de (Data Engineer)
**Supervisé par :** @tech (Tech Lead)
