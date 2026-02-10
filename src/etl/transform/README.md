# Module Transform - ETL Electio-Analytics

## Vue d'ensemble

Module de transformation des données brutes en données structurées et prêtes pour le chargement en base de données.

⚠️ **Note importante** : Les fichiers CSV électoraux contiennent des **virgules comme séparateurs décimaux** (format français). Utiliser le **module csv natif** Python au lieu de pandas pour un parsing fiable.

## Scripts disponibles

### 1. `transform_elections.py` ✅

Transforme les fichiers électoraux par bureau de vote pour Bordeaux.

**Fonctionnalités :**
- Détection automatique du format (2017 vs 2022)
- Parsing avec module csv natif (évite les erreurs pandas)
- Agrégation des bureaux de vote par commune
- Calcul automatique du taux de participation

**Usage :**
```bash
python -m src.etl.transform.transform_elections
```

**Entrées :**
- `data/raw/elections/presidentielles_2017_tour1_bureaux_vote.csv`
- `data/raw/elections/presidentielles_2017_tour2_bureaux_vote.csv`
- `data/raw/elections/presidentielles_2022_tour1_bureaux_vote.csv` (Bordeaux absent)
- `data/raw/elections/presidentielles_2022_tour2_bureaux_vote.csv` (Bordeaux absent)

**Sorties :**
- `data/processed/elections/resultats_elections_bordeaux.csv`

### 2. `transform_securite.py` ✅

Transforme les données de sécurité SSMSI en format long.

**Usage :**
```bash
python -m src.etl.transform.transform_securite
```

**Entrées :**
- `data/raw/securite/delinquance_bordeaux_2016_2024.csv`

**Sorties :**
- `data/processed/indicateurs/indicateurs_securite.csv`

## Fichiers transformés validés

### ✅ `resultats_elections_bordeaux.csv` (2 lignes)
```csv
code_commune,nom_commune,annee,tour,inscrits,votants,taux_participation
33063,Bordeaux,2017,1,147632,114568,77.60
33063,Bordeaux,2017,2,147631,108044,73.19
```

### ✅ `indicateurs_securite.csv` (1,215 lignes)
```csv
code_commune,nom_commune,annee,type_indicateur,valeur
33063,Bordeaux,2016,nombre,504.0
33063,Bordeaux,2016,taux_pour_mille,1.9996826
...
```

**Années couvertes** : 2016-2024
**Indicateurs** : 9 types (criminalité, délinquance, etc.)

## Problèmes identifiés et résolus

### ❌ Problème : Fichiers CSV avec virgules décimales

**Symptôme** : Pandas parse mal les fichiers électoraux (colonnes décalées, données corrompues)

**Cause** : Format français avec virgules comme séparateurs décimaux (1,234 au lieu de 1.234)

**Solution** : Utiliser le module `csv` natif Python au lieu de pandas :
```python
import csv
with open(filepath, 'r', encoding='latin-1') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    for row in reader:
        # Traitement ligne par ligne
```

### ❌ Données 2022 manquantes

**Problème** : Les fichiers 2022 téléchargés ne contiennent pas Bordeaux

**Status** : En attente - utiliser uniquement les données 2017 pour le POC

## Conformité MCD v2.0

Les données transformées sont compatibles avec le schéma `indicateur` :
- `id_territoire` → code_commune (33063)
- `id_type` → type_indicateur
- `annee` → année de l'élection/indicateur
- `periode` → tour (T1, T2) ou trimestre
- `valeur_numerique` → inscrits, taux_participation, nombre de faits, etc.
