# Presentation Soutenance - Electio-Analytics

> Support de presentation (10 slides) - Soutenance orale 20 min
> Groupe RYMS - EPSI M1 - Bloc 3 RNCP35584

---

## SLIDE 1 : Page de titre

```
╔══════════════════════════════════════════════════════╗
║                                                      ║
║           ELECTIO-ANALYTICS                          ║
║                                                      ║
║   Prediction des tendances electorales 2027          ║
║   POC - Presidentielles Gironde                      ║
║                                                      ║
║   ─────────────────────────────────────               ║
║                                                      ║
║   Groupe RYMS                                        ║
║   Samuel Ressiot | Yassine Zouitni                   ║
║   Rudolph Attisso | Marc-Alex Nezout                 ║
║                                                      ║
║   EPSI M1 - Bloc 3 Big Data & BI                     ║
║   Fevrier 2026                                       ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

**Duree :** 2 min

---

## SLIDE 2 : Contexte et problematique

### Le client : Electio-Analytics

- Start-up conseil strategique pour campagnes electorales
- Equipe : 1 expert politique + 1 business developer + 1 assistante
- **Besoin** : prevision des tendances electorales a moyen terme (1-3 ans)

### Problematique

> Comment predire les resultats des Presidentielles 2027
> a partir des donnees historiques et socio-economiques ?

### Perimetre du POC

| | |
|---|---|
| Zone | Gironde (534 communes) |
| Donnees | Presidentielles 2017 & 2022 |
| Prediction | 2027 Tour 1 |
| Indicateurs | Securite (SSMSI) |

**Duree :** 2 min

---

## SLIDE 3 : Sources de donnees

### 3 sources collectees via APIs publiques

| Source | Donnees | Volume |
|--------|---------|--------|
| **geo.api.gouv.fr** | Geographie 534 communes | 200 KB |
| **data.gouv.fr** | Resultats presidentielles T1+T2 | 151 MB |
| **SSMSI** | Criminalite Bordeaux 2016-2024 | 34 MB |

### Donnees en base

- **21 007 lignes** dans PostgreSQL
- **17 tables** (schema normalise 3NF)
- 14 484 resultats candidats + 2 146 lignes participation + 45 indicateurs securite

### Source non retenue

- INSEE (emploi) : API indisponible lors du developpement

**Duree :** 2 min

---

## SLIDE 4 : Architecture technique

### Stack

```
Python 3.12 → Pandas / Scikit-Learn / SQLAlchemy
PostgreSQL 15 → Schema v3.0 (17 tables)
Docker Compose → Infrastructure reproductible
Folium / Matplotlib → Visualisations
```

### Pipeline ETL modulaire

```
  EXTRACT              TRANSFORM             LOAD
  ───────              ─────────             ────
  3 APIs publiques  →  Nettoyage/Normalisation  →  PostgreSQL
  JSON + Parquet       CSV structures             17 tables
  + CSV gzip           8 fichiers                 21 007 lignes
```

### Decisions cles (5 ADRs documentes)

- ADR-001 : PostgreSQL (vs MongoDB) → SQL avance, integrite FK
- ADR-002 : Random Forest (vs XGBoost) → interpretabilite, feature importance
- ADR-003 : ETL modulaire → maintenabilite, testabilite

**Duree :** 2 min

---

## SLIDE 5 : Schema de donnees (MCD v3.0)

### 17 entites - Systeme polymorphe de territoire

```
                    ┌──────────┐
                    │  Region  │
                    └────┬─────┘
                         │
                  ┌──────┴──────┐
                  │ Departement │
                  └──────┬──────┘
                         │
              ┌──────────┴──────────┐
              │       Commune       │──── population
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
   ┌─────┴──────┐  ┌─────┴──────┐  ┌────┴────────┐
   │ Resultat   │  │ Resultat   │  │ Indicateur  │
   │ Candidat   │  │ Particip.  │  │ (securite)  │
   └────────────┘  └────────────┘  └─────────────┘
         │
   ┌─────┴──────┐
   │ Prediction │ ← Output ML
   │   (3745)   │
   └────────────┘
```

- Contraintes : FK, UNIQUE, CHECK (0-100%), indexes composites
- Migrations : 4 versions Alembic

**Duree :** 2 min

---

## SLIDE 6 : Methodologie Machine Learning

### Strategie

- **1 modele Random Forest par candidat** (7 modeles)
- Train : features 2017 → targets 2022
- Predict : features 2022 → prediction 2027
- Validation : 5-Fold Cross-Validation

### 17 Features

| Categorie | Nombre | Source |
|-----------|--------|--------|
| Votes precedents par candidat | 8 | resultat_candidat |
| Participation | 2 | resultat_participation |
| Demographie | 2 | commune |
| Securite | 5 | indicateur |

### Feature la plus importante

> Le % de voix a l'election precedente explique 60-70%
> du resultat suivant → forte inertie electorale

**Duree :** 2 min

---

## SLIDE 7 : Resultats ML

### Performance des modeles (5-Fold CV)

| Candidat | R2 | MAE | Qualite |
|----------|-----|------|---------|
| **LE PEN** | **0.72** | 2.9 pts | **Bon** |
| MELENCHON | 0.51 | 2.5 pts | Acceptable |
| MACRON | 0.41 | 2.9 pts | Acceptable |
| LASSALLE | 0.30 | 1.6 pts | Faible |
| DUPONT-AIGNAN | -0.06 | 0.7 pts | Insuffisant |
| ARTHAUD | -0.09 | 0.3 pts | Insuffisant |
| POUTOU | -0.09 | 0.5 pts | Insuffisant |

- **Objectif R2 > 0.65** : ATTEINT (Le Pen = 0.7245)
- Random Forest surpasse Linear Regression sur tous les candidats majeurs
- Petits candidats (<2%) : signal insuffisant avec 2 elections

> *Inclure ici la figure `comparaison_lr_rf.png`*

**Duree :** 2 min

---

## SLIDE 8 : Predictions 2027

### Classement predit (T1 - moyenne ponderee Gironde)

```
  1. MACRON        ████████████████████████████  ~28%
  2. MELENCHON     █████████████████████████     ~25%
  3. LE PEN        ██████████████████████        ~22%
  4. LASSALLE      ███                           ~3%
  5. DUPONT-AIGNAN ███                           ~3%
  6. POUTOU        █                             ~1%
  7. ARTHAUD       █                             ~1%
```

### Intervalles de confiance (IC 95%)

- Les 3 candidats majeurs ont des IC de ±6-8 points
- Interpretation : resultats indicatifs, pas certains

> *Inclure ici les figures `intervalles_confiance_2027.png` et `evolution_2017_2022_2027.png`*

**Duree :** 2 min

---

## SLIDE 9 : Visualisations et cartes

### Cartes interactives (Folium)

- **Carte candidat en tete** : coloration par commune selon le gagnant predit
- **Carte gradient** : intensite du vote Macron par commune
- **Tooltip interactif** : detail par commune au survol

### Analyse du clivage urbain/rural

- Macron et Melenchon : plus forts en milieu urbain
- Le Pen : plus forte en milieu rural
- Tendance coherente avec la sociologie electorale francaise

### Dashboard de synthese

- Vue multi-panel : podium, R2, intervalles de confiance, evolution, metriques

> *Inclure ici la figure `dashboard_synthese.png`*
> *Demo live de la carte `carte_predictions_2027.html`*

**Duree :** 2 min

---

## SLIDE 10 : Limites et perspectives

### Limites du POC

| Limite | Severite |
|--------|----------|
| 2 elections seulement (pas de serie temporelle) | Haute |
| Indicateurs securite limites a Bordeaux | Haute |
| Candidats 2027 supposes identiques a 2017-2022 | Moyenne |
| Donnees emploi INSEE non integrees | Moyenne |

### Perspectives d'evolution

1. **Court terme** : integrer 10+ elections (municipales, legislatives)
2. **Moyen terme** : ajouter indicateurs emploi, revenus, education (INSEE)
3. **Long terme** : modeles avances (XGBoost, LSTM), pipeline automatise (Airflow)

### Conclusion

> Le POC valide la faisabilite de predictions electorales communales.
> R2 = 0.72 pour Le Pen depasse l'objectif de 0.65.
> La base technique (ETL + BDD + ML) est scalable vers un produit commercial.

**Duree :** 2 min

---

## Notes pour la soutenance

### Repartition du temps (20 min)

| Slides | Duree | Orateur suggere |
|--------|-------|-----------------|
| 1-2 (Contexte) | 4 min | Project Manager |
| 3-5 (Architecture) | 6 min | Data Engineer |
| 6-8 (ML + Resultats) | 6 min | Data Scientist |
| 9-10 (Visu + Conclusion) | 4 min | Data Analyst |

### Questions anticipees du jury (30 min entretien)

1. **Pourquoi Random Forest et pas XGBoost/Neural Network ?**
   → Interpretabilite, feature importance, bon compromis biais/variance pour un POC

2. **Comment ameliorer le R2 pour les petits candidats ?**
   → Plus d'elections historiques, features additionnelles, modeles specifiques

3. **Le modele est-il biaise par la Gironde (zone plutot urbaine/gauche) ?**
   → Oui, le modele capture les specificites locales. Extension multi-departement necessaire

4. **Comment assurez-vous la qualite des donnees ?**
   → Validators ETL, contraintes BDD (FK, CHECK, UNIQUE), code review 7/10

5. **Quid du RGPD ?**
   → Donnees 100% publiques et agregees, aucune donnee personnelle

6. **Pourquoi pas de donnees emploi/chomage ?**
   → API INSEE indisponible lors du developpement, piste d'amelioration prioritaire

7. **Comment gerer les nouveaux candidats en 2027 ?**
   → Le modele ne peut predire que pour les 7 candidats connus. Limite assumee du POC.

8. **Scalabilite : que faudrait-il pour passer a l'echelle nationale ?**
   → Extension du pipeline ETL (deja modulaire), plus de RAM/CPU, schema BDD deja generique
