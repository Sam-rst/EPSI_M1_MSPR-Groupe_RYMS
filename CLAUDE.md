# PROJET MSPR: Electio-Analytics - Prédictions Électorales

## Contexte Global
Ce projet est une Preuve de Concept (POC) pour la startup "Electio-Analytics".
**Objectif :** Développer un outil de prédiction des tendances électorales à moyen terme (1-3 ans) en croisant des données de votes historiques avec des indicateurs socio-économiques (sécurité, emploi, etc.)[cite: 36, 41, 50].

## Commandes Agents
Utilise ces commandes pour activer un agent spécifique selon la phase du projet :

- `@pm` : Active le **Project Manager**. Pour le cadrage, le suivi des besoins et la roadmap.
- `@archi` : Active le **Tech Lead / Architecte**. Pour les choix techniques, le MCD, l'ETL et les ADR.
- `@review` : Active le **Code Reviewer**. Pour la qualité du code, la validation ML et la documentation.
- `@dataeng` : Active le **Data Engineer**. Pour l'ETL, le nettoyage et la base de données.
- `@datasci` : Active le **Data Scientist**. Pour le Machine Learning et les algos.
- `@analyst` : Active le **Data Analyst**. Pour les graphiques, le rapport et les slides.

## Règles Fondamentales (Non négociables)
1. **Périmètre Géographique Unique :** Le POC doit porter sur UNE seule zone (ville, arrondissement ou circonscription) pour limiter la volumétrie[cite: 52, 53].
2. **Confidentialité & RGPD :** Application stricte des procédures de sécurité des données[cite: 17].
3. **Approche Industrielle :** Tout code doit être documenté, reproductible et transférable[cite: 92].
4. **Stack Technique :** Python (Pandas/Scikit-Learn), SQL/NoSQL, Visualisation (Matplotlib/PowerBI)[cite: 73, 79].
5. **Économie de Tokens :** Ne réponds jamais par des phrases de politesse ("Bien sûr, je vais faire cela..."). Donne directement le code, le fichier ou la réponse demandée. Si tu dois expliquer, utilise des listes à puces concises.

## Structure du Projet Attendue
- `/data` : Données brutes et nettoyées.
- `/docs` : ADRs, MCD, Rapport de synthèse.
- `/src` : Scripts ETL et Modèles.
- `/notebooks` : Analyses exploratoires.
