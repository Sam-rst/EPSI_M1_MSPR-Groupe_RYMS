# D1 - Resultats Exploitables (Data Visualisation)

> **Competence C5 :** Organiser les sources de donnees sous forme de resultats exploitables (data visualisation) pour alimenter les outils decisionnels et visualiser les resultats de facon comprehensible permettant d'aider les directions metiers a la prise de decision.

---

## 1. Catalogue des figures

### Notebook 01 - Exploration (6 figures)

| # | Figure | Type | Insight cle |
|---|--------|------|-------------|
| 1 | Distribution communes | Histogramme + boxplot | Forte heterogeneite (41 a 268 000 hab.) |
| 2 | Participation | Barplot + scatter | Taux ~77% T1, baisse 2017→2022 |
| 3 | Top candidats T1 | Barplot horizontal | Macron et Melenchon en tete en Gironde |
| 4 | Comparaison 2017 vs 2022 | Barplot cote-a-cote | Progression Melenchon, stabilite Le Pen |
| 5 | Heatmap communes x candidats | Heatmap | Variations urbain/rural marquees |
| 6 | Indicateurs securite | Lineplot | Hausse tendancielle (sauf 2020 COVID) |

### Notebook 02 - ML (4 figures)

| # | Figure | Type | Insight cle |
|---|--------|------|-------------|
| 7 | Correlation features | Heatmap | Vote precedent = feature dominante |
| 8 | LR vs Random Forest | Barplot R2 | RF surpasse LR sur tous les candidats |
| 9 | Feature importance | Barplots | % voix precedent = 60-70% d'importance |
| 10 | Predictions 2027 | Barplot + scatter | Macron ~28%, Melenchon ~25%, Le Pen ~22% |

### Notebook 03 - Visualisation avancee (5 figures + 2 cartes)

| # | Figure | Type | Insight cle |
|---|--------|------|-------------|
| 11 | Evolution 2017→2022→2027 | Courbes temporelles | Trajectoires par candidat (reel + prediction) |
| 12 | Intervalles de confiance | Barres d'erreur IC 95% | Fiabilite variable selon le candidat |
| 13 | Carte candidat en tete | **Folium interactif** | Couleur par commune, tooltip detaille |
| 14 | Carte gradient Macron | **Folium interactif** | Intensite du vote par commune |
| 15 | Top/Bottom communes | Barplots comparatifs | Communes extremes par candidat |
| 16 | Dashboard synthese | Multi-panel | Vue consolidee (podium, R2, IC, evolution) |
| 17 | Clivage urbain/rural | Scatter + tendance | Macron/Melenchon urbain, Le Pen rural |

## 2. Cartes interactives

Les 2 cartes Folium sont consultables dans un navigateur :
- `docs/figures/visualisation/carte_predictions_2027.html`
- `docs/figures/visualisation/carte_macron_2027.html`

Fonctionnalites : zoom, tooltip au survol (detail par candidat), legende couleur.

## 3. Aide a la decision

| Question du client | Reponse visuelle |
|---------------------|-----------------|
| Qui est en tete en 2027 ? | Dashboard synthese (fig. 16) |
| Quelles sont les tendances ? | Courbes d'evolution (fig. 11) |
| Ou sont les bastions de chaque candidat ? | Cartes choropletres (fig. 13-14) |
| Peut-on faire confiance aux predictions ? | Intervalles de confiance (fig. 12) |
| Quel est le clivage urbain/rural ? | Scatter plots (fig. 17) |

**Fichiers de reference :**
- Notebooks : `notebooks/01_exploration.ipynb`, `02_feature_engineering_ml.ipynb`, `03_visualisation_avancee.ipynb`
- Figures statiques : `docs/figures/exploration/`, `docs/figures/ml/`
- Cartes interactives : `docs/figures/visualisation/`
