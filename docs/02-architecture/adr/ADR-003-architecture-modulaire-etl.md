# ADR-003 : Architecture Modulaire Enterprise-Grade pour le Module ETL

**Statut** : ✅ Accepté
**Date** : 2026-02-10
**Auteur** : @tech (Tech Lead / Architecte) + @de (Data Engineer)
**Décision** : Refactoriser le module ETL en architecture Option 3 (séparation par type de fonction)

---

## Contexte

Le module ETL initial était organisé de manière simple avec des fichiers plats :
- `extract/config.py` (70 lignes)
- `extract/download_elections.py` (64 lignes)
- `extract/download_securite.py` (70 lignes)
- `extract/utils.py` (95 lignes)
- `transform/config.py` (70 lignes)
- `transform/transform_data.py` (252 lignes)

### Problèmes identifiés
1. **Scalabilité limitée** : Ajout de nouvelles sources nécessite création de nouveaux fichiers à la racine
2. **Réutilisabilité** : Utilitaires mélangés avec la logique métier
3. **Testabilité** : Difficile d'isoler les composants pour les tests unitaires
4. **Maintenabilité** : Fichiers volumineux (252 lignes pour transform_data.py)
5. **Standards** : Architecture ne suit pas les patterns enterprise

---

## Décision

Adopter l'**Architecture Option 3** (séparation par type de fonction) pour les modules `extract/` et `transform/`.

### Structure cible

```
src/etl/
├── extract/
│   ├── config/              # Configuration centralisée
│   │   ├── __init__.py
│   │   └── settings.py      # URLs, chemins, constantes
│   ├── core/                # Logique métier par source
│   │   ├── __init__.py
│   │   ├── elections.py     # Téléchargement élections
│   │   └── securite.py      # Téléchargement sécurité
│   ├── utils/               # Utilitaires génériques
│   │   ├── __init__.py
│   │   └── download.py      # download_file()
│   ├── __init__.py          # Exports publics
│   └── main.py              # Orchestrateur

├── transform/
│   ├── config/              # Configuration centralisée
│   │   ├── __init__.py
│   │   └── settings.py      # Chemins, constantes
│   ├── core/                # Logique métier par source
│   │   ├── __init__.py
│   │   ├── elections.py     # Transformation élections
│   │   └── securite.py      # Transformation sécurité
│   ├── utils/               # Utilitaires de parsing
│   │   ├── __init__.py
│   │   └── parsing.py       # parse_french_number()
│   ├── __init__.py          # Exports publics
│   └── main.py              # Orchestrateur
└── README.md                # Documentation complète
```

### Principes architecturaux

1. **Séparation des responsabilités (SRP)**
   - `config/` : Configuration uniquement (URLs, chemins, constantes)
   - `core/` : Logique métier spécifique à chaque source
   - `utils/` : Fonctions génériques réutilisables
   - `main.py` : Orchestration pure

2. **Scalabilité**
   - Ajout d'une nouvelle source = 1 fichier dans `core/`
   - Pas de modification des autres modules

3. **Testabilité**
   - Chaque module peut être testé indépendamment
   - Imports isolés facilitent les mocks

4. **Réutilisabilité**
   - Utilitaires dans `utils/` réutilisables partout
   - API publique claire via `__init__.py`

---

## Alternatives Considérées

### Option 1 : Sources (Organisé par source de données)
```
extract/
├── sources/
│   ├── elections.py
│   ├── securite.py
│   └── emploi.py
├── utils.py
├── config.py
└── main.py
```

**Avantages** :
- ✅ Nom clair ("sources")
- ✅ Facile d'ajouter nouvelles sources

**Inconvénients** :
- ⚠️ Configuration et utils restent à la racine
- ⚠️ Moins de séparation stricte

### Option 2 : Downloaders (Pattern orienté action)
```
extract/
├── downloaders/
│   ├── elections.py
│   ├── securite.py
│   └── emploi.py
├── utils.py
├── config.py
└── main.py
```

**Avantages** :
- ✅ Nom explicite sur l'action

**Inconvénients** :
- ⚠️ Verbeux (dossier parent = "extract")
- ⚠️ Configuration et utils non isolés

### Option 3 : Par type de fonction (CHOIX RETENU)
```
extract/
├── config/
├── core/
├── utils/
└── main.py
```

**Avantages** :
- ✅ Séparation stricte des responsabilités
- ✅ Standards enterprise (Django, Flask, FastAPI)
- ✅ Scalabilité maximale
- ✅ Testabilité parfaite
- ✅ Configuration isolée

**Inconvénients** :
- ⚠️ Peut sembler over-engineering pour POC
- ⚠️ Plus de fichiers à naviguer

### Pourquoi Option 3 ?

Bien que ce soit un POC, l'architecture doit être **transférable** et **professionnelle**. Les contraintes du projet MSPR imposent une "approche industrielle" avec du code "reproductible et transférable" (cf. CLAUDE.md).

L'Option 3 est un **investissement à court terme** pour :
- Faciliter l'ajout de nouvelles sources (emploi, référentiels géographiques)
- Démontrer la maîtrise des patterns enterprise
- Produire un code professionnel pour le portefeuille

---

## Conséquences

### Positives
1. **Scalabilité** : Ajout d'une nouvelle source en 3 étapes simples
2. **Testabilité** : Tests unitaires faciles à écrire
3. **Maintenabilité** : Code organisé et documenté
4. **Professionnalisme** : Architecture reconnue dans l'industrie
5. **Réutilisabilité** : Utilitaires extraits et réutilisables

### Négatives
1. **Complexité initiale** : Plus de fichiers à créer (18 vs 6)
2. **Navigation** : Structure plus profonde (3 niveaux au lieu de 1)
3. **Imports relatifs** : `from ..config import` au lieu de `from .config import`

### Neutres
1. **Lignes de code** : +300 lignes environ (mais mieux organisées)
2. **Temps de développement** : +2h pour la refactorisation (investissement unique)

---

## Implémentation

### Modules créés

**Extract** (9 fichiers) :
- `config/settings.py` (139 lignes)
- `config/__init__.py` (60 lignes)
- `utils/download.py` (105 lignes)
- `utils/__init__.py` (10 lignes)
- `core/elections.py` (70 lignes)
- `core/securite.py` (75 lignes)
- `core/__init__.py` (18 lignes)
- `main.py` (95 lignes)
- `__init__.py` (45 lignes)

**Transform** (9 fichiers) :
- `config/settings.py` (70 lignes)
- `config/__init__.py` (40 lignes)
- `utils/parsing.py` (40 lignes)
- `utils/__init__.py` (10 lignes)
- `core/elections.py` (180 lignes)
- `core/securite.py` (115 lignes)
- `core/__init__.py` (18 lignes)
- `main.py` (120 lignes)
- `__init__.py` (45 lignes)

**Total** : 18 fichiers, ~1220 lignes (vs 621 lignes avant)

### Exemple d'ajout de nouvelle source

```python
# 1. Créer core/emploi.py
from ..config import DATA_RAW_EMPLOI, EMPLOI_URL
from ..utils import download_file

def download_emploi() -> bool:
    return download_file(EMPLOI_URL, DATA_RAW_EMPLOI / "file.csv", "Emploi")

# 2. Ajouter dans config/settings.py
EMPLOI_URL = "https://..."

# 3. Importer dans main.py
from .core import download_elections, download_securite, download_emploi
```

---

## Validation

### Tests effectués
- ✅ Extraction complète : `python -m src.etl.extract.main`
- ✅ Transformation complète : `python -m src.etl.transform.main`
- ✅ Imports publics : `from src.etl.extract import main, download_file`
- ✅ Pipeline complet : Extract + Transform sans erreur

### Métriques de qualité
- ✅ **Type hints** : 100% des fonctions
- ✅ **Docstrings** : 100% des modules et fonctions (Google style)
- ✅ **Logging** : Toutes les opérations loggées
- ✅ **Gestion d'erreurs** : Graceful failures, exit codes appropriés
- ✅ **Documentation** : README.md complet (350 lignes)

---

## Références

- **Patterns** : Clean Architecture (Robert C. Martin)
- **Standards Python** : PEP 8, PEP 484 (Type Hints)
- **Frameworks similaires** : Django (apps), Flask (blueprints), FastAPI (routers)
- **Documentation** : `src/etl/README.md`

---

## Révisions

| Date | Auteur | Changement |
|------|--------|------------|
| 2026-02-10 | @tech + @de | Création initiale, choix Option 3 |

---

**Statut final** : ✅ **ACCEPTÉ** - Architecture Option 3 implémentée et validée
