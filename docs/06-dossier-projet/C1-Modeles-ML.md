# C1 - Modeles Statistiques & Machine Learning

> **Competence C4 :** Proposer des modeles statistiques et de data science (machine learning) afin de detecter de nouveaux services, anticiper des besoins et resoudre des problematiques metiers.

---

## 1. Problematique metier

**Question** : comment predire les resultats des Presidentielles 2027 (T1) par commune en Gironde ?

**Type de probleme** : Regression (predire un % de voix continu entre 0 et 100).

## 2. Strategie de modelisation (ADR-002)

| Parametre | Valeur |
|-----------|--------|
| Unite d'analyse | Commune (534) |
| Entrainement | Features 2017 T1 → Targets 2022 T1 |
| Prediction | Features 2022 T1 → Prediction 2027 T1 |
| Approche | 1 modele par candidat (7 modeles) |
| Modele principal | Random Forest Regressor |
| Baseline | Linear Regression |
| Validation | K-Fold Cross-Validation (k=5) |

**Choix Random Forest** : non-lineaire, feature importance native, robuste aux outliers, peu de tuning requis pour un POC.

## 3. Features (17 variables)

| # | Feature | Source | Type |
|---|---------|--------|------|
| 1-7 | `pct_{candidat}_prev` | Resultats election precedente | Electoral |
| 8 | `pct_autres_prev` | Somme des autres candidats | Electoral |
| 9 | `taux_participation_prev` | Participation T1 | Electoral |
| 10 | `taux_abstention_prev` | Abstention T1 | Electoral |
| 11 | `population` | Commune | Demographique |
| 12 | `log_population` | log(population) | Demographique |
| 13-17 | `securite_*` (5 types) | Indicateurs SSMSI | Socio-economique |

## 4. Resultats

### Performance (5-Fold Cross-Validation)

| Candidat | R2 | MAE (pts) | RMSE (pts) | Qualite |
|----------|-----|-----------|-----------|---------|
| **Marine LE PEN** | **0.7245** | 2.92 | 3.89 | Bon |
| Jean-Luc MELENCHON | 0.5093 | 2.49 | 3.34 | Acceptable |
| Emmanuel MACRON | 0.4083 | 2.89 | 3.92 | Acceptable |
| Jean LASSALLE | 0.2967 | 1.61 | 2.39 | Faible |
| Nicolas DUPONT-AIGNAN | -0.06 | 0.68 | 0.94 | Insuffisant |
| Nathalie ARTHAUD | -0.09 | 0.34 | 0.46 | Insuffisant |
| Philippe POUTOU | -0.09 | 0.46 | 0.68 | Insuffisant |

**Objectif R2 > 0.65** : atteint pour Le Pen (0.7245).

### Feature importance

Pour les 3 candidats majeurs, le **% de voix a l'election precedente** domine (~60-70%), suivi du **taux de participation** (~10-15%) et de la **population** (~5-10%).

### Predictions 2027

- **3 745 predictions** generees (534 communes x 7 candidats)
- Normalisees a 100% par commune
- Intervalles de confiance : prediction ± 1.96 x RMSE
- Stockees en base PostgreSQL (table `prediction`)

## 5. Limites assumees

| Limite | Impact |
|--------|--------|
| 2 elections historiques seulement | Modele peu robuste, R2 faible pour petits candidats |
| Indicateurs securite Bordeaux uniquement | 533/534 communes ont securite = 0 |
| Candidats 2027 supposes identiques | Hypothese de stabilite non garantie |
| Absence de donnees emploi | Feature manquante |

**Fichiers de reference :**
- Notebook ML : `notebooks/02_feature_engineering_ml.ipynb`
- ADR : `docs/02-architecture/adr/ADR-002-choix-algo-ml.md`
- Figures : `docs/figures/ml/`
