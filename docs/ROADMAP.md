# ROADMAP - Electio-Analytics POC

## Périmètre Validé

**Zone géographique :** Bordeaux - Arrondissement Centre
**Type d'élection :** Présidentielles (2017, 2022) → Prédiction 2027
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

## Phase 2 : Architecture & Modélisation ⏳ EN COURS (3h/5h complétées)

**Agent :** `@archi`

### Objectifs
- Définir l'architecture technique du POC
- Concevoir le Modèle Conceptuel de Données (MCD)
- Documenter les choix techniques (ADRs)

### Livrables
| Livrable | Fichier | Statut | Description |
|----------|---------|--------|-------------|
| **MCD** | `docs/MCD.md` | ✅ FAIT | Schéma entités-relations (5 entités: Territoire, Election_Result, Indicateur_Securite, Indicateur_Emploi, Prediction) |
| **ADR-001** | `docs/adr/ADR-001-choix-bdd.md` | ✅ FAIT | Choix SQL (PostgreSQL) vs NoSQL justifié |
| **Architecture ETL** | `docs/ARCHITECTURE.md` | ❌ MANQUANT | Pipeline d'ingestion et traitement des données |
| **ADR-002** | `docs/adr/ADR-002-algo-ml.md` | ❌ MANQUANT | Algorithme de prédiction (Régression, Random Forest, etc.) |

### Tâches
1. ✅ Identifier les entités principales (Bureaux de vote, IRIS, Indicateurs, Résultats)
2. ✅ Définir les relations et cardinalités
3. ✅ Choisir le SGBD (PostgreSQL retenu avec PostGIS)
4. ⏳ Documenter l'architecture ETL (Sources → Staging → Warehouse → ML) - **EN ATTENTE**

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
| **Script ETL Elections** | `src/etl/extract_elections.py` | Extraction résultats présidentielles 2017/2022 (data.gouv.fr) |
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

**Bloquants identifiés :**
- Accès aux APIs data.gouv.fr (rate limiting ?)
- Qualité des données SSMSI au niveau arrondissement (granularité suffisante ?)
- Mapping géographique Bureaux de vote ↔ IRIS (nécessite géocodage)

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
| **Phase 2** : Architecture | ⏳ EN COURS | 3h/5h | 60% |
| **Phase 3** : Data Engineering | ⏸️ PAS COMMENCÉE | 0h/8h | 0% |
| **Phase 4** : Data Science | ⏸️ PAS COMMENCÉE | 0h/6h | 0% |
| **Phase 5** : Visualisation | ⏸️ PAS COMMENCÉE | 0h/4h | 0% |
| **Phase 6** : Revue Qualité | ⏸️ PAS COMMENCÉE | 0h/1h | 0% |

**Total consommé :** 4h / 25h (16%)

---

## Prochaine Étape

**Option A :** Compléter Phase 2 (Architecture ETL + ADR-002 algorithme ML)
```
@archi Crée le document ARCHITECTURE.md et l'ADR-002 pour finaliser la Phase 2
```

**Option B :** Démarrer Phase 3 (Data Engineering) avec architecture minimale
```
@dataeng Démarre la Phase 3 : collecte et ETL des données (Élections, Sécurité, Emploi)
```

**Recommandation PM :** Option B (démarrer ETL) - L'ADR-002 sera fait après exploration données en Phase 4.
