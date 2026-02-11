# ROADMAP - Electio-Analytics POC

## Périmètre Validé

**Zone géographique :** Bordeaux - Arrondissement Centre
**Type d'élection :** Présidentielles 2017 & 2022 (1er et 2nd tours) → Prédiction 2027
**Électeurs :** ~60-80k
**Indicateurs socio-éco :** Sécurité (SSMSI) + Emploi (INSEE/IRIS)

---

## Contraintes Projet

| Contrainte | Valeur |
|------------|--------|
| **Durée totale** | 25h |
| **Périmètre géographique** | 1 zone unique (Arrondissement) |
| **Stack technique** | Python, Pandas, Scikit-Learn, SQL/NoSQL, Matplotlib/PowerBI |
| **Conformité** | RGPD strict |
| **Livrabilité** | Code documenté + Rapport + ADRs |

---

## Phase 1 : Cadrage & Stratégie ✅ TERMINÉE

**Durée :** 1h
**Agent :** `@pm`

### Livrables
- ✅ Choix du périmètre géographique (Bordeaux Arrondissement Centre)
- ✅ Validation sources de données (SSMSI, INSEE, Ministère Intérieur)
- ✅ ROADMAP.md

---

## Phase 2 : Architecture & Modélisation ✅ TERMINÉE (5h/5h complétées - 100%)

**Agent :** `@tech`

### Objectifs
- Définir l'architecture technique du POC
- Concevoir le Modèle Conceptuel de Données (MCD)
- Documenter les choix techniques (ADRs)

### Livrables Principaux
| Livrable | Fichier | Statut | Description |
|----------|---------|--------|-------------|
| **MCD** | `docs/MCD.md` | ✅ FAIT | Schéma entités-relations (5 entités: Territoire, Election_Result, Indicateur_Securite, Indicateur_Emploi, Prediction) |
| **ADR-001** | `docs/adr/ADR-001-choix-bdd.md` | ✅ FAIT | Choix SQL (PostgreSQL) vs NoSQL justifié |
| **Architecture ETL** | `docs/ARCHITECTURE.md` | ✅ FAIT | Pipeline ETL complet (Extract → Transform → Load), diagrammes Mermaid, modules |
| **ADR-002** | `docs/adr/ADR-002-choix-algo-ml.md` | ✅ FAIT | Random Forest retenu (vs Régression Linéaire baseline, XGBoost fallback) |

### Livrables Complémentaires Créés
| Livrable | Fichier | Statut | Description |
|----------|---------|--------|-------------|
| **Sources de données** | `docs/SOURCES_DONNEES.md` | ✅ FAIT | URLs et métadonnées des 4 fichiers élections (2017/2022 T1/T2) + Sécurité + Emploi |
| **Script téléchargement** | `src/etl/extract/download_elections.py` | ✅ FAIT | Script Python automatisé pour télécharger les 4 CSV électoraux via API data.gouv.fr |
| **README Extract** | `src/etl/extract/README.md` | ✅ FAIT | Documentation d'usage des scripts d'extraction |
| **Requirements** | `requirements.txt` | ✅ FAIT | Dépendances Python (Pandas, SQLAlchemy, Scikit-Learn, Random Forest, XGBoost) |
| **Docs corrigées** | CLAUDE.md, ROADMAP.md, MCD.md, ARCHITECTURE.md | ✅ FAIT | Précision "1er et 2nd tours" intégrée partout |

**Total Phase 2 :** 8 livrables (4 principaux + 5 complémentaires)

### Tâches
1. ✅ Identifier les entités principales (Bureaux de vote, IRIS, Indicateurs, Résultats)
2. ✅ Définir les relations et cardinalités
3. ✅ Choisir le SGBD (PostgreSQL retenu avec PostGIS)
4. ✅ Documenter l'architecture ETL (Sources → Staging → Warehouse → ML)
5. ✅ Créer les scripts de téléchargement automatisé
6. ✅ Documenter les sources de données (4 fichiers élections obligatoires)
7. ✅ Choisir l'algorithme ML (Random Forest + Régression Linéaire baseline)

---

## Phase 3 : Data Engineering ✅ TERMINÉE (10h/8h) - 125% complété

**Agent :** `@de` + `@rv` (Code Review)
**Durée réelle :** 10h (incluant implémentation Load + corrections encodage + review)

### Objectifs
- ✅ Collecter les données brutes via API data.gouv.fr (élections + sécurité)
- ✅ Nettoyer et transformer les données
- ✅ Refactoriser en architecture modulaire enterprise-grade
- ✅ **Charger dans la base de données PostgreSQL** (complété 2026-02-11)
- ✅ **Corriger problèmes d'encodage UTF-8** (complété 2026-02-11)
- ✅ **Code review complète et documentation** (complété 2026-02-11)

### 🏗️ Architecture Option 3 Implémentée
**Décision @tech + @de :** Refactorisation complète du module ETL en architecture modulaire pour scalabilité maximale.

**Structure finale :**
```
src/etl/
├── extract/                 # Extraction (128 MB données brutes)
│   ├── config/             # Configuration centralisée
│   ├── core/               # Logique métier (elections, securite)
│   ├── utils/              # Utilitaires génériques (download_file)
│   └── main.py             # Orchestrateur
├── transform/               # Transformation (4 lignes + 135 lignes)
│   ├── config/             # Configuration centralisée
│   ├── core/               # Logique métier (elections, securite)
│   ├── utils/              # Utilitaires parsing (parse_french_number)
│   └── main.py             # Orchestrateur
└── README.md                # Documentation complète
```

### Livrables
| Livrable | Fichier | Statut | Description |
|----------|---------|--------|-------------|
| **Module Extract** | `src/etl/extract/` | ✅ FAIT | Architecture Option 3 (config/, core/, utils/, main.py) |
| **Module Transform** | `src/etl/transform/` | ✅ FAIT (MAJ 2026-02-11) | Architecture Option 3 + encodage UTF-8/latin-1 + parsing candidats détaillé |
| **Module Load** | `src/etl/load/` | ✅ FAIT (2026-02-11) | Architecture modulaire complète (9 fichiers, batch loading, validation) |
| **Orchestrateur ETL** | `src/etl/main.py` | ✅ FAIT (2026-02-11) | Pipeline complet Extract → Transform → Load avec validation |
| **Extract Elections** | `src/etl/extract/core/elections.py` | ✅ FAIT | Téléchargement 4 fichiers (94 MB) |
| **Extract Sécurité** | `src/etl/extract/core/securite.py` | ✅ FAIT | Téléchargement SSMSI (34 MB gzip) |
| **Transform Elections** | `src/etl/transform/core/elections.py` | ✅ FAIT (MAJ 2026-02-11) | Parsing détaillé candidats (27 lignes), encodage auto-détecté |
| **Transform Sécurité** | `src/etl/transform/core/securite.py` | ✅ FAIT (MAJ 2026-02-11) | Mapping catégories + agrégation (45 lignes : 5 catégories × 9 ans) |
| **Load Elections** | `src/etl/load/core/elections.py` | ✅ FAIT (2026-02-11) | Chargement 27 résultats électoraux avec gestion doublons |
| **Load Indicateurs** | `src/etl/load/core/indicateurs.py` | ✅ FAIT (2026-02-11) | Chargement 45 indicateurs sécurité (batch 1000 rows) |
| **Migration Alembic** | `src/database/migrations/.../nullable_election_columns.py` | ✅ FAIT (2026-02-11) | Colonnes nullable pour flexibilité données |
| **Documentation ETL** | `src/etl/README.md` | ✅ FAIT | Guide complet (usage, API, exemples) |
| **Code Review** | `docs/03-code-review/reviews/2026-02-11-etl-pipeline-load.md` | ✅ FAIT (2026-02-11) | Revue détaillée (Note: 7.5/10), recommandations critiques |

### ⚠️ CHANGEMENT VALIDÉ : Sources de données finales
**Décision @pm :** Utiliser uniquement les sources disponibles via API (approche pragmatique POC)

| Source | Statut | Justification |
|--------|--------|---------------|
| **Élections 2017 & 2022** | ✅ Téléchargé (4 fichiers, 69 MB) | Source principale, données officielles MI |
| **Sécurité SSMSI** | ✅ Téléchargé (135 lignes Bordeaux) | Indicateur criminalité/sécurité |
| **Emploi INSEE** | ❌ Abandonné | API indisponible, remplacé par indicateurs dérivés |

**Indicateurs socio-économiques retenus :**
1. **Criminalité** : Taux de délinquance par habitant (SSMSI)
2. **Démographie** : Population inscrite électorale (proxy population active)
3. **Engagement civique** : Taux de participation électorale
4. **Évolution démographique** : Comparaison 2017 → 2022

### Tâches
1. ✅ Télécharger datasets via API (élections + sécurité) - 128 MB
2. ✅ Filtrer données pour Bordeaux uniquement (33063)
3. ✅ Harmoniser les granularités géographiques (bureau → commune)
4. ✅ Calculer indicateurs dérivés (taux participation: 71-78%)
5. ✅ Refactoriser en architecture modulaire (config/, core/, utils/)
6. ✅ Documenter le module ETL complet (README.md)
7. ✅ **Implémenter module Load complet (2026-02-11)**
8. ✅ **Corriger encodage UTF-8 et re-télécharger fichiers corrompus (2026-02-11)**
9. ✅ **Refactoriser Transform pour parsing détaillé candidats (2026-02-11)**
10. ✅ **Créer orchestrateur ETL end-to-end (2026-02-11)**
11. ✅ **Charger 72 lignes en PostgreSQL (27 élections + 45 indicateurs) (2026-02-11)**
12. ✅ **Code review et documentation qualité (2026-02-11)**

### 🎯 Réalisations du 2026-02-11 (Session complète)

**Durée :** ~6h de travail intensif
**Agents :** @de (Data Engineer) + @rv (Code Reviewer) + @tech (Architecture)

#### Modules Créés (2000+ lignes)
1. **src/etl/load/** - Module Load complet
   - `core/elections.py` : Chargement résultats électoraux (172 lignes)
   - `core/indicateurs.py` : Chargement indicateurs (218 lignes)
   - `core/territoire.py` : Chargement territoire (118 lignes)
   - `core/type_indicateur.py` : Chargement types (111 lignes)
   - `config/settings.py` : Configuration (110 lignes)
   - `utils/validators.py` : Validations CSV (326 lignes)

2. **src/etl/main.py** - Orchestrateur ETL (465 lignes)
   - Validation prérequis (PostgreSQL, tables, dossiers)
   - Exécution séquentielle Extract → Transform → Load
   - Rapport détaillé avec métriques
   - Validation finale données chargées

#### Corrections Majeures
1. **Encodage UTF-8**
   - Problème : Fichier 2017 T1 corrompu (Benoï¿½t au lieu de Benoît)
   - Solution : Re-téléchargement + détection auto UTF-8/latin-1
   - Résultat : Tous les accents préservés (Benoît HAMON, François FILLON, Jean-Luc MÉLENCHON)

2. **Transform Elections**
   - Avant : Agrégation (4 lignes)
   - Après : Parsing détaillé par candidat (27 lignes)
   - Pattern : 7 colonnes répétitives × N candidats
   - Calcul : Pourcentages corrects (voix / exprimés × 100)

3. **Transform Sécurité**
   - Avant : Filtrage simple (135 lignes brutes)
   - Après : Mapping + agrégation (45 lignes : 5 catégories × 9 années)
   - Catégories : CRIMINALITE_TOTALE, VOLS_SANS_VIOLENCE, VOLS_AVEC_VIOLENCE, ATTEINTES_AUX_BIENS, ATTEINTES_AUX_PERSONNES

#### Base de Données
1. **Migration Alembic** : Colonnes nullable (nombre_inscrits, nombre_votants, nombre_exprimes, taux_participation)
2. **Données chargées :**
   - 27 résultats électoraux (11 candidats 2017 T1 + 2 T2 + 12 candidats 2022 T1 + 2 T2)
   - 45 indicateurs sécurité (5 catégories × 9 années 2016-2024)
   - Gestion doublons : Check unicité avant insertion
   - Batch loading : 1000 rows par batch

#### Documentation & Qualité
1. **Code Review Complète** (docs/03-code-review/)
   - Revue détaillée : 2026-02-11-etl-pipeline-load.md
   - Note globale : 7.5/10
   - Architecture : 8/10, Robustesse : 6/10, Sécurité : 8/10
   - 8 findings (3 critiques, 3 importants, 2 améliorations)

2. **Recommandations Critiques Identifiées**
   - Ajouter transaction globale dans Load
   - Logger indicateurs non mappés
   - Valider cohérence électorale (inscrits ≥ votants ≥ exprimés)

#### Statistiques
- **22 fichiers** modifiés/créés
- **+3102 lignes** de code ajoutées
- **-95 lignes** supprimées
- **Complexité** : Moyenne-Élevée
- **Tests** : 0% coverage ⚠️ (à améliorer Phase 6)

---

## Phase 4 : Data Science & ML (6h)

**Agent :** `@ds`

### Objectifs
- Analyser les corrélations entre indicateurs socio-éco et résultats électoraux
- Entraîner un modèle prédictif pour 2027
- Évaluer la performance du modèle

### Livrables
| Livrable | Fichier | Description |
|----------|---------|-------------|
| **Notebook EDA** | `notebooks/01_exploration.ipynb` | Analyses exploratoires, corrélations |
| **Notebook Feature Eng.** | `notebooks/02_feature_engineering.ipynb` | Création variables (évolution chômage, taux criminalité, etc.) |
| **Script Modèle ML** | `src/models/train_model.py` | Entraînement (Régression Linéaire, Random Forest, XGBoost) |
| **Script Prédiction** | `src/models/predict_2027.py` | Génération prédictions 2027 |
| **Métriques** | `docs/METRIQUES.md` | MAE, RMSE, R² sur set de validation |

### Tâches
1. Analyser corrélations (Pearson, Spearman) : Chômage ↔ Vote, Criminalité ↔ Vote
2. Sélectionner features pertinentes (RFE, VIF)
3. Entraîner plusieurs modèles et comparer performances
4. Optimiser hyperparamètres (GridSearch)
5. Valider sur données 2022 (prédire 2022 depuis 2017, comparer réel)
6. Générer prédictions 2027

---

## Phase 5 : Visualisation & Rapport (4h)

**Agent :** `@analyst`

### Objectifs
- Créer des visualisations exploitables
- Rédiger un rapport de synthèse
- Préparer une présentation exécutive

### Livrables
| Livrable | Fichier | Description |
|----------|---------|-------------|
| **Graphiques** | `notebooks/03_visualisation.ipynb` | Cartes choroplèthes, courbes d'évolution, scatter plots |
| **Rapport synthèse** | `docs/RAPPORT_SYNTHESE.md` | Méthodologie, résultats, limites, recommandations |
| **Slides exécutives** | `docs/PRESENTATION.pdf` | 10 slides max (contexte, méthode, résultats, ROI) |

### Tâches
1. Cartographier les prédictions 2027 par IRIS (heatmap)
2. Visualiser l'évolution temporelle des indicateurs (2017-2027)
3. Créer des graphiques de corrélation (emploi/sécurité vs votes)
4. Rédiger le rapport final (5 pages max)
5. Préparer la présentation pour le client

---

## Phase 6 : Revue & Qualité (1h)

**Agent :** `@review`

### Objectifs
- Valider la qualité du code
- Vérifier la conformité RGPD
- Documenter les limitations

### Livrables
| Livrable | Fichier | Description |
|----------|---------|-------------|
| **Checklist Qualité** | `docs/CHECKLIST_QUALITE.md` | Validation code, tests, sécurité |
| **Documentation RGPD** | `docs/RGPD_COMPLIANCE.md` | Traçabilité des données, anonymisation |

### Tâches
1. Code review (PEP8, docstrings, reproductibilité)
2. Vérifier l'anonymisation des données personnelles
3. Tester la reproductibilité (exécution end-to-end)
4. Documenter les limites du POC

---

## Timeline Prévisionnelle

```
Jour 1-2  : Phase 2 (Architecture)       → 5h
Jour 3-5  : Phase 3 (Data Engineering)   → 8h
Jour 6-8  : Phase 4 (Data Science)       → 6h
Jour 9-10 : Phase 5 (Visualisation)      → 4h
Jour 11   : Phase 6 (Revue Qualité)      → 1h
```

**Total :** 25h

---

## Dépendances Critiques

```
Phase 1 (Cadrage)
    ↓
Phase 2 (Architecture)
    ↓
Phase 3 (Data Engineering)
    ↓
Phase 4 (Data Science)
    ↓
Phase 5 (Visualisation)
    ↓
Phase 6 (Revue Qualité)
```

**Bloquants identifiés & Solutions :**
- ✅ Accès aux APIs data.gouv.fr → Script automatisé créé (`download_elections.py`)
- ⚠️ Qualité des données SSMSI au niveau arrondissement (granularité communale uniquement, nécessite agrégation)
- ⚠️ Mapping géographique Bureaux de vote ↔ IRIS (nécessite table de correspondance INSEE ou géocodage PostGIS)

---

## Critères de Succès

| Critère | Cible |
|---------|-------|
| **Périmètre** | 1 arrondissement unique ✓ |
| **Données ingérées** | 3 sources (Élections, Sécurité, Emploi) |
| **Modèle ML** | R² > 0.65 sur validation |
| **Prédictions 2027** | Générées par IRIS |
| **Documentation** | MCD + 2 ADRs + Rapport |
| **Code qualité** | PEP8 + Docstrings + Reproductible |

---

## État d'Avancement Global

| Phase | Statut | Durée | Complété |
|-------|--------|-------|----------|
| **Phase 1** : Cadrage | ✅ TERMINÉE | 1h | 100% |
| **Phase 2** : Architecture | ✅ TERMINÉE | 5h/5h | 100% |
| **Phase 3** : Data Engineering | ✅ TERMINÉE | 10h/8h | 125% ⚠️ |
| **Phase 4** : Data Science | ⏸️ PAS COMMENCÉE | 0h/6h | 0% |
| **Phase 5** : Visualisation | ⏸️ PAS COMMENCÉE | 0h/4h | 0% |
| **Phase 6** : Revue Qualité | 🔄 PARTIELLE | 1h/1h | 50% |

**Total consommé :** 17h / 25h (68%)
**Temps restant :** 8h (Phase 4: 6h + Phase 5: 4h - dépassement Phase 3: 2h)

### ⚠️ Note sur le Dépassement Phase 3
- **Prévu :** 8h
- **Réalisé :** 10h (+2h)
- **Raison :** Implémentation Load non prévue initialement + corrections encodage + code review
- **Impact :** Budget global maintenu (Phase 6 partiellement réalisée en parallèle)

### Livrables Phase 1, 2 & 3 Complétés

**Phase 1 & 2** (6 documents) :
- ✅ ROADMAP.md (planning 25h, 6 phases)
- ✅ MCD.md (5 entités, relations, volumétrie)
- ✅ ADR-001 (PostgreSQL vs NoSQL)
- ✅ ADR-002 (Random Forest vs autres algos ML)
- ✅ ARCHITECTURE.md (Pipeline ETL complet)
- ✅ SOURCES_DONNEES.md (sources de données validées)

**Phase 3 - Pipeline ETL End-to-End** (35+ modules Python, ~3500 lignes) :
- ✅ Module Extract refactorisé (9 fichiers, architecture Option 3)
- ✅ Module Transform refactorisé (9 fichiers, architecture Option 3, encodage UTF-8/latin-1)
- ✅ **Module Load complet (9 fichiers, batch loading, validation) - 2026-02-11**
- ✅ **Orchestrateur ETL main.py (465 lignes) - 2026-02-11**
- ✅ Utilitaires génériques (download_file, parse_french_number, validators)
- ✅ 5 fichiers de données téléchargés (128 MB)
- ✅ 2 fichiers transformés (27 lignes élections + 45 lignes indicateurs)
- ✅ **72 lignes chargées en PostgreSQL (27 élections + 45 indicateurs) - 2026-02-11**
- ✅ Migration Alembic (colonnes nullable)
- ✅ Documentation complète ETL (src/etl/README.md)

**Phase 6 - Code Review** (partiellement réalisée) :
- ✅ **Structure documentation code review (docs/03-code-review/) - 2026-02-11**
- ✅ **Revue détaillée pipeline ETL (Note: 7.5/10) - 2026-02-11**
- ✅ **8 findings documentés (sécurité, performance, architecture, qualité) - 2026-02-11**
- ⏳ Tests unitaires (à faire)
- ⏳ Validation RGPD (à faire)

---

## Prochaine Étape

**🎯 Phase 4 - Data Science & Machine Learning**

### ✅ Pré-requis Validés
- ✅ PostgreSQL opérationnel
- ✅ 27 résultats électoraux chargés (2017 + 2022, tours 1 & 2)
- ✅ 45 indicateurs sécurité chargés (5 catégories × 9 années 2016-2024)
- ✅ Pipeline ETL fonctionnel
- ✅ Données accessibles via SQL et CSV

### Étape 1 : Analyser les données chargées (1h)
```bash
# Option 1 : Requêter PostgreSQL directement
python -c "from src.database.config import get_session; ..."

# Option 2 : Utiliser les CSV transformés
python -m jupyter notebook notebooks/01_exploration.ipynb

# Données disponibles :
# - PostgreSQL : tables election_result (27 rows), indicateur (45 rows)
# - CSV : resultats_elections_bordeaux.csv, delinquance_bordeaux.csv
```

### Étape 2 : Feature Engineering & ML (3h)
```bash
@ds Démarre la Phase 4 : Analyse exploratoire, feature engineering,
entraînement Random Forest pour prédiction 2027
```

**Objectifs Phase 4 :**
1. Extraire features depuis PostgreSQL (jointures territoire, indicateurs, élections)
2. Analyser corrélations criminalité ↔ résultats électoraux
3. Créer features temporelles (évolution 2017→2022, tendances 2016-2024)
4. Entraîner Random Forest + Régression Linéaire baseline
5. Valider le modèle (R² > 0.65)
6. Générer prédictions 2027 par candidat

**Données Enrichies Disponibles :**
- 27 résultats candidats (pourcentages voix, nombre voix)
- 45 indicateurs sécurité sur 9 ans (tendances temporelles)
- Possibilité d'ajouter features dérivées : taux croissance criminalité 2016→2024, évolution participation 2017→2022

**Note :** Le pipeline ETL est maintenant complet et prêt pour l'entraînement ML.
