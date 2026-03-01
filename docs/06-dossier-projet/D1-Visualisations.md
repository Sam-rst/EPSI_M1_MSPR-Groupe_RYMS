# D1 - Résultats Exploitables (Data Visualisation)

> **Compétence C5 :** Organiser les sources de données sous forme de résultats exploitables (data visualisation) pour alimenter les outils décisionnels et visualiser les résultats de façon compréhensible permettant d'aider les directions métiers à la prise de décision.

---

## 1. Démarche de visualisation

Notre stratégie de visualisation suit le cheminement naturel d'une analyse prédictive : **comprendre le passé, valider le modèle, puis présenter l'avenir**. Chaque figure répond à une question précise et prépare la suivante. L'ensemble forme un récit cohérent pour le client Electio-Analytics.

```
 PHASE 1                    PHASE 2                   PHASE 3
 Exploration                Modélisation               Communication
 "De quoi dispose-t-on ?"   "Le modèle est-il fiable ?" "Que prédit-on pour 2027 ?"
 ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
 │ 6 figures        │──────▶│ 4 figures        │──────▶│ 5 figures        │
 │ (Notebook 01)    │        │ (Notebook 02)    │        │ + 2 cartes       │
 └─────────────────┘        └─────────────────┘        │ (Notebook 03)    │
                                                        └─────────────────┘
```

---

## 2. Phase 1 — Comprendre le terrain (Notebook 01)

**Objectif :** avant de prédire quoi que ce soit, il faut prouver au client que l'on maîtrise les données. Cette phase répond à la question : *"Sur quoi travaille-t-on exactement ?"*

| # | Figure | Type | Pourquoi cette figure ? |
|---|--------|------|------------------------|
| 1 | Distribution des communes | Histogramme + boxplot | **Point de départ obligatoire.** Montre l'hétérogénéité du territoire (41 à 268 000 hab.). Justifie le choix de pondérer les résultats par population dans la suite. |
| 2 | Participation électorale | Barplot + scatter | **Indicateur de qualité des données.** Un taux de ~77% au T1 confirme la représentativité des scrutins. La baisse 2017→2022 est un signal à surveiller. |
| 3 | Top candidats T1 | Barplot horizontal | **Vue d'ensemble par élection.** Identifie les 3 candidats majeurs en Gironde (Macron, Mélenchon, Le Pen) qui concentreront l'analyse. |
| 4 | Comparaison 2017 vs 2022 | Barplot côte-à-côte | **Première dynamique temporelle.** C'est ici que l'on voit les tendances : progression Mélenchon (+4 pts), stabilité Le Pen. C'est cette dynamique que le ML devra capter. |
| 5 | Heatmap communes x candidats | Heatmap | **Zoom sur les disparités locales.** Les 10 plus grandes communes votent différemment → le territoire n'est pas homogène. Un modèle par commune est justifié. |
| 6 | Indicateurs sécurité | Lineplot | **Validation de la donnée socio-économique.** Confirme que les indicateurs SSMSI existent et ont une tendance lisible (hausse, sauf creux COVID 2020), mais uniquement pour Bordeaux. |

**Transition vers la Phase 2 :** l'exploration confirme que les données sont cohérentes et qu'il existe des dynamiques temporelles et spatiales exploitables. On peut construire un modèle.

---

## 3. Phase 2 — Valider le modèle (Notebook 02)

**Objectif :** le client ne fait confiance à une prédiction que si on lui montre *pourquoi* le modèle fonctionne. Cette phase répond à : *"Peut-on faire confiance à votre algorithme ?"*

| # | Figure | Type | Pourquoi cette figure ? |
|---|--------|------|------------------------|
| 7 | Corrélation des features | Heatmap | **Transparence sur les inputs.** Montre que le vote précédent domine les corrélations (~0.7-0.9). Le client comprend que "le meilleur prédicteur du vote est... le vote précédent". |
| 8 | LR vs Random Forest (R²) | Barplot comparatif | **Justification du choix d'algorithme.** Le Random Forest surpasse la Régression Linéaire sur tous les candidats. Ce n'est pas un choix arbitraire, c'est mesurable. |
| 9 | Feature importance | Barplots par candidat | **Explicabilité du modèle.** Le % de voix précédent pèse 60-70%, suivi de la participation (~10-15%) et de la population (~5-10%). Le client comprend *ce qui fait bouger les prédictions*. |
| 10 | Prédictions brutes 2027 | Barplot + scatter | **Premier aperçu des résultats.** Macron ~28%, Mélenchon ~25%, Le Pen ~22%. Mais ce n'est qu'un chiffre brut — les visualisations avancées viendront le contextualiser. |

**Transition vers la Phase 3 :** le modèle est validé (R² = 0.72 pour Le Pen, meilleur score) et explicable. On peut maintenant présenter les prédictions de façon actionnable.

---

## 4. Phase 3 — Communiquer les prédictions (Notebook 03)

**Objectif :** transformer des prédictions numériques en outils d'aide à la décision. Cette phase répond à : *"Concrètement, que doit retenir le client ?"*

### 4.1 Tendances et fiabilité

| # | Figure | Type | Pourquoi cette figure ? |
|---|--------|------|------------------------|
| 11 | Évolution 2017→2022→2027 | Courbes temporelles | **Figure clé de la présentation.** Trait plein = réel, pointillé = prédiction. Le client voit d'un coup d'œil les trajectoires et distingue le connu du projeté. |
| 12 | Intervalles de confiance | Barres d'erreur IC 95% | **Honnêteté scientifique.** Code couleur R² (vert/orange/rouge) pour que le client sache immédiatement quels candidats ont des prédictions fiables et lesquels sont incertains. |

### 4.2 Dimension géographique

| # | Figure | Type | Pourquoi cette figure ? |
|---|--------|------|------------------------|
| 13 | Carte candidat en tête | **Folium interactif** | **Visualisation la plus impactante.** Chaque commune est colorée selon le candidat prédit en tête. Tooltip au survol avec le détail. Le client peut explorer librement. |
| 14 | Carte gradient Macron | **Folium interactif** | **Zoom sur un candidat.** Gradient d'intensité montrant les bastions et les faiblesses de Macron, commune par commune. Applicable aux autres candidats. |
| 15 | Top/Bottom communes | Barplots comparatifs | **Identification des extrêmes.** Pour chaque candidat majeur, les 10 communes les plus et les moins favorables. Utile pour cibler une stratégie de campagne locale. |

### 4.3 Synthèse et clivages

| # | Figure | Type | Pourquoi cette figure ? |
|---|--------|------|------------------------|
| 16 | Dashboard synthèse | Multi-panel (5 panneaux) | **Figure de conclusion.** Regroupe podium, R², intervalles de confiance, évolution et métriques clés. Un seul visuel pour tout résumer en soutenance. |
| 17 | Clivage urbain/rural | Scatter + tendance | **Insight stratégique final.** Macron et Mélenchon performent en zone urbaine, Le Pen en zone rurale. Tendance linéaire visible. Donne au client un axe d'analyse supplémentaire. |

---

## 5. Cartes interactives

Les 2 cartes Folium sont consultables dans un navigateur :

- `docs/figures/visualisation/carte_predictions_2027.html` — candidat en tête par commune
- `docs/figures/visualisation/carte_macron_2027.html` — gradient de vote Macron

Fonctionnalités : zoom, tooltip au survol (détail par candidat), légende couleur.

---

## 6. Guide de présentation orale

Fil conducteur suggéré pour la soutenance (section D1, ~5-7 min) :

1. **Accrocher** — Montrer la carte interactive (fig. 13), laisser le jury explorer 30 sec. *"Voici la Gironde en 2027 selon notre modèle."*
2. **Contextualiser** — Revenir en arrière avec la comparaison 2017/2022 (fig. 4). *"Avant de prédire, on a observé les dynamiques réelles."*
3. **Légitimer** — Montrer le barplot LR vs RF (fig. 8) et la feature importance (fig. 9). *"Notre modèle n'est pas une boîte noire : voici ce qui le fait fonctionner."*
4. **Projeter** — Présenter les courbes d'évolution (fig. 11) avec le passage réel → prédiction. *"Les pointillés, c'est notre projection."*
5. **Nuancer** — Afficher les intervalles de confiance (fig. 12). *"On est honnêtes : certaines prédictions sont plus fiables que d'autres."*
6. **Approfondir** — Scatter urbain/rural (fig. 17). *"Au-delà des chiffres, un clivage structurel se dessine."*
7. **Conclure** — Dashboard synthèse (fig. 16). *"En un visuel, tout ce qu'il faut retenir."*

---

## 7. Aide à la décision

| Question du client | Réponse visuelle | Figures |
|---------------------|-----------------|---------|
| Qui est en tête en 2027 ? | Podium + classement | fig. 16 (dashboard) |
| Quelles sont les tendances ? | Trajectoires temporelles | fig. 11 (évolution) |
| Où sont les bastions de chaque candidat ? | Carte colorée par commune | fig. 13-14 (cartes) |
| Peut-on faire confiance aux prédictions ? | Barres d'erreur + code couleur R² | fig. 12 (IC) |
| Quel est le clivage urbain/rural ? | Nuage de points + tendance | fig. 17 (scatter) |
| Quelles communes cibler en priorité ? | Communes extrêmes par candidat | fig. 15 (top/bottom) |

---

**Fichiers de référence :**

- Notebooks : `notebooks/01_exploration.ipynb`, `02_feature_engineering_ml.ipynb`, `03_visualisation_avancee.ipynb`
- Figures statiques : `docs/figures/exploration/`, `docs/figures/ml/`
- Cartes interactives : `docs/figures/visualisation/`
