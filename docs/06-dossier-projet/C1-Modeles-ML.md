# C1 - Modèles Statistiques & Machine Learning

> **Compétence C4 :** Proposer des modèles statistiques et de data science (machine learning) afin de détecter de nouveaux services, anticiper des besoins et résoudre des problématiques métiers.

---

## 1. Problématique métier

**Question** : comment prédire les résultats des Présidentielles 2027 (T1) par commune en Gironde ?

**Type de problème** : Régression (prédire un % de voix continu entre 0 et 100).

## 2. Stratégie de modélisation (ADR-002)

| Paramètre | Valeur |
|-----------|--------|
| Unité d'analyse | Commune (534) |
| Entraînement | Features 2017 T1 → Targets 2022 T1 |
| Prédiction | Features 2022 T1 → Prédiction 2027 T1 |
| Approche | 1 modèle par candidat (7 modèles) |
| Modèle principal | Random Forest Regressor |
| Baseline | Linear Regression |
| Validation | K-Fold Cross-Validation (k=5) |

**Choix Random Forest** : non-linéaire, feature importance native, robuste aux outliers, peu de tuning requis pour un POC.

## 3. Features (17 variables)

| # | Feature | Source | Type |
|---|---------|--------|------|
| 1-7 | `pct_{candidat}_prev` | Résultats élection précédente | Électoral |
| 8 | `pct_autres_prev` | Somme des autres candidats | Électoral |
| 9 | `taux_participation_prev` | Participation T1 | Électoral |
| 10 | `taux_abstention_prev` | Abstention T1 | Électoral |
| 11 | `population` | Commune | Démographique |
| 12 | `log_population` | log(population) | Démographique |
| 13-17 | `securite_*` (5 types) | Indicateurs SSMSI | Socio-économique |

## 4. Résultats

### Performance (5-Fold Cross-Validation)

| Candidat | R² | MAE (pts) | RMSE (pts) | Qualité |
|----------|-----|-----------|-----------|---------|
| **Marine LE PEN** | **0.7245** | 2.92 | 3.89 | Bon |
| Jean-Luc MÉLENCHON | 0.5093 | 2.49 | 3.34 | Acceptable |
| Emmanuel MACRON | 0.4083 | 2.89 | 3.92 | Acceptable |
| Jean LASSALLE | 0.2967 | 1.61 | 2.39 | Faible |
| Nicolas DUPONT-AIGNAN | -0.06 | 0.68 | 0.94 | Insuffisant |
| Nathalie ARTHAUD | -0.09 | 0.34 | 0.46 | Insuffisant |
| Philippe POUTOU | -0.09 | 0.46 | 0.68 | Insuffisant |

**Objectif R² > 0.65** : atteint pour Le Pen (0.7245).

### Feature importance

Pour les 3 candidats majeurs, le **% de voix à l'élection précédente** domine (~60-70%), suivi du **taux de participation** (~10-15%) et de la **population** (~5-10%).

### Prédictions 2027

- **3 745 prédictions** générées (534 communes x 7 candidats)
- Normalisées à 100% par commune
- Intervalles de confiance : prédiction ± 1.96 x RMSE
- Stockées en base PostgreSQL (table `prediction`)

## 5. Limites assumées

| Limite | Impact |
|--------|--------|
| 2 élections historiques seulement | Modèle peu robuste, R² faible pour petits candidats |
| Indicateurs sécurité Bordeaux uniquement | 533/534 communes ont sécurité = 0 |
| Candidats 2027 supposés identiques | Hypothèse de stabilité non garantie |
| Absence de données emploi | Feature manquante |

**Fichiers de référence :**
- Notebook ML : `notebooks/02_feature_engineering_ml.ipynb`
- ADR : `docs/02-architecture/adr/ADR-002-choix-algo-ml.md`
- Figures : `docs/figures/ml/`
