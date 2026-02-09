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

## Phase 3 : Data Engineering (8h)

**Agent :** `@dataeng`

### Objectifs
- Collecter les données brutes des 3 sources
- Nettoyer et transformer les données
- Charger dans la base de données

### Livrables
| Livrable | Fichier | Description |
|----------|---------|-------------|
| **Script ETL Elections** | `src/etl/extract_elections.py` | Extraction résultats présidentielles 2017 & 2022 (1er et 2nd tours) depuis data.gouv.fr |
| **Script ETL Sécurité** | `src/etl/extract_securite.py` | Extraction crimes/délits SSMSI (2017-2024) |
| **Script ETL Emploi** | `src/etl/extract_emploi.py` | Extraction données emploi/chômage INSEE IRIS |
| **Script Nettoyage** | `src/etl/transform.py` | Harmonisation géographique (Bureaux → IRIS), gestion valeurs manquantes |
| **Script Chargement** | `src/etl/load.py` | Insertion en base + validation intégrité |
| **Base de données** | `data/processed/electio_analytics.db` | Base SQLite ou PostgreSQL |

### Tâches
1. Télécharger datasets sources (data.gouv.fr, INSEE, SSMSI)
2. Harmoniser les granularités géographiques (Bureaux de vote ↔ IRIS)
3. Gérer les valeurs manquantes (imputation ou exclusion)
4. Valider la cohérence temporelle (2017-2024)
5. Documenter le dictionnaire de données

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
| **Phase 3** : Data Engineering | ⏸️ PAS COMMENCÉE | 0h/8h | 0% |
| **Phase 4** : Data Science | ⏸️ PAS COMMENCÉE | 0h/6h | 0% |
| **Phase 5** : Visualisation | ⏸️ PAS COMMENCÉE | 0h/4h | 0% |
| **Phase 6** : Revue Qualité | ⏸️ PAS COMMENCÉE | 0h/1h | 0% |

**Total consommé :** 6h / 25h (24%)

### Livrables Phase 1 & 2 Complétés (9 documents)
- ✅ ROADMAP.md (planning 25h, 6 phases)
- ✅ MCD.md (5 entités, relations, volumétrie)
- ✅ ADR-001 (PostgreSQL vs NoSQL)
- ✅ ADR-002 (Random Forest vs autres algos ML)
- ✅ ARCHITECTURE.md (Pipeline ETL complet)
- ✅ SOURCES_DONNEES.md (4 fichiers élections + métadonnées)
- ✅ download_elections.py (téléchargement automatisé)
- ✅ requirements.txt (dépendances Python)
- ✅ Documentation corrigée (1er et 2nd tours précisés)

---

## Prochaine Étape

**🎯 Phase 3 - Data Engineering : Téléchargement et Extraction**

### Étape 1 : Télécharger les données électorales (0.5h)
```bash
# Installer les dépendances
pip install -r requirements.txt

# Télécharger les 4 fichiers CSV électoraux
python src/etl/extract/download_elections.py

# Vérifier les téléchargements
ls data/raw/elections/
# Attendu : 4 fichiers (2017 T1/T2, 2022 T1/T2)
```

### Étape 2 : Lancer Phase 3 complète
```
@dataeng Démarre la Phase 3 : Télécharge et transforme les données (Élections, Sécurité, Emploi)
```

**Alternative :** Téléchargement manuel via les URLs dans `docs/SOURCES_DONNEES.md`

**Note :** ADR-002 (choix algorithme ML) sera créé en Phase 4 après exploration des données.
