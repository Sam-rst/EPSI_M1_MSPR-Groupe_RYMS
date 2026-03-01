# B2 - Entrepôt de Données & Référentiels

> **Compétence C6 :** Définir les données de référence à partir des données utilisées pour créer un référentiel afin d'assurer la mise à disposition de données cohérentes.
> **Compétence C7 :** Créer un entrepôt unique à partir du référentiel pour centraliser les informations stratégiques et répondre rapidement aux besoins métiers.

---

## 1. Entrepôt unique : PostgreSQL 15

| Paramètre | Valeur |
|-----------|--------|
| SGBD | PostgreSQL 15 + PostGIS |
| Schéma | v3.0 normalisé 3NF |
| Tables | 17 |
| Lignes totales | ~21 000 |
| Infrastructure | Docker Compose |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic (4 versions) |

## 2. MLD (v3.0)

## Diagramme Relationnel

```mermaid
erDiagram
    region ||--o{ departement : "contient"
    departement ||--o{ canton : "contient"
    departement ||--o{ commune : "contient"
    commune ||--o{ arrondissement : "contient"
    commune ||--o{ bureau_vote : "contient"
    arrondissement ||--o{ bureau_vote : "optionnel"

    type_election ||--o{ election : "catégorise"
    election ||--o{ election_territoire : "déclare"
    election_territoire ||--o{ resultat_participation : "mesure"
    election_territoire ||--o{ resultat_candidat : "mesure"

    candidat ||--o{ candidat_parti : "affilié"
    parti ||--o{ candidat_parti : "accueille"
    candidat ||--o{ resultat_candidat : "obtient"
    parti ||--o| parti : "succède"

    type_indicateur ||--o{ indicateur : "catégorise"

    region {
        varchar id_region PK
        varchar nom_region
        integer population
    }

    departement {
        varchar id_departement PK
        varchar id_region FK
        varchar nom_departement
        integer population
    }

    commune {
        varchar id_commune PK
        varchar id_departement FK
        varchar code_insee UK
        varchar nom_commune
        integer population
    }

    canton {
        varchar id_canton PK
        varchar id_departement FK
        varchar nom_canton
    }

    arrondissement {
        varchar id_arrondissement PK
        varchar id_commune FK
        varchar nom_arrondissement
    }

    bureau_vote {
        varchar id_bureau PK
        varchar id_commune FK
        varchar id_arrondissement FK
        varchar code_bureau
    }

    type_election {
        serial id_type_election PK
        varchar code_type UK
        varchar nom_type
    }

    election {
        serial id_election PK
        integer id_type_election FK
        integer annee
        date date_tour1
        date date_tour2
    }

    election_territoire {
        serial id_election_territoire PK
        integer id_election FK
        varchar id_territoire
        varchar type_territoire
    }

    resultat_participation {
        bigserial id_resultat_part PK
        integer id_election FK
        varchar id_territoire
        varchar type_territoire
        integer tour
        integer nombre_inscrits
        integer nombre_votants
        integer nombre_exprimes
    }

    resultat_candidat {
        bigserial id_resultat_cand PK
        integer id_election FK
        integer id_candidat FK
        varchar id_territoire
        varchar type_territoire
        integer tour
        integer nombre_voix
    }

    candidat {
        serial id_candidat PK
        varchar nom
        varchar prenom
        varchar nom_complet
    }

    parti {
        serial id_parti PK
        varchar code_parti UK
        varchar nom_officiel
        varchar classification_ideologique
    }

    candidat_parti {
        serial id_affiliation PK
        integer id_candidat FK
        integer id_parti FK
        date date_debut
    }

    type_indicateur {
        serial id_type PK
        varchar code_type UK
        varchar categorie
        varchar nom_affichage
    }

    indicateur {
        bigserial id_indicateur PK
        varchar id_territoire
        varchar type_territoire
        integer id_type FK
        integer annee
        decimal valeur_numerique
    }

    prediction {
        bigserial id_prediction PK
        varchar id_territoire
        varchar type_territoire
        varchar candidat
        integer tour
        decimal pourcentage_predit
        varchar modele_utilise
    }
```

## 3. Référentiels définis

### Référentiel géographique

| Table | Clé | Exemples | Lignes |
|-------|-----|----------|--------|
| `region` | id_region | Nouvelle-Aquitaine | 1 |
| `departement` | id_departement | Gironde (33) | 1 |
| `commune` | id_commune | Bordeaux (33063), Mérignac (33281)... | 534 |

### Référentiel candidats & partis

| Table | Clé | Exemples | Lignes |
|-------|-----|----------|--------|
| `candidat` | id_candidat | Macron, Le Pen, Mélenchon... | 16 |
| `parti` | id_parti | RE, RN, LFI... | 15 |
| `candidat_parti` | (id_candidat, id_parti) | Association candidat-parti | 25 |

### Référentiel élections

| Table | Clé | Exemples | Lignes |
|-------|-----|----------|--------|
| `type_election` | id_type | Présidentielle | 1 |
| `election` | id_election | 2017, 2022 | 2 |

### Référentiel indicateurs

| Table | Clé | Exemples | Lignes |
|-------|-----|----------|--------|
| `type_indicateur` | id_type | Criminalité totale, Vols, Atteintes... | 5 |

## 4. Contraintes d'intégrité

| Type | Nombre | Exemple |
|------|--------|---------|
| Clés primaires | 17 | `commune.id_commune` |
| Clés étrangères | 12 | `commune.id_departement → departement` |
| UNIQUE | 8 | `(id_territoire, candidat, tour, annee, version)` |
| CHECK | 10 | `pourcentage BETWEEN 0 AND 100` |
| NOT NULL | ~50 | Colonnes obligatoires |

## 5. Historique des versions

| Version | Date | Changement |
|---------|------|-----------|
| v1.0 | 2026-02-09 | Schéma initial (8 tables) |
| v2.0 | 2026-02-10 | Séparation participation/résultats |
| v3.0 | 2026-02-12 | Système polymorphe, 17 tables, table prediction |

## 6. Dictionnaire de données

Extrait pour les tables clés :

| Table.Colonne | Type | Description |
|---------------|------|-------------|
| `commune.id_commune` | VARCHAR(5) | Code INSEE (ex: 33063) |
| `commune.population` | INTEGER | Population municipale |
| `resultat_candidat.pourcentage_voix_exprimes` | NUMERIC(5,2) | % voix (0-100) |
| `prediction.pourcentage_predit` | NUMERIC(5,2) | % prédit ML (0-100) |
| `prediction.intervalle_confiance_inf` | NUMERIC(5,2) | Borne inf IC 95% |
| `prediction.metriques_modele` | JSONB | {r2, mae, rmse, feature_importance} |

**Fichiers de référence :**
- Modèles ORM : `src/database/models/`
- MCD : `docs/02-architecture/database/01-mcd.md`
- MLD : `docs/02-architecture/database/02-mld.md`
- Dictionnaire complet : `docs/02-architecture/database/03-dictionnaire-donnees.md`
- Règles de gestion : `docs/02-architecture/database/04-regles-gestion.md`
- Contraintes : `docs/02-architecture/database/05-contraintes-integrite.md`
