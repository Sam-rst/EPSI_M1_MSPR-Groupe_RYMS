# Dossier Projet - Electio-Analytics

> **MSPR Bloc 3 - Big Data & Business Intelligence (RNCP35584)**
> Groupe RYMS (Samuel RESSIOT, Yassine ZOUITNI, Rudolph ATTISSO, Marc-Alex NEZOUT) | Février 2026

---

## Présentation

Ce dossier structure l'ensemble des livrables du POC Electio-Analytics en les organisant selon les **9 compétences évaluées** du Bloc 3. Chaque section pointe vers les preuves techniques du projet.

| Donnée | Valeur |
|--------|--------|
| **Client** | Electio-Analytics (start-up conseil électoral) |
| **Objectif** | Prédire les résultats des Présidentielles 2027 (T1) |
| **Périmètre** | Gironde - 534 communes |
| **Stack** | Python / PostgreSQL / Scikit-Learn / Folium |
| **Équipe** | Samuel RESSIOT, Yassine ZOUITNI, Rudolph ATTISSO, Marc-Alex NEZOUT |

---

## Table des matières par compétence

| # | Compétence Bloc 3 | Section |
|---|-------------------|---------|
| C1 | Collecter les besoins en données des directions métiers | [A1 - Cadrage & Besoins](A1-Cadrage-Besoins.md) |
| C2 | Définir une architecture business intelligence | [A2 - Architecture BI](A2-Architecture-BI.md) |
| C3 | Définir une stratégie big data (collecte → traitements) | [B1 - Pipeline ETL](B1-Pipeline-ETL.md) |
| C4 | Proposer des modèles statistiques et de data science (ML) | [C1 - Modèles ML](C1-Modeles-ML.md) |
| C5 | Organiser les sources sous forme de résultats exploitables | [D1 - Visualisations](D1-Visualisations.md) |
| C6 | Définir les données de référence (référentiel) | [B2 - Entrepôt & Référentiels](B2-Entrepot-Referentiels.md) |
| C7 | Créer un entrepôt unique | [B2 - Entrepôt & Référentiels](B2-Entrepot-Referentiels.md) |
| C8 | Assurer la qualité des données | [E1 - Qualité des Données](E1-Qualite-Donnees.md) |
| C9 | Appliquer les procédures RGPD | [E2 - Sécurité & RGPD](E2-Securite-RGPD.md) |

---

## Livrables techniques

| Livrable | Chemin dans le repo |
|----------|---------------------|
| Pipeline ETL complet | `src/etl/` (extract / transform / load) |
| Base de données PostgreSQL | `src/database/` (17 modèles SQLAlchemy) |
| Notebook exploration | `notebooks/01_exploration.ipynb` |
| Notebook ML | `notebooks/02_feature_engineering_ml.ipynb` |
| Notebook visualisation | `notebooks/03_visualisation_avancee.ipynb` |
| Cartes interactives | `docs/figures/visualisation/*.html` |
| Rapport de synthèse | `docs/05-reports/RAPPORT_SYNTHESE.md` |
| Audit RGPD | `docs/05-reports/AUDIT_RGPD.md` |
| Support de présentation | `docs/05-reports/PRESENTATION.md` |
| 5 ADRs | `docs/02-architecture/adr/` |
| Documentation BDD (8 docs) | `docs/02-architecture/database/` |

---

## Navigation rapide

```
docs/06-dossier-projet/
├── 00-INDEX.md               ← Vous êtes ici
├── A1-Cadrage-Besoins.md     ← C1 : Besoins & stratégie data
├── A2-Architecture-BI.md     ← C2 : Architecture & décisions
├── B1-Pipeline-ETL.md        ← C3 : Stratégie big data
├── B2-Entrepot-Referentiels.md ← C6+C7 : Référentiels & entrepôt
├── C1-Modeles-ML.md          ← C4 : Machine Learning
├── D1-Visualisations.md      ← C5 : Data visualisation
├── E1-Qualite-Donnees.md     ← C8 : Qualité des données
└── E2-Securite-RGPD.md       ← C9 : RGPD & sécurité
```
