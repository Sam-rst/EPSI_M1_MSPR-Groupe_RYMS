# Rapport de Synthese - Electio-Analytics

> **POC : Prediction des tendances electorales 2027**
> Groupe RYMS - EPSI M1 - Bloc 3 RNCP35584
> Date : Fevrier 2026

---

## 1. Contexte et Objectifs

### 1.1 Presentation du client

Electio-Analytics est une start-up specialisee dans le conseil strategique dedie aux campagnes electorales. Son besoin : mettre en place une capacite de prevision des tendances electorales a moyen terme (1-3 ans) en croisant donnees de votes historiques et indicateurs socio-economiques.

### 1.2 Objectif du POC

Developper un outil de prediction des resultats des **Presidentielles 2027 (Tour 1)** a l'echelle communale, en exploitant :

- Les resultats electoraux historiques (2017 et 2022)
- Les indicateurs de securite (SSMSI 2016-2024)
- Les donnees geographiques et demographiques (INSEE)

### 1.3 Perimetre valide

| Parametre | Valeur |
|-----------|--------|
| Zone geographique | Gironde (departement 33) - 534 communes |
| Elections | Presidentielles 2017 & 2022 (T1 + T2) |
| Prediction | Presidentielles 2027 (T1) |
| Candidats | 7 candidats communs 2017-2022 |

**Justification du perimetre** (ADR-005) : une zone unique permet de limiter la volumetrie, de valider l'approche methodologique et d'assurer la faisabilite dans le budget de 25h.

---

## 2. Architecture et Choix Techniques

### 2.1 Stack technique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Langage | Python 3.12 | Ecosysteme Data Science mature |
| Base de donnees | PostgreSQL 15 + PostGIS | Robustesse, SQL avance, geospatial (ADR-001) |
| ORM | SQLAlchemy 2.x | Typage fort, migrations Alembic |
| ETL | Architecture modulaire maison | Separation Extract/Transform/Load (ADR-003) |
| ML | Scikit-Learn (RandomForest) | Non-lineaire, feature importance, minimal tuning (ADR-002) |
| Visualisation | Matplotlib, Seaborn, Folium | Statique + cartes interactives |
| Infrastructure | Docker Compose | Reproductibilite PostgreSQL |
| Gestion packages | UV | Performance, lock file deterministe |

### 2.2 Schema de donnees (v3.0)

Le schema comporte **17 tables** organisees en 5 domaines :

```
Geographie          Candidats           Elections
─────────────       ─────────────       ─────────────
Region (1)          Candidat (16)       TypeElection (1)
Departement (1)     Parti (15)          Election (2)
Canton (0)          CandidatParti (25)  ElectionTerritoire (1073)
Commune (534)
Arrondissement      Resultats           Indicateurs
Bureau de Vote      ─────────────       ─────────────
                    Participation (2146) TypeIndicateur (5)
                    ResultatCandidat    Indicateur (45)
                    (14484)             Prediction (3745)
```

**Systeme polymorphe de territoire** : les tables `resultat_*`, `indicateur` et `prediction` utilisent un couple `(id_territoire, type_territoire)` pour referencer n'importe quel niveau geographique sans jointures multiples.

### 2.3 Architecture ETL

Pipeline modulaire en 3 phases :

```
EXTRACT                 TRANSFORM               LOAD
─────────────────       ─────────────────       ─────────────────
geo.api.gouv.fr    →    JSON → CSV normalisé   →    PostgreSQL
data.gouv.fr       →    Parquet → CSV agrege   →    (17 tables)
SSMSI (CSV)        →    CSV → CSV filtre       →    21 007 lignes
```

**Sources de donnees :**

| Source | API/Format | Volume | Contenu |
|--------|-----------|--------|---------|
| geo.api.gouv.fr | REST JSON | 200 KB | 534 communes, 1 dept, 1 region |
| data.gouv.fr | JSON + Parquet | 151 MB | Resultats presidentielles T1+T2 |
| SSMSI | CSV gzip | 34 MB | Criminalite Bordeaux 2016-2024 |

---

## 3. Methodologie Machine Learning

### 3.1 Strategie de modelisation (ADR-002)

| Parametre | Valeur |
|-----------|--------|
| Unite d'analyse | Commune (534 alignees) |
| Entrainement | Features 2017 T1 → Targets 2022 T1 |
| Prediction | Features 2022 T1 → Prediction 2027 T1 |
| Approche | 1 modele Random Forest par candidat (7 modeles) |
| Baseline | Linear Regression |
| Validation | K-Fold Cross-Validation (k=5, shuffle, seed=42) |

### 3.2 Feature Engineering (17 variables)

| Categorie | Features | Source |
|-----------|----------|--------|
| Votes precedents | `pct_{candidat}_prev` (7 features) | resultat_candidat |
| Autres candidats | `pct_autres_prev` | Somme hors 7 communs |
| Participation | `taux_participation_prev`, `taux_abstention_prev` | resultat_participation |
| Demographie | `population`, `log_population` | commune |
| Securite | `securite_{type}` (5 features) | indicateur (0 si hors Bordeaux) |

### 3.3 Resultats

#### Comparaison Linear Regression vs Random Forest

| Candidat | LR R2 | RF R2 | RF MAE (pts) | RF RMSE (pts) | Qualite |
|----------|-------|-------|-------------|--------------|---------|
| Marine LE PEN | 0.58 | **0.7245** | 2.92 | 3.89 | Bon |
| Jean-Luc MELENCHON | 0.38 | **0.5093** | 2.49 | 3.34 | Acceptable |
| Emmanuel MACRON | 0.27 | **0.4083** | 2.89 | 3.92 | Acceptable |
| Jean LASSALLE | 0.15 | **0.2967** | 1.61 | 2.39 | Faible |
| Nicolas DUPONT-AIGNAN | -0.12 | **-0.06** | 0.68 | 0.94 | Insuffisant |
| Nathalie ARTHAUD | -0.15 | **-0.09** | 0.34 | 0.46 | Insuffisant |
| Philippe POUTOU | -0.13 | **-0.09** | 0.46 | 0.68 | Insuffisant |

**Objectif R2 > 0.65** : atteint pour Marine Le Pen (0.7245). Le Random Forest surpasse la baseline sur tous les candidats.

#### Features les plus importantes

Pour les 3 candidats majeurs, la feature dominante est systematiquement le **pourcentage de voix a l'election precedente** (~60-70% d'importance). Les facteurs secondaires sont :
- Taux de participation (10-15%)
- Population / log_population (5-10%)
- Indicateurs securite : impact limite (disponibles uniquement pour Bordeaux)

### 3.4 Predictions 2027

**3 745 predictions** generees (534 communes x 7 candidats), normalisees a 100% par commune.

| Candidat | % predit (moy. ponderee) | IC 95% |
|----------|--------------------------|--------|
| Emmanuel MACRON | ~28% | ±7.7 pts |
| Marine LE PEN | ~22% | ±7.6 pts |
| Jean-Luc MELENCHON | ~25% | ±6.5 pts |
| Jean LASSALLE | ~3% | ±4.7 pts |
| Nicolas DUPONT-AIGNAN | ~3% | ±1.8 pts |
| Nathalie ARTHAUD | ~1% | ±0.9 pts |
| Philippe POUTOU | ~1% | ±1.3 pts |

Intervalles de confiance calcules : prediction ± 1.96 x RMSE.

---

## 4. Resultats et Visualisations

### 4.1 Analyse exploratoire (Notebook 01)

6 figures generees couvrant :

1. **Distribution des communes** : forte heterogeneite de population (41 a 268 000 hab.)
2. **Participation** : taux moyen ~77% en T1, baisse entre 2017 et 2022
3. **Top candidats T1** : Macron et Melenchon en tete en Gironde
4. **Comparaison 2017 vs 2022** : progression Melenchon, stabilite Le Pen
5. **Heatmap communes** : variations significatives entre zones urbaines et rurales
6. **Indicateurs securite** : hausse tendancielle (sauf 2020 COVID)

### 4.2 Visualisations ML (Notebook 02)

4 figures : correlation features, comparaison LR/RF, feature importance, predictions 2027.

### 4.3 Visualisations avancees (Notebook 03)

7 figures / cartes :

1. **Courbes d'evolution 2017→2022→2027** : trajectoires par candidat (reel + prediction)
2. **Intervalles de confiance** : barres d'erreur IC 95% par candidat avec code couleur R2
3. **Carte chorolethe** : candidat en tete par commune (Folium interactif)
4. **Carte gradient Macron** : intensite du vote par commune
5. **Top/Bottom communes** : 10 communes les plus et moins favorables par candidat
6. **Dashboard de synthese** : vue multi-panel (podium, R2, IC, evolution, metriques)
7. **Clivage urbain/rural** : dispersion du vote en fonction de la population

---

## 5. Qualite des Donnees et Conformite

### 5.1 Assurance qualite

| Mesure | Implementation |
|--------|---------------|
| Validation colonnes | Verification presence/type/valeurs dans chaque CSV |
| Integrite referentielle | Contraintes FK strictes en PostgreSQL |
| Unicite | Contraintes UNIQUE sur les cles naturelles |
| Bornes | CHECK constraints (0-100% pour les pourcentages) |
| Tests | 2 revues de code (6.5/10 → 7/10) |

### 5.2 Conformite RGPD

| Exigence | Statut |
|----------|--------|
| Donnees personnelles | Aucune : donnees agregees par commune/bureau |
| Sources | 100% donnees publiques (data.gouv.fr, INSEE, SSMSI) |
| Droit a l'oubli | Non applicable (pas de donnees individuelles) |
| Tracabilite | Attribution des sources documentee |
| Securite acces | Credentials en variables d'environnement (.env) |
| Injection SQL | Requetes parametrees (SQLAlchemy text()) |

---

## 6. Limites et Pistes d'Amelioration

### 6.1 Limites identifiees

| Limite | Impact | Severite |
|--------|--------|----------|
| Seulement 2 elections historiques (2017, 2022) | Pas de serie temporelle longue, modele peu robuste | Haute |
| Indicateurs securite limites a Bordeaux | 533/534 communes ont securite = 0 | Haute |
| Hypothese de stabilite des candidats | Les candidats 2027 ne seront pas les memes | Moyenne |
| Absence de donnees emploi/pauvrete | Feature manquante vs cahier des charges | Moyenne |
| Petits candidats (<2%) imprevisibles | R2 negatif pour Arthaud, Poutou, Dupont-Aignan | Faible |
| Normalisation a 100% | Peut biaiser les predictions individuelles | Faible |

### 6.2 Pistes d'amelioration (post-POC)

1. **Enrichir la serie temporelle** : integrer 10+ elections (municipales, legislatives, europeennes) pour capturer les tendances de fond
2. **Ajouter des indicateurs** : emploi (INSEE), revenus, education, demographie
3. **Etendre le perimetre** : deployer sur d'autres departements puis national
4. **Modeles avances** : XGBoost, LSTM (si serie temporelle longue), ensemble stacking
5. **Automatiser le pipeline** : orchestration Airflow/Prefect, CI/CD
6. **Tests unitaires** : couverture pytest sur ETL et ML
7. **Dashboard temps reel** : Streamlit avec mise a jour automatique

---

## 7. Conclusion

Ce POC demontre la faisabilite d'un outil de prediction electorale a l'echelle communale. Les resultats sont encourageants pour les 3 candidats majeurs (Macron, Le Pen, Melenchon) avec un R2 atteignant **0.7245** pour Le Pen, depassant l'objectif de 0.65.

Le pipeline ETL industrialise, le schema de donnees normalise et l'architecture modulaire permettent une scalabilite vers un produit complet. Les principales limites (serie temporelle courte, indicateurs limites) sont clairement identifiees et des pistes d'amelioration concretes sont proposees.

**Recommandation** : Electio-Analytics dispose d'une base technique solide pour evoluer vers un produit commercial, a condition d'investir dans l'enrichissement des donnees et l'extension du perimetre geographique.

---

## Annexes

### A. Structure du projet

```
EPSI_M1_MSPR-Groupe_RYMS/
├── data/raw/              # 185 MB donnees brutes
├── data/processed/        # 3 MB donnees nettoyees
├── docs/                  # 30+ documents
│   ├── 02-architecture/   # 5 ADRs, MCD, MLD
│   └── 05-reports/        # Ce rapport
├── notebooks/             # 3 Jupyter notebooks
│   ├── 01_exploration.ipynb
│   ├── 02_feature_engineering_ml.ipynb
│   └── 03_visualisation_avancee.ipynb
└── src/
    ├── database/          # 17 modeles SQLAlchemy
    └── etl/               # Pipeline Extract/Transform/Load
```

### B. Budget temps

| Phase | Budget | Reel | Ecart |
|-------|--------|------|-------|
| 1. Cadrage | 1h | 1h | 0% |
| 2. Architecture | 5h | 5h | 0% |
| 3. Data Engineering | 8h | 12h | +50% |
| 4. Data Science | 6h | 6h | 0% |
| 5. Visualisation & Rapport | 4h | 4h | 0% |
| 6. Revue & Qualite | 1h | 2h | +100% |
| **Total** | **25h** | **30h** | **+20%** |

Le depassement de la Phase 3 s'explique par la complexite du systeme polymorphe de territoire et les 4 migrations successives du schema.

### C. Decisions d'architecture (ADRs)

| ADR | Decision | Justification |
|-----|----------|---------------|
| ADR-001 | PostgreSQL | Robustesse, SQL avance, PostGIS |
| ADR-002 | Random Forest | Non-lineaire, feature importance |
| ADR-003 | ETL modulaire (Option 3) | Separation des responsabilites |
| ADR-004 | Schema v3.0 | Systeme polymorphe de territoire |
| ADR-005 | Perimetre Bordeaux | Maitrise volumetrie, faisabilite |

### D. Equipe

| Membre | Role |
|--------|------|
| Samuel Ressiot | Data Engineer / DevOps |
| Yassine Zouitni | Data Scientist |
| Rudolph Attisso | Data Analyst |
| Marc-Alex Nezout | Project Manager |
