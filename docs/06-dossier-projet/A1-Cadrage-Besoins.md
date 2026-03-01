# A1 - Cadrage & Collecte des Besoins

> **Compétence C1 :** Collecter les besoins en données des directions métiers afin d'avoir une vision structurée de l'ensemble des données du SI et partager la stratégie Data globale.

---

## 1. Contexte client

Electio-Analytics est une start-up de conseil stratégique pour campagnes électorales. L'équipe (1 expert politique, 1 business developer, 1 assistante) souhaite un outil de **prévision des tendances électorales à moyen terme (1-3 ans)**.

## 2. Besoins identifiés

| Besoin métier | Traduction data | Priorité |
|---------------|-----------------|----------|
| Prédire les résultats électoraux 2027 | Modèle ML régression (% voix par candidat) | Haute |
| Comprendre les facteurs d'influence | Feature importance (Random Forest) | Haute |
| Visualiser les résultats par commune | Cartes choroplèthes interactives | Moyenne |
| Croiser votes et indicateurs socio-éco | Jointures BDD multi-tables | Haute |

## 3. Périmètre validé (ADR-005)

| Paramètre | Décision | Justification |
|-----------|----------|---------------|
| Zone | Gironde (534 communes) | Volume maîtrisable pour un POC 25h |
| Élections | Présidentielles 2017 & 2022 (T1+T2) | Scrutins nationaux comparables |
| Prédiction | 2027 Tour 1 | Horizon moyen terme (1-3 ans) |
| Indicateurs | Sécurité SSMSI | Seule source disponible à la maille communale |

## 4. Sources de données retenues

| Source | API/Format | Volume | Licence |
|--------|-----------|--------|---------|
| geo.api.gouv.fr | REST JSON | 200 KB | Etalab 2.0 |
| data.gouv.fr (élections) | JSON + Parquet | 151 MB | Etalab 2.0 |
| SSMSI (sécurité) | CSV gzip | 34 MB | Etalab 2.0 |

**Source écartée** : INSEE emploi (API indisponible lors du dev).

## 5. Stratégie data globale

```mermaid
flowchart LR
    A["Données publiques\n(3 sources API)"] --> B["Pipeline ETL\n(Python)"]
    B --> C["Entrepôt PostgreSQL\n(17 tables, 3NF)"]
    C --> D["ML + Visualisation\n(Prédictions 2027)"]
```

**Fichiers de référence :**
- Roadmap : `docs/01-project-management/ROADMAP.md`
- Sources : `docs/01-project-management/SOURCES_DONNEES.md`
- Périmètre : `docs/02-architecture/adr/ADR-005-choix-perimetre-geographique.md`
