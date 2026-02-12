# Dictionnaire de Donnees

**Version :** 3.0
**Date :** 2026-02-12
**Auteur :** @tech
**Statut :** Production-Ready

---

## Vue d'Ensemble

Le dictionnaire de donnees documente exhaustivement les **17 tables** du schema v3.0, organise en 6 domaines :

| Domaine | Tables | Description |
|---------|--------|-------------|
| Hierarchie geographique | 6 | region, departement, commune, canton, arrondissement, bureau_vote |
| References electorales | 2 | type_election, election |
| References politiques | 3 | parti, candidat, candidat_parti |
| Resultats electoraux | 3 | election_territoire, resultat_participation, resultat_candidat |
| Indicateurs socio-economiques | 2 | type_indicateur, indicateur |
| Predictions ML | 1 | prediction |

**Systeme polymorphe** : Les tables resultat_participation, resultat_candidat, indicateur et prediction utilisent un couple `(id_territoire, type_territoire)` permettant de lier les donnees a n'importe quel niveau geographique.

---

## 1. Hierarchie Geographique

### Table `region`

**Description :** Regions administratives (niveau le plus haut de la hierarchie geographique).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_region` | VARCHAR(2) | Non | PK | Code region INSEE | `'75'` |
| 2 | `code_insee` | VARCHAR(2) | Non | | Code INSEE region | `'75'` |
| 3 | `nom_region` | VARCHAR(100) | Non | | Nom de la region | `'Nouvelle-Aquitaine'` |
| 4 | `population` | INTEGER | Oui | | Population totale | `6010289` |
| 5 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

---

### Table `departement`

**Description :** Departements, rattaches a une region via FK.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_departement` | VARCHAR(3) | Non | PK | Code departement | `'33'` |
| 2 | `id_region` | VARCHAR(2) | Non | FK -> region, CASCADE | Region parente | `'75'` |
| 3 | `code_insee` | VARCHAR(3) | Non | | Code INSEE departement | `'33'` |
| 4 | `nom_departement` | VARCHAR(100) | Non | | Nom du departement | `'Gironde'` |
| 5 | `population` | INTEGER | Oui | | Population totale | `1623749` |
| 6 | `chef_lieu` | VARCHAR(5) | Oui | | Code INSEE du chef-lieu | `'33063'` |
| 7 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

---

### Table `commune`

**Description :** Communes, rattachees a un departement via FK.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_commune` | VARCHAR(5) | Non | PK | Code INSEE commune | `'33063'` |
| 2 | `id_departement` | VARCHAR(3) | Non | FK -> departement, CASCADE | Departement parent | `'33'` |
| 3 | `code_insee` | VARCHAR(5) | Non | UNIQUE | Code INSEE unique | `'33063'` |
| 4 | `nom_commune` | VARCHAR(100) | Non | | Nom de la commune | `'Bordeaux'` |
| 5 | `population` | INTEGER | Oui | | Population totale | `257068` |
| 6 | `superficie_km2` | DECIMAL(10,2) | Oui | | Superficie en km2 | `49.36` |
| 7 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |
| 8 | `updated_at` | TIMESTAMP | Non | DEFAULT NOW() | Derniere modification | `'2026-02-12 10:00:00'` |

---

### Table `canton`

**Description :** Cantons, rattaches a un departement via FK.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_canton` | VARCHAR(10) | Non | PK | Identifiant canton | `'3301'` |
| 2 | `id_departement` | VARCHAR(3) | Non | FK -> departement, CASCADE | Departement parent | `'33'` |
| 3 | `code_canton` | VARCHAR(10) | Non | | Code du canton | `'3301'` |
| 4 | `numero_canton` | INTEGER | Oui | | Numero du canton | `1` |
| 5 | `nom_canton` | VARCHAR(100) | Non | | Nom du canton | `'Bordeaux-1'` |
| 6 | `population` | INTEGER | Oui | | Population totale | `45000` |
| 7 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

---

### Table `arrondissement`

**Description :** Arrondissements municipaux, rattaches a une commune via FK.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_arrondissement` | VARCHAR(10) | Non | PK | Identifiant arrondissement | `'33063_01'` |
| 2 | `id_commune` | VARCHAR(5) | Non | FK -> commune, CASCADE | Commune parente | `'33063'` |
| 3 | `numero_arrondissement` | INTEGER | Oui | | Numero de l'arrondissement | `1` |
| 4 | `nom_arrondissement` | VARCHAR(100) | Oui | | Nom de l'arrondissement | `'Bordeaux Centre'` |
| 5 | `population` | INTEGER | Oui | | Population totale | `40000` |
| 6 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

---

### Table `bureau_vote`

**Description :** Bureaux de vote, rattaches a une commune et optionnellement a un arrondissement.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_bureau` | VARCHAR(15) | Non | PK | Identifiant unique bureau | `'33063_001'` |
| 2 | `id_commune` | VARCHAR(5) | Non | FK -> commune, CASCADE | Commune de rattachement | `'33063'` |
| 3 | `id_arrondissement` | VARCHAR(10) | Oui | FK -> arrondissement, SET NULL | Arrondissement (si applicable) | `'33063_01'` |
| 4 | `code_bureau` | VARCHAR(10) | Non | | Code du bureau | `'001'` |
| 5 | `nom_bureau` | VARCHAR(200) | Oui | | Nom du bureau | `'Ecole Gambetta'` |
| 6 | `adresse` | TEXT | Oui | | Adresse du bureau | `'12 rue Gambetta, Bordeaux'` |
| 7 | `nombre_inscrits` | INTEGER | Oui | | Nombre d'inscrits | `1200` |
| 8 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |
| 9 | `updated_at` | TIMESTAMP | Non | DEFAULT NOW() | Derniere modification | `'2026-02-12 10:00:00'` |

**Contrainte d'unicite :** `(id_commune, code_bureau)`

---

## 2. References Electorales

### Table `type_election`

**Description :** Types d'elections supportes (presidentielle, legislative, municipale, etc.).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_type_election` | SERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `code_type` | VARCHAR(20) | Non | UNIQUE, CHECK IN | Code du type d'election | `'PRES'` |
| 3 | `nom_type` | VARCHAR(100) | Non | | Nom complet | `'Presidentielle'` |
| 4 | `mode_scrutin` | VARCHAR(50) | Oui | | Mode de scrutin | `'Uninominal majoritaire'` |
| 5 | `niveau_geographique` | VARCHAR(50) | Oui | | Niveau geographique | `'National'` |
| 6 | `description` | TEXT | Oui | | Description detaillee | `'Election du president...'` |
| 7 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

**Check :** `code_type IN ('PRES', 'LEG', 'MUN', 'EUR', 'REG', 'DEP', 'SENAT')`

---

### Table `election`

**Description :** Instances d'elections specifiques (annee, dates, nombre de tours).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_election` | SERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `id_type_election` | INTEGER | Non | FK -> type_election, CASCADE | Type d'election | `1` |
| 3 | `annee` | INTEGER | Non | CHECK [1900-2100] | Annee de l'election | `2022` |
| 4 | `date_tour1` | DATE | Non | | Date du premier tour | `'2022-04-10'` |
| 5 | `date_tour2` | DATE | Oui | CHECK > date_tour1 | Date du second tour | `'2022-04-24'` |
| 6 | `nombre_tours` | INTEGER | Non | CHECK IN (1,2), DEFAULT 1 | Nombre de tours | `2` |
| 7 | `contexte` | TEXT | Oui | | Contexte politique | `'Post-COVID'` |
| 8 | `metadata_` | JSON | Oui | | Metadonnees flexibles | `{"source": "MI"}` |
| 9 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

**Contrainte d'unicite :** `(id_type_election, annee, date_tour1)`

---

## 3. References Politiques

### Table `parti`

**Description :** Partis et nuances politiques avec positionnement ideologique.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_parti` | SERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `code_parti` | VARCHAR(20) | Non | UNIQUE | Code / nuance politique | `'REM'` |
| 3 | `nom_officiel` | VARCHAR(200) | Non | | Nom officiel complet | `'La Republique En Marche'` |
| 4 | `nom_court` | VARCHAR(100) | Oui | | Nom abrege | `'LREM'` |
| 5 | `classification_ideologique` | VARCHAR(50) | Oui | CHECK IN | Classification politique | `'centre'` |
| 6 | `position_economique` | DECIMAL(3,2) | Oui | CHECK [-1.0, 1.0] | Axe economique (-1=gauche, 1=droite) | `0.30` |
| 7 | `position_sociale` | DECIMAL(3,2) | Oui | CHECK [-1.0, 1.0] | Axe social (-1=progressiste, 1=conservateur) | `-0.20` |
| 8 | `couleur_hex` | VARCHAR(7) | Oui | | Couleur officielle | `'#FFD700'` |
| 9 | `logo_url` | VARCHAR(500) | Oui | | URL du logo | |
| 10 | `date_creation` | DATE | Oui | | Date de creation du parti | `'2016-04-06'` |
| 11 | `date_dissolution` | DATE | Oui | CHECK >= date_creation | Date de dissolution | |
| 12 | `successeur_id` | INTEGER | Oui | FK -> parti (self), SET NULL | Parti successeur | |
| 13 | `metadata_` | JSON | Oui | | Metadonnees flexibles | |
| 14 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

**Check classification :** `IN ('extreme_gauche', 'gauche', 'centre_gauche', 'centre', 'centre_droit', 'droite', 'extreme_droite', 'autre')`

---

### Table `candidat`

**Description :** Candidats uniques avec profil.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_candidat` | SERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `nom` | VARCHAR(100) | Non | | Nom de famille | `'MACRON'` |
| 3 | `prenom` | VARCHAR(100) | Non | | Prenom | `'Emmanuel'` |
| 4 | `nom_complet` | VARCHAR(200) | Non | Computed | Nom complet genere | `'Emmanuel MACRON'` |
| 5 | `date_naissance` | DATE | Oui | CHECK <= CURRENT_DATE | Date de naissance | `'1977-12-21'` |
| 6 | `profession` | VARCHAR(200) | Oui | | Profession | `'Haut fonctionnaire'` |
| 7 | `biographie` | TEXT | Oui | | Biographie | |
| 8 | `photo_url` | VARCHAR(500) | Oui | | URL de la photo | |
| 9 | `metadata_` | JSON | Oui | | Metadonnees flexibles | |
| 10 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

**Note :** `nom_complet` est une colonne calculee : `prenom || ' ' || nom`

---

### Table `candidat_parti`

**Description :** Table d'association N:N entre candidats et partis (affiliations avec historique temporel).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_affiliation` | SERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `id_candidat` | INTEGER | Non | FK -> candidat, CASCADE | Candidat affilie | `1` |
| 3 | `id_parti` | INTEGER | Non | FK -> parti, CASCADE | Parti d'affiliation | `1` |
| 4 | `date_debut` | DATE | Non | | Debut de l'affiliation | `'2016-04-06'` |
| 5 | `date_fin` | DATE | Oui | CHECK >= date_debut | Fin de l'affiliation | |
| 6 | `fonction` | VARCHAR(200) | Oui | | Fonction dans le parti | `'President'` |
| 7 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | `'2026-02-12 10:00:00'` |

**Contrainte d'unicite :** `(id_candidat, id_parti, date_debut)`

---

## 4. Resultats Electoraux

### Table `election_territoire`

**Description :** Table pivot liant une election a un territoire. Sert de reference pour les resultats (participation et candidats). Utilise le **systeme polymorphe** `(id_territoire, type_territoire)`.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_election_territoire` | SERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `id_election` | INTEGER | Non | FK -> election, CASCADE | Election concernee | `1` |
| 3 | `id_territoire` | VARCHAR(15) | Non | | ID du territoire (polymorphe) | `'33063'` |
| 4 | `type_territoire` | VARCHAR(20) | Non | CHECK IN | Type de territoire | `'COMMUNE'` |
| 5 | `granularite_source` | VARCHAR(20) | Non | | Granularite des donnees source | `'COMMUNE'` |
| 6 | `date_import` | TIMESTAMP | Non | DEFAULT NOW() | Date d'import des donnees | |
| 7 | `source_fichier` | VARCHAR(500) | Oui | | Fichier source | `'participation_gironde.csv'` |
| 8 | `nombre_resultats_attendus` | INTEGER | Oui | | Nombre de resultats attendus | `10` |
| 9 | `nombre_resultats_charges` | INTEGER | Oui | >= 0 | Nombre de resultats charges | `10` |
| 10 | `statut_validation` | VARCHAR(20) | Non | CHECK IN, DEFAULT 'EN_COURS' | Statut de validation | `'VALIDE'` |
| 11 | `metadata_` | JSON | Oui | | Metadonnees flexibles | |
| 12 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | |
| 13 | `updated_at` | TIMESTAMP | Non | DEFAULT NOW() | Derniere modification | |

**Contrainte d'unicite :** `(id_election, id_territoire, type_territoire)`
**Check type_territoire :** `IN ('BUREAU', 'CANTON', 'COMMUNE', 'ARRONDISSEMENT', 'DEPARTEMENT', 'REGION', 'NATIONAL', 'CIRCONSCRIPTION')`
**Check statut_validation :** `IN ('EN_COURS', 'VALIDE', 'ERREUR', 'INCOMPLET')`

---

### Table `resultat_participation`

**Description :** Donnees de participation par election, territoire et tour. Inclut des colonnes calculees pour les pourcentages.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_resultat_part` | BIGSERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `id_election` | INTEGER | Non | FK composite | Election concernee | `1` |
| 3 | `id_territoire` | VARCHAR(15) | Non | FK composite | ID territoire (polymorphe) | `'33063'` |
| 4 | `type_territoire` | VARCHAR(20) | Non | FK composite, CHECK IN | Type de territoire | `'COMMUNE'` |
| 5 | `tour` | INTEGER | Non | CHECK IN (1,2) | Tour de l'election | `1` |
| 6 | `nombre_inscrits` | INTEGER | Non | >= 0 | Nombre d'inscrits | `130000` |
| 7 | `nombre_abstentions` | INTEGER | Non | >= 0 | Nombre d'abstentions | `30000` |
| 8 | `nombre_votants` | INTEGER | Non | >= 0 | Nombre de votants | `100000` |
| 9 | `nombre_blancs_nuls` | INTEGER | Non | >= 0 | Blancs + nuls | `2000` |
| 10 | `nombre_exprimes` | INTEGER | Non | >= 0 | Suffrages exprimes | `98000` |
| 11 | `pourcentage_abstentions` | DECIMAL(5,2) | Oui | Computed | % abstentions / inscrits | `23.08` |
| 12 | `pourcentage_votants` | DECIMAL(5,2) | Oui | Computed | % votants / inscrits | `76.92` |
| 13 | `pourcentage_blancs_nuls_inscrits` | DECIMAL(5,2) | Oui | Computed | % blancs-nuls / inscrits | `1.54` |
| 14 | `pourcentage_blancs_nuls_votants` | DECIMAL(5,2) | Oui | Computed | % blancs-nuls / votants | `2.00` |
| 15 | `pourcentage_exprimes_inscrits` | DECIMAL(5,2) | Oui | Computed | % exprimes / inscrits | `75.38` |
| 16 | `pourcentage_exprimes_votants` | DECIMAL(5,2) | Oui | Computed | % exprimes / votants | `98.00` |
| 17 | `metadata_` | JSON | Oui | | Metadonnees flexibles | |
| 18 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | |

**FK composite :** `(id_election, id_territoire, type_territoire) -> election_territoire` (CASCADE)
**Contrainte d'unicite :** `(id_election, id_territoire, type_territoire, tour)`
**Check coherence :** `nombre_votants + nombre_abstentions = nombre_inscrits` ET `nombre_exprimes + nombre_blancs_nuls = nombre_votants`

---

### Table `resultat_candidat`

**Description :** Voix obtenues par chaque candidat, par election, territoire et tour.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_resultat_cand` | BIGSERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `id_election` | INTEGER | Non | FK composite | Election concernee | `1` |
| 3 | `id_candidat` | INTEGER | Non | FK -> candidat, CASCADE | Candidat concerne | `1` |
| 4 | `id_territoire` | VARCHAR(15) | Non | FK composite | ID territoire (polymorphe) | `'33063'` |
| 5 | `type_territoire` | VARCHAR(20) | Non | FK composite, CHECK IN | Type de territoire | `'COMMUNE'` |
| 6 | `tour` | INTEGER | Non | CHECK IN (1,2) | Tour de l'election | `1` |
| 7 | `nombre_voix` | INTEGER | Non | >= 0 | Nombre de voix obtenues | `45000` |
| 8 | `pourcentage_voix_inscrits` | DECIMAL(5,2) | Oui | CHECK [0, 100] | % voix / inscrits | `34.62` |
| 9 | `pourcentage_voix_exprimes` | DECIMAL(5,2) | Oui | CHECK [0, 100] | % voix / exprimes | `45.92` |
| 10 | `metadata_` | JSON | Oui | | Metadonnees flexibles | |
| 11 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | |

**FK composite :** `(id_election, id_territoire, type_territoire) -> election_territoire` (CASCADE)
**Contrainte d'unicite :** `(id_election, id_candidat, id_territoire, type_territoire, tour)`

---

## 5. Indicateurs Socio-Economiques

### Table `type_indicateur`

**Description :** Catalogue des types d'indicateurs socio-economiques (securite, emploi, demographie, etc.). Pattern EAV.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_type` | SERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `code_type` | VARCHAR(50) | Non | UNIQUE | Code identifiant unique | `'CRIMINALITE_TOTALE'` |
| 3 | `categorie` | VARCHAR(50) | Non | | Categorie macro | `'SECURITE'` |
| 4 | `nom_affichage` | VARCHAR(100) | Non | | Libelle pour l'interface | `'Criminalite totale'` |
| 5 | `description` | TEXT | Oui | | Description detaillee | `'Total des faits de delinquance'` |
| 6 | `unite_mesure` | VARCHAR(50) | Oui | | Unite de mesure | `'nombre'` |
| 7 | `source_officielle` | VARCHAR(100) | Oui | | Organisme source | `'SSMSI'` |
| 8 | `frequence` | VARCHAR(20) | Oui | | Periodicite | `'ANNUEL'` |
| 9 | `date_debut_disponibilite` | DATE | Oui | | Premiere date disponible | `'2016-01-01'` |
| 10 | `actif` | BOOLEAN | Non | DEFAULT TRUE | Indicateur actif (soft delete) | `TRUE` |
| 11 | `schema_metadata` | JSONB | Oui | | Schema JSON de validation | `{"type": "object"}` |
| 12 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | |

### Types pre-charges (POC Bordeaux)

| id_type | code_type | categorie | nom_affichage | source |
|---------|-----------|-----------|---------------|--------|
| 1 | `CRIMINALITE_TOTALE` | SECURITE | Criminalite totale | SSMSI |
| 2 | `VOLS_SANS_VIOLENCE` | SECURITE | Vols sans violence | SSMSI |
| 3 | `VOLS_AVEC_VIOLENCE` | SECURITE | Vols avec violence | SSMSI |
| 4 | `ATTEINTES_AUX_BIENS` | SECURITE | Atteintes aux biens | SSMSI |
| 5 | `ATTEINTES_AUX_PERSONNES` | SECURITE | Atteintes aux personnes | SSMSI |

---

### Table `indicateur`

**Description :** Table generique stockant TOUS les indicateurs socio-economiques. Pattern EAV polymorphe permettant l'ajout de nouvelles sources sans modification de schema.

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_indicateur` | BIGSERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `id_territoire` | VARCHAR(15) | Non | | ID territoire (polymorphe) | `'33063'` |
| 3 | `type_territoire` | VARCHAR(20) | Non | CHECK IN | Type de territoire | `'COMMUNE'` |
| 4 | `id_type` | INTEGER | Non | FK -> type_indicateur, RESTRICT | Type d'indicateur | `1` |
| 5 | `annee` | INTEGER | Non | CHECK [2000, 2100] | Annee de reference | `2022` |
| 6 | `periode` | VARCHAR(20) | Oui | | Periode infra-annuelle | `'T1'`, `NULL` |
| 7 | `valeur_numerique` | DECIMAL(15,4) | Oui | | Valeur principale | `23971.0` |
| 8 | `valeur_texte` | TEXT | Oui | | Valeur qualitative | |
| 9 | `metadata_` | JSONB | Oui | GIN index | Metadonnees flexibles | `{"taux_pour_1000_hab": 2.0}` |
| 10 | `source_detail` | VARCHAR(200) | Oui | | Source precise | `'SSMSI_2024'` |
| 11 | `fiabilite` | VARCHAR(20) | Non | CHECK IN, DEFAULT 'CONFIRME' | Niveau de fiabilite | `'CONFIRME'` |
| 12 | `created_at` | TIMESTAMP | Non | DEFAULT NOW() | Date de creation | |

**Contrainte d'unicite :** `(id_territoire, type_territoire, id_type, annee, periode)`
**Check fiabilite :** `IN ('CONFIRME', 'ESTIME', 'PROVISOIRE', 'REVISION')`
**Check type_territoire :** `IN ('BUREAU', 'CANTON', 'COMMUNE', 'ARRONDISSEMENT', 'DEPARTEMENT', 'REGION', 'NATIONAL')`

### Exemples de donnees (POC Bordeaux)

| id_indicateur | id_territoire | type_territoire | id_type | annee | valeur_numerique | fiabilite |
|---------------|---------------|-----------------|---------|-------|------------------|-----------|
| 1 | `33063` | COMMUNE | 1 | 2022 | 23971.0 | CONFIRME |
| 2 | `33063` | COMMUNE | 2 | 2022 | 16181.0 | CONFIRME |
| 3 | `33063` | COMMUNE | 3 | 2022 | 1079.0 | CONFIRME |

---

## 6. Predictions ML

### Table `prediction`

**Description :** Predictions electorales 2027 generees par les modeles Machine Learning. Tracabilite complete (modele, version, metriques).

| # | Colonne | Type | Null | Contrainte | Description | Exemple |
|---|---------|------|------|------------|-------------|---------|
| 1 | `id_prediction` | BIGSERIAL | Non | PK | Identifiant auto-incremente | `1` |
| 2 | `id_territoire` | VARCHAR(15) | Non | | ID territoire (polymorphe) | `'33063'` |
| 3 | `type_territoire` | VARCHAR(20) | Non | CHECK IN | Type de territoire | `'COMMUNE'` |
| 4 | `candidat` | VARCHAR(100) | Non | | Nom du candidat predit | `'Emmanuel MACRON'` |
| 5 | `parti` | VARCHAR(50) | Oui | | Parti politique | `'RE'` |
| 6 | `annee_prediction` | INTEGER | Oui | CHECK [2025, 2050], DEFAULT 2027 | Annee de l'election predite | `2027` |
| 7 | `tour` | INTEGER | Non | CHECK IN (1, 2) | Tour predit | `1` |
| 8 | `pourcentage_predit` | DECIMAL(5,2) | Non | CHECK [0, 100] | % de voix predit | `32.15` |
| 9 | `intervalle_confiance_inf` | DECIMAL(5,2) | Oui | CHECK [0, 100] | Borne inferieure IC 95% | `29.80` |
| 10 | `intervalle_confiance_sup` | DECIMAL(5,2) | Oui | CHECK [0, 100] | Borne superieure IC 95% | `34.50` |
| 11 | `modele_utilise` | VARCHAR(50) | Non | | Algorithme ML | `'RandomForest'` |
| 12 | `version_modele` | VARCHAR(20) | Oui | | Version du modele | `'v1.0.0'` |
| 13 | `metriques_modele` | JSONB | Oui | | Metriques de performance | `{"r2": 0.72, "mae": 2.3}` |
| 14 | `features_utilisees` | JSONB | Oui | | Features ML utilisees | `["criminalite_totale", ...]` |
| 15 | `date_generation` | TIMESTAMP | Non | DEFAULT NOW() | Date de generation | |

**Contrainte d'unicite :** `(id_territoire, type_territoire, candidat, tour, annee_prediction, version_modele)`

---

## Types de Donnees PostgreSQL

### Types Scalaires

| Type SQL | Description | Exemple |
|----------|-------------|---------|
| `VARCHAR(n)` | Chaine de caracteres variable (max n) | `'Bordeaux'` |
| `INTEGER` | Entier 32 bits | `252040` |
| `BIGINT` / `BIGSERIAL` | Entier 64 bits (auto-incremente) | `1, 2, 3...` |
| `SERIAL` | Auto-incremente INTEGER | `1, 2, 3...` |
| `DECIMAL(p,s)` | Nombre decimal (precision p, echelle s) | `28.45` |
| `NUMERIC(p,s)` | Alias de DECIMAL | `0.30` |
| `BOOLEAN` | Booleen | `TRUE`, `FALSE` |
| `DATE` | Date | `'2022-04-10'` |
| `TIMESTAMP` | Date + heure | `'2026-02-12 10:00:00'` |
| `TEXT` | Texte sans limite | Description longue |

### Types Avances

| Type SQL | Description | Exemple |
|----------|-------------|---------|
| `JSON` | JSON standard | `{"key": "value"}` |
| `JSONB` | JSON binaire indexable (GIN) | `{"key": "value"}` |

---

## Conventions de Nommage

| Element | Convention | Exemples |
|---------|-----------|----------|
| Tables | `snake_case` | `resultat_candidat`, `type_indicateur` |
| Colonnes | `snake_case` | `id_territoire`, `pourcentage_voix_exprimes` |
| Cles primaires | `id_<entite>` | `id_election`, `id_candidat` |
| Cles etrangeres | `id_<table_parent>` | `id_region`, `id_type_election` |
| Contraintes PK | `pk_<table>` | `pk_commune` |
| Contraintes FK | `fk_<enfant>_<parent>` | `fk_commune_departement` |
| Contraintes UK | `uk_<table>_<colonnes>` | `uk_election_type_annee` |
| Contraintes CK | `ck_<table>_<colonne>` | `ck_election_annee` |

---

## Volumetrie (POC Bordeaux - Resultats reels)

| Table | Lignes | Description |
|-------|--------|-------------|
| `region` | 1 | Nouvelle-Aquitaine |
| `departement` | 1 | Gironde |
| `commune` | ~535 | Communes de Gironde |
| `canton` | 0 | Non charge dans le POC |
| `arrondissement` | 0 | Non charge dans le POC |
| `bureau_vote` | 0 | Non charge dans le POC |
| `type_election` | 1 | Presidentielle |
| `election` | 2 | 2017, 2022 |
| `candidat` | ~25 | Candidats uniques |
| `parti` | ~15 | Nuances politiques |
| `candidat_parti` | ~25 | Affiliations |
| `election_territoire` | ~2 140 | Elections x communes x tours |
| `resultat_participation` | ~2 140 | Participation par commune/tour |
| `resultat_candidat` | ~14 484 | Voix par candidat/commune/tour |
| `type_indicateur` | 5 | Categories securite |
| `indicateur` | ~45 | Bordeaux 2016-2024 |
| `prediction` | 0 | En attente Phase 4 (ML) |
| **TOTAL** | **~17 262** | |

---

**Prochaine etape :** Consulter les [Regles de Gestion](04-regles-gestion.md) pour comprendre les regles metier implementees.
