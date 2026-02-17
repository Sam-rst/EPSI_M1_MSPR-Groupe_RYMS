# A1 - Cadrage & Collecte des Besoins

> **Competence C1 :** Collecter les besoins en donnees des directions metiers afin d'avoir une vision structuree de l'ensemble des donnees du SI et partager la strategie Data globale.

---

## 1. Contexte client

Electio-Analytics est une start-up de conseil strategique pour campagnes electorales. L'equipe (1 expert politique, 1 business developer, 1 assistante) souhaite un outil de **prevision des tendances electorales a moyen terme (1-3 ans)**.

## 2. Besoins identifies

| Besoin metier | Traduction data | Priorite |
|---------------|-----------------|----------|
| Predire les resultats electoraux 2027 | Modele ML regression (% voix par candidat) | Haute |
| Comprendre les facteurs d'influence | Feature importance (Random Forest) | Haute |
| Visualiser les resultats par commune | Cartes choropletres interactives | Moyenne |
| Croiser votes et indicateurs socio-eco | Jointures BDD multi-tables | Haute |

## 3. Perimetre valide (ADR-005)

| Parametre | Decision | Justification |
|-----------|----------|---------------|
| Zone | Gironde (534 communes) | Volume maitrisable pour un POC 25h |
| Elections | Presidentielles 2017 & 2022 (T1+T2) | Scrutins nationaux comparables |
| Prediction | 2027 Tour 1 | Horizon moyen terme (1-3 ans) |
| Indicateurs | Securite SSMSI | Seule source disponible a la maille communale |

## 4. Sources de donnees retenues

| Source | API/Format | Volume | Licence |
|--------|-----------|--------|---------|
| geo.api.gouv.fr | REST JSON | 200 KB | Etalab 2.0 |
| data.gouv.fr (elections) | JSON + Parquet | 151 MB | Etalab 2.0 |
| SSMSI (securite) | CSV gzip | 34 MB | Etalab 2.0 |

**Source ecartee** : INSEE emploi (API indisponible lors du dev).

## 5. Strategie data globale

```
Donnees publiques    →    Pipeline ETL    →    Entrepot PostgreSQL    →    ML + Visualisation
(3 sources API)           (Python)              (17 tables, 3NF)           (Predictions 2027)
```

**Fichiers de reference :**
- Roadmap : `docs/01-project-management/ROADMAP.md`
- Sources : `docs/01-project-management/SOURCES_DONNEES.md`
- Perimetre : `docs/02-architecture/adr/ADR-005-choix-perimetre-geographique.md`
