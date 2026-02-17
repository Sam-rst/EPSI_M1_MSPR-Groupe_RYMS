# Dossier Projet - Electio-Analytics

> **MSPR Bloc 3 - Big Data & Business Intelligence (RNCP35584)**
> Groupe RYMS (Samuel RESSIOT, Yassine ZOUITNI, Rudolph ATTISSO, Marc-Alex NEZOUT) | Fevrier 2026

---

## Presentation

Ce dossier structure l'ensemble des livrables du POC Electio-Analytics en les organisant selon les **9 competences evaluees** du Bloc 3. Chaque section pointe vers les preuves techniques du projet.

| Donnee | Valeur |
|--------|--------|
| **Client** | Electio-Analytics (start-up conseil electoral) |
| **Objectif** | Predire les resultats des Presidentielles 2027 (T1) |
| **Perimetre** | Gironde - 534 communes |
| **Stack** | Python / PostgreSQL / Scikit-Learn / Folium |
| **Equipe** | Samuel RESSIOT, Yassine ZOUITNI, Rudolph ATTISSO, Marc-Alex NEZOUT |

---

## Table des matieres par competence

| # | Competence Bloc 3 | Section |
|---|-------------------|---------|
| C1 | Collecter les besoins en donnees des directions metiers | [A1 - Cadrage & Besoins](A1-Cadrage-Besoins.md) |
| C2 | Definir une architecture business intelligence | [A2 - Architecture BI](A2-Architecture-BI.md) |
| C3 | Definir une strategie big data (collecte → traitements) | [B1 - Pipeline ETL](B1-Pipeline-ETL.md) |
| C4 | Proposer des modeles statistiques et de data science (ML) | [C1 - Modeles ML](C1-Modeles-ML.md) |
| C5 | Organiser les sources sous forme de resultats exploitables | [D1 - Visualisations](D1-Visualisations.md) |
| C6 | Definir les donnees de reference (referentiel) | [B2 - Entrepot & Referentiels](B2-Entrepot-Referentiels.md) |
| C7 | Creer un entrepot unique | [B2 - Entrepot & Referentiels](B2-Entrepot-Referentiels.md) | 
| C8 | Assurer la qualite des donnees | [E1 - Qualite des Donnees](E1-Qualite-Donnees.md) | 
| C9 | Appliquer les procedures RGPD | [E2 - Securite & RGPD](E2-Securite-RGPD.md) | 

---

## Livrables techniques

| Livrable | Chemin dans le repo |
|----------|---------------------|
| Pipeline ETL complet | `src/etl/` (extract / transform / load) |
| Base de donnees PostgreSQL | `src/database/` (17 modeles SQLAlchemy) |
| Notebook exploration | `notebooks/01_exploration.ipynb` |
| Notebook ML | `notebooks/02_feature_engineering_ml.ipynb` |
| Notebook visualisation | `notebooks/03_visualisation_avancee.ipynb` |
| Cartes interactives | `docs/figures/visualisation/*.html` |
| Rapport de synthese | `docs/05-reports/RAPPORT_SYNTHESE.md` |
| Audit RGPD | `docs/05-reports/AUDIT_RGPD.md` |
| Support de presentation | `docs/05-reports/PRESENTATION.md` |
| 5 ADRs | `docs/02-architecture/adr/` |
| Documentation BDD (8 docs) | `docs/02-architecture/database/` |

---

## Navigation rapide

```
docs/06-dossier-projet/
├── 00-INDEX.md               ← Vous etes ici
├── A1-Cadrage-Besoins.md     ← C1 : Besoins & strategie data
├── A2-Architecture-BI.md     ← C2 : Architecture & decisions
├── B1-Pipeline-ETL.md        ← C3 : Strategie big data
├── B2-Entrepot-Referentiels.md ← C6+C7 : Referentiels & entrepot
├── C1-Modeles-ML.md          ← C4 : Machine Learning
├── D1-Visualisations.md      ← C5 : Data visualisation
├── E1-Qualite-Donnees.md     ← C8 : Qualite des donnees
└── E2-Securite-RGPD.md       ← C9 : RGPD & securite
```
