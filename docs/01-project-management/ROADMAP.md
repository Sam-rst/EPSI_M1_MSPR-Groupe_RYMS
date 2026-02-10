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

**Agent :** `@archi`

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

## Phase 3 : Data Engineering ✅ TERMINÉE (8h/8h) - 100% complété

**Agent :** `@de`

### Objectifs
- ✅ Collecter les données brutes via API data.gouv.fr (élections + sécurité)
- ✅ Nettoyer et transformer les données
- ✅ Refactoriser en architecture modulaire enterprise-grade
- ⏳ Charger dans la base de données (reporté Phase 4)

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
| **Module Transform** | `src/etl/transform/` | ✅ FAIT | Architecture Option 3 (config/, core/, utils/, main.py) |
| **Extract Elections** | `src/etl/extract/core/elections.py` | ✅ FAIT | Téléchargement 4 fichiers (94 MB) |
| **Extract Sécurité** | `src/etl/extract/core/securite.py` | ✅ FAIT | Téléchargement SSMSI (34 MB gzip) |
| **Transform Elections** | `src/etl/transform/core/elections.py` | ✅ FAIT | Agrégation Bordeaux (4 lignes) |
| **Transform Sécurité** | `src/etl/transform/core/securite.py` | ✅ FAIT | Filtrage Bordeaux (135 lignes) |
| **Documentation ETL** | `src/etl/README.md` | ✅ FAIT | Guide complet (usage, API, exemples) |
| **Script Chargement** | `src/etl/load/` | ⏳ TODO | Insertion en base PostgreSQL (Phase 4) |

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
7. ⏳ Charger en base PostgreSQL (reporté Phase 4)

---

## Phase 4 : Data Science & ML (6h)

**Agent :** `@datasci`

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
| **Phase 3** : Data Engineering | ✅ TERMINÉE | 8h/8h | 100% |
| **Phase 4** : Data Science | ⏸️ PAS COMMENCÉE | 0h/6h | 0% |
| **Phase 5** : Visualisation | ⏸️ PAS COMMENCÉE | 0h/4h | 0% |
| **Phase 6** : Revue Qualité | ⏸️ PAS COMMENCÉE | 0h/1h | 0% |

**Total consommé :** 14h / 25h (56%)

### Livrables Phase 1, 2 & 3 Complétés
**Phase 1 & 2** (6 documents) :
- ✅ ROADMAP.md (planning 25h, 6 phases)
- ✅ MCD.md (5 entités, relations, volumétrie)
- ✅ ADR-001 (PostgreSQL vs NoSQL)
- ✅ ADR-002 (Random Forest vs autres algos ML)
- ✅ ARCHITECTURE.md (Pipeline ETL complet)
- ✅ SOURCES_DONNEES.md (sources de données validées)

**Phase 3 - ETL Complet** (18 modules Python, ~1500 lignes) :
- ✅ Module Extract refactorisé (9 fichiers, architecture Option 3)
- ✅ Module Transform refactorisé (9 fichiers, architecture Option 3)
- ✅ Utilitaires génériques (download_file, parse_french_number)
- ✅ 5 fichiers de données téléchargés (128 MB)
- ✅ 2 fichiers transformés (4 lignes élections + 135 lignes sécurité)
- ✅ Documentation complète ETL (src/etl/README.md)

---

## Prochaine Étape

**🎯 Phase 4 - Data Science & Machine Learning**

### Étape 1 : Analyser les données transformées (1h)
```bash
# Lancer l'exploration des données
python -m jupyter notebook notebooks/01_exploration.ipynb

# Données disponibles :
# - data/processed/elections/resultats_elections_bordeaux.csv (4 lignes)
# - data/processed/indicateurs/delinquance_bordeaux.csv (135 lignes)
```

### Étape 2 : Entraîner le modèle ML (3h)
```bash
@datasci Démarre la Phase 4 : Analyse exploratoire, feature engineering,
entraînement Random Forest pour prédiction 2027
```

**Objectifs Phase 4 :**
1. Analyser corrélations entre criminalité et résultats électoraux
2. Créer features temporelles (évolution 2017→2022)
3. Entraîner Random Forest + Régression Linéaire baseline
4. Valider le modèle (R² > 0.65)
5. Générer prédictions 2027

**Note :** Le chargement en base PostgreSQL sera effectué si nécessaire pour la Phase 4.
