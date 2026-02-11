# Code Review - Pipeline ETL Load + Correction Encodage

**Date :** 2026-02-11
**Reviewer :** @rv (Code Reviewer)
**Feature :** Implémentation complète pipeline ETL + correction encodage UTF-8
**Commit range :** Modifications non committées

---

## 📋 Vue d'Ensemble

**Périmètre :** Implémentation complète de la pipeline ETL avec correction d'encodage
**Fichiers modifiés :** 4 fichiers
**Nouveaux modules :** Load (complet), Orchestrateur ETL, Migration Alembic
**Lignes ajoutées :** ~2000+ lignes
**Complexité :** Moyenne-Élevée

**Note Globale : 7.5/10**

---

## 📊 Analyse Détaillée par Composant

### 1. **Modèle Base de Données** (`election_result.py`)

**Modifications :**
```python
# Colonnes rendues nullable
- nombre_inscrits: nullable=False → nullable=True
- nombre_votants: nullable=False → nullable=True
- nombre_exprimes: nullable=False → nullable=True
- taux_participation: nullable=False → nullable=True
```

**✅ Points Positifs :**
- Flexibilité accrue pour données incomplètes
- Migration Alembic propre et réversible

**⚠️ Points d'Attention :**
- **Impact sémantique** : Ces colonnes étaient NOT NULL pour une raison. Autoriser NULL pourrait poser des problèmes dans les analyses ML futures
- **Validation manquante** : Aucune validation au niveau applicatif pour gérer les NULL
- **Documentation** : Le docstring du modèle n'a pas été mis à jour

**Recommandation :**
```python
# Ajouter une validation au niveau Load
if pd.notna(row.get("nombre_inscrits")):
    # Vérifier cohérence : inscrits >= votants >= exprimés
    validate_electoral_coherence(inscrits, votants, exprimes)
```

---

### 2. **Transform Elections** (`transform/core/elections.py`)

**Modifications Majeures :**
1. Détection automatique d'encodage (UTF-8 → latin-1 fallback)
2. Réécriture complète du parsing : agrégation → détail candidats
3. Pattern de colonnes répétitives (7 cols × N candidats)

**✅ Points Positifs :**
- **Robustesse encodage** : Gère les fichiers mixtes
- **Architecture correcte** : Parse le format SSMSI correctement
- **Agrégation** : Calculs de pourcentages corrects (voix/exprimés)

**⚠️ Points d'Attention :**

**A. Détection d'encodage fragile :**
```python
# PROBLÈME : Lit 1024 bytes puis réouvre le fichier
try:
    with open(filepath, 'r', encoding='utf-8') as test_f:
        test_f.read(1024)  # ⚠️ Peut ne pas détecter erreur
except UnicodeDecodeError:
    encoding = 'latin-1'
```
- Échantillon de 1024 bytes peut manquer les caractères problématiques
- Fichier ouvert 2 fois (performance)

**Meilleure approche :**
```python
import chardet

# Détection robuste
with open(filepath, 'rb') as f:
    raw = f.read(10000)  # Échantillon plus large
    detected = chardet.detect(raw)
    encoding = detected['encoding']
```

**B. Gestion erreurs insuffisante :**
```python
try:
    voix = parse_french_number(row[col + 4])
    # ...
except (IndexError, ValueError):
    break  # ⚠️ Ignore silencieusement les erreurs
```
- Erreurs de parsing avalées sans log
- Difficile de déboguer en production

**C. Performance :**
```python
# Anti-pattern : Agrégation manuelle en boucle
for row in reader:
    if candidat not in candidats_data:
        candidats_data[candidat] = {'voix': 0}
    candidats_data[candidat]['voix'] += voix
```
- Pour Bordeaux (136 bureaux × 11 candidats = 1496 itérations) : OK
- Si extension à Gironde (33 communes × N bureaux) : problématique

**Solution :**
```python
# Utiliser pandas groupby dès le départ
df = pd.read_csv(filepath, sep=';', encoding=encoding)
df_bordeaux = df[df['Code du département'] == '33']
grouped = df_bordeaux.groupby(['annee', 'tour', 'candidat'])['voix'].sum()
```

---

### 3. **Transform Sécurité** (`transform/core/securite.py`)

**Modifications Majeures :**
1. Ajout mapping indicateurs granulaires → catégories
2. Agrégation par (code_type, année)
3. Calcul CRIMINALITE_TOTALE automatique

**✅ Points Positifs :**
- **Mapping explicite** : Clair et maintenable
- **Agrégation correcte** : Utilise pandas groupby (performant)
- **Calcul dérivé** : CRIMINALITE_TOTALE cohérent

**⚠️ Points d'Attention :**

**A. Mapping en dur dans le code :**
```python
MAPPING_INDICATEURS = {
    'Cambriolages de logement': 'VOLS_SANS_VIOLENCE',
    # ... ⚠️ Hard-codé dans la fonction
}
```
- Difficile à maintenir si nouvelles catégories SSMSI
- Pas de traçabilité des changements

**Meilleure approche :**
```python
# Externaliser dans config/mappings.py
SSMSI_CATEGORY_MAPPING = {
    "version": "2024-01",
    "source": "SSMSI",
    "mappings": {
        "VOLS_SANS_VIOLENCE": [
            "Cambriolages de logement",
            "Vols d'accessoires sur véhicules",
            # ...
        ]
    }
}
```

**B. Indicateurs non mappés ignorés silencieusement :**
```python
df_mapped = df_bordeaux[df_bordeaux['code_type'].notna()].copy()
# ⚠️ Les stupéfiants, escroqueries, etc. disparaissent sans trace
```

**Solution :**
```python
unmapped = df_bordeaux[df_bordeaux['code_type'].isna()]['indicateur'].unique()
if len(unmapped) > 0:
    logger.info(f"  Indicateurs non mappés (ignorés) : {list(unmapped)}")
```

---

### 4. **Module Load** (Nouveau)

**Structure :**
```
src/etl/load/
├── main.py                    # Orchestrateur Load
├── config/
│   └── settings.py            # Types indicateurs, config
├── core/
│   ├── elections.py           # Load résultats électoraux
│   ├── indicateurs.py         # Load indicateurs sécurité
│   ├── territoire.py          # Load territoire
│   └── type_indicateur.py     # Load types
└── utils/
    └── validation.py          # Validations CSV
```

**✅ Points Positifs :**
- **Architecture modulaire** : Séparation des responsabilités claire
- **Batch loading** : Gère les gros volumes (1000 rows/batch)
- **Gestion doublons** : Vérifie l'existence avant insertion
- **Type casting** : Convertit id_territoire en string (évite erreurs)
- **Validation** : Valide les colonnes CSV avant chargement

**⚠️ Points d'Attention :**

**A. Absence de transactions explicites :**
```python
for i in range(0, len(df), BATCH_SIZE):
    batch_df = df.iloc[i : i + BATCH_SIZE]
    inserted = load_indicateurs_batch(session, batch_df, type_mapping)
    session.commit()  # ⚠️ Commit par batch
```
- Si batch 3/5 échoue, les batchs 1-2 sont déjà committés
- État inconsistant difficile à rollback

**Solution :**
```python
# Option 1: Transaction globale
with session.begin():
    for batch in batches:
        load_batch(session, batch)
    # Commit automatique si pas d'erreur

# Option 2: Savepoints
for batch in batches:
    savepoint = session.begin_nested()
    try:
        load_batch(session, batch)
        savepoint.commit()
    except Exception:
        savepoint.rollback()
        raise
```

**B. Gestion d'erreurs trop permissive :**
```python
if code_type not in type_mapping:
    print(f"[WARN]  Type inconnu ignoré : {code_type}")
    continue  # ⚠️ Continue silencieusement
```
- Typo dans code_type → données perdues silencieusement
- Pas de compteur d'erreurs

**C. Performance du check de doublons :**
```python
# Pour chaque ligne, une requête SQL
existing = session.query(Indicateur).filter(...).first()
```
- Pour 45 indicateurs × 1 requête = 45 queries
- Acceptable pour POC, mais pas scalable

**Solution :**
```python
# Charger tous les existants en mémoire
existing_keys = set(
    session.query(
        Indicateur.id_territoire,
        Indicateur.id_type,
        Indicateur.annee,
        Indicateur.periode
    ).all()
)

# Check en mémoire O(1)
if (id_territoire, id_type, annee, periode) in existing_keys:
    continue
```

---

### 5. **Orchestrateur ETL** (`etl/main.py`)

**✅ Points Positifs :**
- **UX excellent** : Affichage clair, coloré, progressif
- **Validation préalable** : Vérifie PostgreSQL, tables, dossiers
- **Rapport détaillé** : Résumé final avec statistiques
- **Gestion erreurs** : Continue même si une phase échoue partiellement

**⚠️ Points d'Attention :**

**A. Pas de gestion de retry :**
```python
success = extract_main()  # ⚠️ Si échec réseau → arrêt complet
```

**B. Logs console uniquement :**
- Pas de fichier de log persistant
- Difficile de déboguer les runs passés

**Solution :**
```python
import logging
from datetime import datetime

# Configurer logging vers fichier + console
log_file = f"logs/etl_{datetime.now():%Y%m%d_%H%M%S}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
```

---

### 6. **Migration Alembic**

**✅ Points Positifs :**
- Migration manuelle (évite les bugs d'autogenerate PostGIS)
- Fonctions upgrade/downgrade symétriques
- Nommage clair

**⚠️ Points d'Attention :**
- Pas de validation des données existantes avant migration
- Si des NULL existaient avant, la downgrade échouera

**Solution :**
```python
def downgrade() -> None:
    # Vérifier qu'aucun NULL n'existe
    conn = op.get_bind()
    null_count = conn.execute(
        "SELECT COUNT(*) FROM election_result "
        "WHERE nombre_inscrits IS NULL"
    ).scalar()

    if null_count > 0:
        raise Exception(f"{null_count} rows with NULL - clean data first")

    # Puis alter columns...
```

---

## 🔒 Sécurité & Risques

### ✅ Points Sécurisés :
1. **Pas d'injection SQL** : Utilisation d'ORM SQLAlchemy
2. **Validation colonnes** : Vérifie présence des colonnes attendues
3. **Type casting** : Conversion explicite des types

### ⚠️ Risques Identifiés :

**1. Path Traversal potentiel** (Faible risque)
```python
# Si filepath vient d'un input utilisateur non validé
with open(filepath, 'r', encoding=encoding) as f:
```
- **Ici OK** : Chemins hardcodés dans config
- **À surveiller** : Si future feature "charger fichier custom"

**2. CSV Injection** (Faible risque)
```python
# Si un candidat s'appelle "=1+1" ou "=cmd|' /c calc'"
candidat = f"{prenom} {nom}"  # ⚠️ Non sanitizé
```
- **Ici OK** : Données sources officielles SSMSI
- **À surveiller** : Si affichage dans Excel/LibreOffice

**3. Pas de limite de taille de fichier**
```python
df = pd.read_csv(filepath, ...)  # ⚠️ Peut charger 10GB en RAM
```
- **Ici OK** : Fichiers connus (~34MB max)
- **À surveiller** : Si extension à d'autres sources

---

## 📈 Performance

### Points Critiques :

**1. Transform Elections : O(n×m)**
- 136 bureaux × 11 candidats × 4 fichiers = ~6000 itérations
- **Acceptable** pour POC Bordeaux
- **Problématique** si extension Gironde (×30 communes)

**2. Load : N+1 queries**
- 1 SELECT par ligne pour check doublons
- **Acceptable** pour 72 lignes (27 élections + 45 indicateurs)
- **Problématique** si >10k lignes

**3. Détection encodage : Double lecture**
- Fichier ouvert 2× pour tester encodage
- Impact négligeable pour fichiers 30MB

### Recommandations Performance :
```python
# Transform : Utiliser pandas dès le départ
# Load : Bulk upsert PostgreSQL
from sqlalchemy.dialects.postgresql import insert

stmt = insert(Indicateur).values(records)
stmt = stmt.on_conflict_do_nothing(
    index_elements=['id_territoire', 'id_type', 'annee', 'periode']
)
session.execute(stmt)
```

---

## 📝 Documentation & Tests

### ⚠️ Manquements :

**1. Tests unitaires absents**
```
tests/
└── etl/
    ├── test_transform_elections.py  # ❌ Manquant
    ├── test_load_indicateurs.py     # ❌ Manquant
    └── test_encoding_detection.py   # ❌ Manquant
```

**Recommandation :**
```python
# tests/etl/test_transform_elections.py
def test_parse_candidats_2017():
    """Vérifie parsing correct des 11 candidats 2017 T1."""
    result = transform_elections()
    assert result == True
    df = pd.read_csv('data/processed/elections/...')
    assert len(df[df['annee'] == 2017]) == 13  # 11+2

def test_encoding_accents():
    """Vérifie que les accents sont préservés."""
    df = pd.read_csv('data/processed/elections/...')
    hamon = df[df['candidat'].str.contains('HAMON')]
    assert 'Benoît' in hamon['candidat'].values[0]
```

**2. Documentation API manquante**
- Pas de docstrings pour certaines fonctions Load
- Pas de schema des CSV attendus

**3. Logs insuffisants**
- Pas de logging structuré (JSON)
- Pas de tracing des transformations (lineage)

---

## 🎯 Recommandations Prioritaires

### 🔴 Critique (À faire avant production)

1. **Ajouter transaction globale dans Load**
   - Éviter états inconsistants
   - Rollback automatique si erreur

2. **Logger les indicateurs non mappés**
   - Traçabilité des données ignorées
   - Permet de compléter le mapping

3. **Valider cohérence électorale**
   ```python
   assert nombre_votants <= nombre_inscrits
   assert nombre_exprimes <= nombre_votants
   assert sum(voix_candidats) == nombre_exprimes
   ```

### 🟡 Important (À planifier)

4. **Externaliser mapping SSMSI**
   - Fichier JSON/YAML dans `config/`
   - Versionné avec date de MAJ

5. **Ajouter logging fichier**
   - Rotation automatique (max 10 fichiers)
   - Format structuré (JSON) pour parsing

6. **Tests unitaires de base**
   - Au minimum : test_transform_elections
   - Au minimum : test_load_indicateurs

### 🟢 Améliorations (Nice to have)

7. **Optimiser check doublons**
   - Charger existants en mémoire
   - Ou utiliser UPSERT PostgreSQL

8. **Meilleure détection encodage**
   - Utiliser chardet library
   - Cache du résultat détecté

9. **Monitoring & Observabilité**
   - Métriques : durée par phase, lignes insérées/sec
   - Alertes si anomalies (0 lignes insérées, etc.)

---

## ✅ Verdict Final

**Qualité Générale : 7.5/10**

| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture | 8/10 | Modulaire, séparation claire |
| Correctness | 8/10 | Résultats corrects, encodage fixé |
| Robustesse | 6/10 | Gestion erreurs perfectible |
| Performance | 7/10 | OK pour POC, limites si scale |
| Sécurité | 8/10 | Pas de vulnérabilités majeures |
| Documentation | 6/10 | Docstrings OK, tests absents |
| Maintenabilité | 7/10 | Code clair, mapping à externaliser |

**Points Forts :**
- ✅ Architecture ETL solide et complète
- ✅ Problème d'encodage résolu élégamment
- ✅ Code lisible et bien structuré
- ✅ Gestion des doublons

**Points Faibles :**
- ❌ Absence de tests automatisés
- ❌ Gestion d'erreurs perfectible
- ❌ Transactions Load non atomiques
- ❌ Mapping hard-codé

**Recommandation : MERGE AVEC RÉSERVES**
- ✅ Code fonctionnel et prêt pour POC
- ⚠️ Implémenter recommandations critiques avant production
- 📝 Créer issues GitHub pour points d'amélioration

---

## 📊 Métriques

- **Fichiers modifiés :** 4
- **Nouveaux fichiers :** 50+
- **Lignes ajoutées :** ~2000
- **Lignes supprimées :** ~200
- **Complexité cyclomatique moyenne :** Moyenne
- **Couverture tests :** 0% ⚠️

---

*Revue effectuée le : 2026-02-11*
*Durée de la revue : ~2h*
*Reviewer : @rv (Code Reviewer)*
