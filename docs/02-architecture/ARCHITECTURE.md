# Architecture ETL & Database - Electio-Analytics

**Version :** 3.0 (Schéma Enrichi Multi-Granularités + Architecture Modulaire)

**Date :** 2026-02-11

**Périmètre :** Bordeaux - Présidentielles 2017 & 2022 (1er et 2nd tours) → Prédiction 2027

**Tech Lead :** @tech + @de + @ds

**Décisions Architecturales :**
- ADR-003 (Architecture ETL Modulaire Option 3)
- ADR-004 (Enrichissement Schéma Base de Données v3.0)

**Documents Associés :**
- [MCD v3.0](./database/01-mcd.md) - Modèle Conceptuel de Données
- [MLD v3.0](./database/02-mld.md) - Modèle Logique de Données

---

## 🗄️ Schéma Base de Données v3.0 (Nouveauté)

### Vue d'Ensemble

Le schéma de base de données a été **enrichi et normalisé** (3NF) pour supporter :
- **Multi-granularités territoriales** (BUREAU, CANTON, COMMUNE, DEPARTEMENT, REGION)
- **Référentiels candidats et partis** (tracking historique, profil idéologique)
- **Séparation participation/résultats** (élimination redondances)
- **Traçabilité granularités** (table `election_territoire`)

**Gain ML estimé :** +15-25% R² score (×3.5 features exploitables)

### Architecture

```mermaid
erDiagram
    REGION ||--o{ DEPARTEMENT : "contient"
    DEPARTEMENT ||--o{ CANTON : "contient"
    DEPARTEMENT ||--o{ COMMUNE : "contient"
    COMMUNE ||--o{ BUREAU_VOTE : "contient"

    CANDIDAT ||--o{ CANDIDAT_PARTI : "affilie"
    PARTI ||--o{ CANDIDAT_PARTI : "accueille"

    TYPE_ELECTION ||--o{ ELECTION : "categorise"
    ELECTION ||--o{ ELECTION_TERRITOIRE : "declare"
    ELECTION_TERRITOIRE ||--o{ RESULTAT_PARTICIPATION : "valide"
    ELECTION_TERRITOIRE ||--o{ RESULTAT_CANDIDAT : "valide"
    CANDIDAT ||--o{ RESULTAT_CANDIDAT : "obtient"
```

### Tables Principales (14)

| Domaine | Tables | Rôle |
|---------|--------|------|
| **Géographique** | region, departement, canton, commune, arrondissement, bureau_vote | Hiérarchie multi-niveaux |
| **Candidats/Partis** | candidat, parti, candidat_parti | Référentiels normalisés |
| **Élections** | type_election, election, election_territoire | Événements + référentiel granularités |
| **Résultats** | resultat_participation, resultat_candidat | Séparation stats générales vs candidats |

### Features ML Exploitables

**Avant (schéma v2.0) :** ~10 features
```
['nombre_voix', 'pourcentage_voix', 'criminalite_totale', ...]
```

**Après (schéma v3.0) :** ~35 features
```python
# Candidat (7)
['age', 'nb_elections_precedentes', 'score_moyen_historique',
 'evolution_momentum', 'profession', ...]

# Parti (6)
['position_economique', 'position_sociale', 'classification_ideologique',
 'distance_ideologique_gagnant', ...]

# Participation (8)
['taux_abstention', 'taux_blancs_nuls', 'evolution_vs_N-1',
 'ecart_vs_national', ...]

# Géographique (5)
['type_territoire', 'densite_population', 'taille_commune', ...]

# Socio-économique (9)
['criminalite_totale', 'criminalite_evolution', ...]
```

**Référence complète :** [MCD v3.0](./database/01-mcd.md)

---

## Vue d'Ensemble ETL

Le pipeline ETL (Extract-Transform-Load) centralise les données électorales (1er et 2nd tours des présidentielles 2017 & 2022) et socio-économiques depuis 3 sources externes, en garantissant la **traçabilité**, la **qualité** et la **reproductibilité**.

**Nouvelle architecture :** Le module ETL a été refactorisé selon l'**Architecture Option 3** (séparation par type de fonction) pour une scalabilité et maintenabilité maximales.

---

## 🏗️ Architecture Modulaire (Version 2.0)

### Structure du Module ETL

```
src/etl/
├── extract/                    # Extraction des données brutes
│   ├── config/                # Configuration centralisée
│   │   ├── __init__.py
│   │   └── settings.py        # URLs, chemins, constantes
│   ├── core/                  # Logique métier par source
│   │   ├── __init__.py
│   │   ├── elections.py       # Téléchargement élections
│   │   └── securite.py        # Téléchargement sécurité
│   ├── utils/                 # Utilitaires génériques
│   │   ├── __init__.py
│   │   └── download.py        # download_file()
│   ├── __init__.py            # Exports publics
│   └── main.py                # Orchestrateur extraction
│
├── transform/                  # Transformation des données
│   ├── config/                # Configuration centralisée
│   │   ├── __init__.py
│   │   └── settings.py        # Chemins, constantes
│   ├── core/                  # Logique métier par source
│   │   ├── __init__.py
│   │   ├── elections.py       # Transformation élections
│   │   └── securite.py        # Transformation sécurité
│   ├── utils/                 # Utilitaires de parsing
│   │   ├── __init__.py
│   │   └── parsing.py         # parse_french_number()
│   ├── __init__.py            # Exports publics
│   └── main.py                # Orchestrateur transformation
│
└── README.md                   # Documentation complète
```

### Principes Architecturaux

1. **Séparation des responsabilités (SRP)**
   - `config/` : Configuration uniquement (URLs, chemins, constantes)
   - `core/` : Logique métier spécifique à chaque source de données
   - `utils/` : Fonctions génériques réutilisables
   - `main.py` : Orchestration pure sans logique métier

2. **Scalabilité**
   - Ajout d'une nouvelle source = 1 fichier dans `core/`
   - Pas de modification des modules existants (Open/Closed Principle)

3. **Testabilité**
   - Chaque module peut être testé indépendamment
   - Imports isolés facilitent les mocks et stubs

4. **Réutilisabilité**
   - Utilitaires dans `utils/` réutilisables partout
   - API publique claire via `__init__.py`

5. **Maintenabilité**
   - Code organisé et documenté
   - Type hints sur toutes les fonctions
   - Docstrings au format Google

### Avantages de l'Architecture Option 3

| Aspect | Avant | Après |
|--------|-------|-------|
| **Fichiers racine** | 6 fichiers | 1 fichier (main.py) + 3 packages |
| **Scalabilité** | Moyenne | Excellente |
| **Testabilité** | Bonne | Parfaite |
| **Patterns** | Simple | Enterprise-grade |
| **Lignes de code** | 621 lignes | 1220 lignes (mieux organisées) |

**Référence :** Voir `docs/02-architecture/adr/ADR-003-architecture-modulaire-etl.md`

```mermaid
flowchart LR
    A[Sources Externes] --> B[Extraction]
    B --> C[Transformation]
    C --> D[Chargement]

    style A fill:#e1f5ff,stroke:#01579b, color: #020202
    style B fill:#fff3e0,stroke:#e65100, color: #020202
    style C fill:#f3e5f5,stroke:#4a148c, color: #020202
    style D fill:#e8f5e9,stroke:#1b5e20, color: #020202
```

---

## Architecture Globale

```mermaid
graph LR
    subgraph Sources Externes
        A[data.gouv.fr<br/>Élections 2017/2022]
        B[SSMSI<br/>Sécurité 2017-2024]
        C[INSEE<br/>Emploi IRIS 2017-2024]
    end

    subgraph ETL Pipeline
        D[Extract<br/>extract_*.py]
        E[Transform<br/>transform.py]
        F[Load<br/>load.py]
    end

    subgraph Stockage
        G[(PostgreSQL<br/>electio_analytics)]
        H[/data/raw/<br/>CSV bruts/]
        I[/data/processed/<br/>CSV nettoyés/]
    end

    A --> D
    B --> D
    C --> D
    D --> H
    H --> E
    E --> I
    I --> F
    F --> G
```

---

## Phase 1 : EXTRACT (Extraction)

### Objectif
Télécharger les datasets bruts depuis les APIs/sites open data et les sauvegarder localement.

### Sources de Données

#### Source 1 : Élections Présidentielles (data.gouv.fr)

**Données collectées :** 1er et 2nd tours pour 2017 et 2022 (4 fichiers CSV)

**URL :**
- 2017 Tour 1 : `https://www.data.gouv.fr/datasets/elections-presidentielle-2017-resultats-bureaux-vote-tour-1`
- 2017 Tour 2 : `https://www.data.gouv.fr/datasets/5cddfde49ce2e76d93bdb18b`
- 2022 Tour 1 : `https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-du-1er-tour`
- 2022 Tour 2 : `https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-du-second-tour`

**Format :** CSV
**Granularité :** Bureau de vote
**Champs clés :**
- `Code du département`, `Code de la commune`, `Code du bureau de vote`
- `Nom`, `Prénom` (candidat)
- `Voix`, `% Voix/Exp`, `Inscrits`, `Votants`, `Exprimés`

**Filtrage :** Département 33 (Gironde), Commune 33063 (Bordeaux)

**Script :** `src/etl/extract_elections.py`

```python
def extract_elections(year: int, tour: int, output_path: str) -> pd.DataFrame:
    """
    Télécharge les résultats présidentielles depuis data.gouv.fr.

    Args:
        year: Année élection (2017, 2022)
        tour: Tour de l'élection (1 ou 2)
        output_path: Chemin sauvegarde CSV brut

    Returns:
        DataFrame avec résultats bruts

    Notes:
        Télécharge les 4 fichiers requis :
        - 2017 Tour 1, 2017 Tour 2
        - 2022 Tour 1, 2022 Tour 2
    """
    # Télécharger CSV depuis data.gouv.fr
    # Filtrer département=33, commune=33063
    # Sauvegarder dans /data/raw/elections_{year}_tour{tour}.csv
    pass
```

---

#### Source 2 : Sécurité / Criminalité (SSMSI)

**URL :** `https://www.data.gouv.fr/fr/datasets/bases-statistiques-communale-departementale-et-regionale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales/`

**Format :** CSV
**Granularité :** Commune (pas de détail IRIS public)
**Période :** 2017-2024
**Champs clés :**
- `Code.département`, `Code.commune`, `Année`, `Mois` (optionnel)
- 13 indicateurs : `Cambriolages de logement`, `Vols de véhicules`, `Coups et blessures volontaires`, etc.

**Limitation :** Données communales uniquement (agrégation nécessaire pour IRIS)

**Script :** `src/etl/extract_securite.py`

```python
def extract_securite(start_year: int, end_year: int, output_path: str) -> pd.DataFrame:
    """
    Télécharge les statistiques SSMSI pour Bordeaux.

    Args:
        start_year: Année début (2017)
        end_year: Année fin (2024)
        output_path: Chemin sauvegarde CSV brut

    Returns:
        DataFrame avec faits de délinquance
    """
    # Télécharger CSV SSMSI
    # Filtrer commune=33063
    # Sauvegarder dans /data/raw/securite_2017_2024.csv
    pass
```

---

#### Source 3 : Emploi / Chômage (INSEE)

**URL :**
- Données IRIS : `https://www.insee.fr/fr/statistiques/zones/2011101` (Dossier complet commune)
- Demandeurs emploi IRIS : `https://www.insee.fr/fr/statistiques/7654804`

**Format :** CSV, Excel
**Granularité :** IRIS (Ilots Regroupés pour l'Information Statistique)
**Champs clés :**
- `CODE_IRIS`, `NOM_IRIS`, `Année`, `Trimestre`
- `Taux de chômage`, `Population active`, `Revenus médian`, `Nombre emplois`

**Script :** `src/etl/extract_emploi.py`

```python
def extract_emploi_iris(commune_code: str, output_path: str) -> pd.DataFrame:
    """
    Télécharge les données emploi INSEE au niveau IRIS.

    Args:
        commune_code: Code commune INSEE (33063)
        output_path: Chemin sauvegarde CSV brut

    Returns:
        DataFrame avec indicateurs emploi par IRIS
    """
    # Scraper ou utiliser API INSEE
    # Extraire données IRIS pour Bordeaux
    # Sauvegarder dans /data/raw/emploi_iris_bordeaux.csv
    pass
```

---

### Arborescence de Sortie (Extract)

```
/data/raw/elections/
    ├── presidentielles_2017_tour1_bureaux_vote.csv  (1er tour 2017)
    ├── presidentielles_2017_tour2_bureaux_vote.csv  (2nd tour 2017)
    ├── presidentielles_2022_tour1_bureaux_vote.csv  (1er tour 2022)
    ├── presidentielles_2022_tour2_bureaux_vote.csv  (2nd tour 2022)

/data/raw/securite/
    └── delinquance_bordeaux_2017_2024.csv

/data/raw/emploi/
    └── emploi_iris_bordeaux_2017_2024.csv
```

---

## Phase 2 : TRANSFORM (Transformation)

### Objectif
Nettoyer, harmoniser et enrichir les données brutes pour les rendre exploitables.

### Transformations Clés

#### T1 : Harmonisation Géographique

**Problème :** 3 granularités différentes
- Élections : **Bureau de vote** (Code BV)
- Sécurité : **Commune** (33063)
- Emploi : **IRIS** (Code IRIS)

**Solution :** Créer une table de mapping `bureau_vote → IRIS`

**Approche :**
1. Utiliser le fichier de correspondance INSEE : [Table passage Bureau de vote → IRIS](https://www.insee.fr/fr/information/2008354)
2. Géocoder les adresses de bureaux de vote (lat/long)
3. Spatial join avec polygones IRIS via PostGIS

**Script :** `src/etl/transform_geo_mapping.py`

```python
def map_bureau_to_iris(elections_df: pd.DataFrame,
                        mapping_table: pd.DataFrame) -> pd.DataFrame:
    """
    Associe chaque bureau de vote à un IRIS.

    Args:
        elections_df: Résultats électoraux par bureau
        mapping_table: Table Bureau → IRIS (INSEE)

    Returns:
        DataFrame avec colonne `id_iris` ajoutée
    """
    # Jointure elections_df <> mapping_table sur code_bureau
    # Ajouter colonne `id_iris`
    pass
```

---

#### T2 : Normalisation des Données Électorales

**Transformations :**
- Uniformiser noms candidats : `"MACRON Emmanuel"` → `"Emmanuel MACRON"`
- Calculer `taux_participation = (Votants / Inscrits) * 100`
- Calculer `pourcentage_voix = (Voix / Exprimés) * 100`
- Gérer valeurs manquantes (bureaux fermés, données incomplètes)
- Dédoublonner (si CSV mal formatés)

**Script :** `src/etl/transform_elections.py`

```python
def normalize_elections(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et normalise les résultats électoraux.

    Returns:
        DataFrame conforme au schéma Election_Result (MCD)
    """
    # Renommer colonnes selon MCD
    # Calculer métriques dérivées (%, taux)
    # Typer les colonnes (int, float, str)
    pass
```

---

#### T3 : Normalisation Sécurité

**Transformations :**
- Pivot des 13 indicateurs (colonnes → lignes) : `type_fait`, `nombre_faits`
- Calculer `taux_pour_1000_hab = (nombre_faits / population) * 1000`
- Gérer valeurs nulles (certains types de faits absents)
- Harmoniser types de faits (uniformiser libellés)

**Script :** `src/etl/transform_securite.py`

```python
def normalize_securite(raw_df: pd.DataFrame,
                        population_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme les données SSMSI au format long (pivot).

    Returns:
        DataFrame conforme au schéma Indicateur_Securite (MCD)
    """
    # Pivot : 13 colonnes indicateurs → 13 lignes par année
    # Calculer taux pour 1000 habitants
    pass
```

---

#### T4 : Normalisation Emploi

**Transformations :**
- Gérer données trimestrielles vs annuelles (agréger ou interpoler)
- Calculer `taux_chomage = (Chomeurs / Population_active) * 100`
- Gérer valeurs aberrantes (taux > 100%, négatifs)
- Harmoniser codes IRIS (supprimer préfixes/suffixes)

**Script :** `src/etl/transform_emploi.py`

```python
def normalize_emploi(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les indicateurs emploi INSEE.

    Returns:
        DataFrame conforme au schéma Indicateur_Emploi (MCD)
    """
    # Harmoniser codes IRIS
    # Calculer taux de chômage
    # Gérer valeurs manquantes (imputation médiane ou suppression)
    pass
```

---

#### T5 : Enrichissement Temporel

**Objectif :** Créer features pour le ML

**Features dérivées :**
- `evolution_chomage_1an = taux_chomage(N) - taux_chomage(N-1)`
- `evolution_criminalite_3ans = AVG(faits_2020-2022) - AVG(faits_2017-2019)`
- `tendance_participation = participation(2022) - participation(2017)`

**Script :** `src/etl/transform_features.py`

```python
def create_temporal_features(emploi_df: pd.DataFrame,
                               securite_df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée des features d'évolution temporelle.

    Returns:
        DataFrame avec colonnes delta_* et tendance_*
    """
    # Calculer variations année N vs N-1
    # Moyennes mobiles sur 3 ans
    pass
```

---

### Arborescence de Sortie (Transform)

```
/data/processed/
    ├── territoire.csv                 (référentiel IRIS + Bureaux)
    ├── elections_normalized.csv       (résultats harmonisés)
    ├── securite_normalized.csv        (indicateurs pivotés)
    ├── emploi_normalized.csv          (taux chômage nettoyés)
    └── features_ml.csv                (features enrichies pour ML)
```

---

## Phase 3 : LOAD (Chargement)

### Objectif
Insérer les données transformées dans PostgreSQL en garantissant l'intégrité référentielle.

### Ordre de Chargement (Respect des FK)

```mermaid
flowchart TD
    A[1. Territoire<br/>table parent, pas de FK]
    B[2. Election_Result<br/>FK → Territoire]
    C[3. Indicateur_Securite<br/>FK → Territoire]
    D[4. Indicateur_Emploi<br/>FK → Territoire]
    E[5. Prediction<br/>FK → Territoire, chargé en Phase 4]

    A --> B
    B --> C
    C --> D
    D --> E

    style A fill:#e1f5ff,stroke:#01579b, color: #020202
    style B fill:#fff3e0,stroke:#e65100, color: #020202
    style C fill:#f3e5f5,stroke:#4a148c, color: #020202
    style D fill:#fff3e0,stroke:#e65100, color: #020202
    style E fill:#e8f5e9,stroke:#1b5e20, color: #020202
```

### Scripts de Chargement

**Script principal :** `src/etl/load.py`

```python
import pandas as pd
import sqlalchemy as sa

def load_to_postgres(df: pd.DataFrame,
                      table_name: str,
                      engine: sa.Engine,
                      if_exists: str = 'append') -> int:
    """
    Charge un DataFrame dans PostgreSQL.

    Args:
        df: DataFrame à charger
        table_name: Nom de la table cible
        engine: SQLAlchemy engine
        if_exists: 'append', 'replace', 'fail'

    Returns:
        Nombre de lignes insérées
    """
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return len(df)

def run_etl_pipeline():
    """Exécute le pipeline ETL complet."""

    # 1. Connexion PostgreSQL
    engine = sa.create_engine('postgresql://admin:password@localhost:5432/electio_analytics')

    # 2. Chargement Territoire
    territoire_df = pd.read_csv('/data/processed/territoire.csv')
    load_to_postgres(territoire_df, 'territoire', engine, if_exists='replace')

    # 3. Chargement Election_Result
    elections_df = pd.read_csv('/data/processed/elections_normalized.csv')
    load_to_postgres(elections_df, 'election_result', engine)

    # 4. Chargement Indicateur_Securite
    securite_df = pd.read_csv('/data/processed/securite_normalized.csv')
    load_to_postgres(securite_df, 'indicateur_securite', engine)

    # 5. Chargement Indicateur_Emploi
    emploi_df = pd.read_csv('/data/processed/emploi_normalized.csv')
    load_to_postgres(emploi_df, 'indicateur_emploi', engine)

    print("✅ ETL Pipeline terminé avec succès")
```

---

### Validation Post-Chargement

**Script :** `src/etl/validate_data.py`

```python
def validate_referential_integrity(engine: sa.Engine) -> bool:
    """
    Vérifie que toutes les FK sont valides.

    Returns:
        True si intégrité OK, False sinon
    """
    # Test 1 : Tous les id_territoire de Election_Result existent dans Territoire
    query = """
        SELECT COUNT(*)
        FROM election_result er
        LEFT JOIN territoire t ON er.id_territoire = t.id_territoire
        WHERE t.id_territoire IS NULL
    """
    result = pd.read_sql(query, engine)
    orphans = result.iloc[0, 0]

    if orphans > 0:
        print(f"❌ {orphans} résultats électoraux sans territoire associé")
        return False

    # Test 2 : Pas de doublons
    # Test 3 : Pas de valeurs nulles sur colonnes NOT NULL
    # ...

    print("✅ Intégrité référentielle validée")
    return True
```

---

## Gestion des Erreurs & Traçabilité

### Logs ETL

**Structure :** Chaque étape du pipeline génère un log JSON

```json
{
  "timestamp": "2026-02-09T14:32:10Z",
  "step": "extract_elections",
  "status": "success",
  "rows_extracted": 12450,
  "source_url": "https://data.gouv.fr/...",
  "output_file": "/data/raw/elections_2022_tour2.csv",
  "execution_time_seconds": 3.2
}
```

**Script :** `src/etl/logger.py`

```python
import json
from datetime import datetime

def log_etl_step(step: str, status: str, metadata: dict):
    """Enregistre les métadonnées d'une étape ETL."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "step": step,
        "status": status,
        **metadata
    }

    with open('/logs/etl_pipeline.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

---

### Gestion des Erreurs

**Stratégie :** Rollback transactionnel en cas d'échec

```python
def run_etl_with_rollback():
    engine = sa.create_engine('postgresql://...')

    with engine.begin() as conn:  # Transaction automatique
        try:
            # Étape 1 : Extract
            extract_elections(2017, '/data/raw/elections_2017.csv')

            # Étape 2 : Transform
            transform_elections('/data/raw/elections_2017.csv')

            # Étape 3 : Load
            load_to_postgres(elections_df, 'election_result', conn)

            # Si tout réussit → COMMIT automatique

        except Exception as e:
            # Si erreur → ROLLBACK automatique
            log_etl_step('run_etl', 'failed', {'error': str(e)})
            raise
```

---

## Diagramme de Flux Complet

```mermaid
sequenceDiagram
    participant User
    participant Extract as Extract Scripts
    participant Raw as /data/raw/
    participant Transform as Transform Scripts
    participant Processed as /data/processed/
    participant Load as Load Script
    participant DB as PostgreSQL

    User->>Extract: python src/etl/extract_all.py
    Extract->>Raw: Télécharge CSVs (Élections, Sécurité, Emploi)
    Raw-->>Transform: Lit CSVs bruts
    Transform->>Transform: Nettoyage + Harmonisation
    Transform->>Processed: Sauvegarde CSVs normalisés
    Processed-->>Load: Lit CSVs processés
    Load->>DB: INSERT INTO territoire, election_result, ...
    DB-->>Load: Validation intégrité FK
    Load-->>User: ✅ ETL terminé (26k lignes chargées)
```

---

## Architecture Modulaire

### Structure des Modules

```
src/etl/
    ├── __init__.py
    ├── extract/
    │   ├── extract_elections.py      (Télécharge résultats électoraux)
    │   ├── extract_securite.py       (Télécharge données SSMSI)
    │   ├── extract_emploi.py         (Télécharge données INSEE)
    │   └── extract_all.py            (Orchestrateur : lance tous les extracts)
    │
    ├── transform/
    │   ├── transform_elections.py    (Normalise élections)
    │   ├── transform_securite.py     (Normalise sécurité)
    │   ├── transform_emploi.py       (Normalise emploi)
    │   ├── transform_geo_mapping.py  (Mapping Bureau → IRIS)
    │   ├── transform_features.py     (Features ML)
    │   └── transform_all.py          (Orchestrateur transforms)
    │
    ├── load/
    │   ├── load.py                   (Chargement PostgreSQL)
    │   └── validate_data.py          (Tests intégrité post-load)
    │
    ├── utils/
    │   ├── logger.py                 (Logs ETL)
    │   ├── db_connection.py          (SQLAlchemy engine)
    │   └── config.py                 (Variables d'environnement)
    │
    └── main.py                       (Point d'entrée : lance pipeline complet)
```

---

## Configuration (Variables d'Environnement)

**Fichier :** `.env` (non versionné)

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=electio_analytics
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password

# Chemins
DATA_RAW_PATH=/data/raw
DATA_PROCESSED_PATH=/data/processed
LOGS_PATH=/logs

# URLs Data.gouv.fr
ELECTIONS_2017_URL=https://www.data.gouv.fr/fr/datasets/r/...
ELECTIONS_2022_URL=https://www.data.gouv.fr/fr/datasets/r/...
SECURITE_URL=https://www.data.gouv.fr/fr/datasets/r/...
EMPLOI_INSEE_URL=https://www.insee.fr/...

# Filtres
DEPARTEMENT_CODE=33
COMMUNE_CODE=33063
COMMUNE_NAME=Bordeaux
```

---

## Exécution du Pipeline

### Commande Unique (Orchestration)

```bash
# Lancer le pipeline complet (Extract → Transform → Load)
python src/etl/main.py --full

# Lancer uniquement Extract
python src/etl/main.py --extract

# Lancer uniquement Transform
python src/etl/main.py --transform

# Lancer uniquement Load
python src/etl/main.py --load
```

### Docker Compose (Environnement complet)

**Fichier :** `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: electio_analytics
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docs/MCD.sql:/docker-entrypoint-initdb.d/01_schema.sql

  etl:
    build: .
    depends_on:
      - postgres
    environment:
      POSTGRES_HOST: postgres
    volumes:
      - ./data:/data
      - ./logs:/logs
    command: python src/etl/main.py --full

volumes:
  postgres_data:
```

**Lancement :**
```bash
docker-compose up -d postgres    # Démarre PostgreSQL
docker-compose up etl            # Lance le pipeline ETL
```

---

## Métriques & Monitoring

### Métriques de Performance

| Étape | Temps cible | Volumétrie |
|-------|-------------|------------|
| **Extract Elections** | <10s | 12k lignes (4 fichiers CSV) |
| **Extract Sécurité** | <5s | 1k lignes |
| **Extract Emploi** | <15s | 400 lignes (50 IRIS × 8 ans) |
| **Transform All** | <20s | Normalisation + Mapping géo |
| **Load All** | <30s | 26k insertions PostgreSQL |
| **Total Pipeline** | **<80s** | |

### Dashboard Monitoring (Optionnel - Phase future)

- Grafana + Prometheus pour tracer les exécutions ETL
- Alertes si échecs (Slack/Email)

---

## Évolutions Futures (Hors POC)

1. **Automatisation :** Scheduler (Airflow, Prefect) pour refresh automatique données
2. **Incrémental ETL :** Ne recharger que les nouvelles données (delta)
3. **Data Quality Tests :** Great Expectations pour validation automatique
4. **Streaming :** Kafka pour ingestion temps réel (sondages)
5. **Data Lineage :** Apache Atlas pour tracer l'origine de chaque donnée

---

## Checklist de Validation

- [ ] Toutes les tables PostgreSQL créées (5 tables)
- [ ] Intégrité référentielle validée (aucune FK orpheline)
- [ ] Volumétrie conforme (~26k lignes)
- [ ] Logs ETL générés (1 fichier JSONL)
- [ ] Pas de valeurs nulles sur colonnes NOT NULL
- [ ] Pas de doublons (contraintes UNIQUE respectées)
- [ ] Codes géographiques cohérents (INSEE, IRIS, Bureaux)
- [ ] Pipeline reproductible (exécution depuis zéro réussie)

---

## Références Techniques

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Data.gouv.fr API](https://doc.data.gouv.fr/)
- [INSEE Web Services](https://api.insee.fr/)
- [PostGIS Spatial Queries](https://postgis.net/docs/)

---

**Statut :** ✅ Documentation complétée
**Prochaine étape :** Phase 3 - `@de` implémente les scripts ETL (`extract_*.py`, `transform_*.py`, `load.py`)
