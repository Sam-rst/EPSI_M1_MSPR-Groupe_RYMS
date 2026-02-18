# B2 - Entrepot de Donnees & Referentiels

> **Competence C6 :** Definir les donnees de reference a partir des donnees utilisees pour creer un referentiel afin d'assurer la mise a disposition de donnees coherentes.
> **Competence C7 :** Creer un entrepot unique a partir du referentiel pour centraliser les informations strategiques et repondre rapidement aux besoins metiers.

---

## 1. Entrepot unique : PostgreSQL 15

| Parametre | Valeur |
|-----------|--------|
| SGBD | PostgreSQL 15 + PostGIS |
| Schema | v3.0 normalise 3NF |
| Tables | 17 |
| Lignes totales | ~21 000 |
| Infrastructure | Docker Compose |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic (4 versions) |

## 2. MCD simplifie (v3.0)

## Diagramme Relationnel

```mermaid
erDiagram
    region ||--o{ departement : "contient"
    departement ||--o{ canton : "contient"
    departement ||--o{ commune : "contient"
    commune ||--o{ arrondissement : "contient"
    commune ||--o{ bureau_vote : "contient"
    arrondissement ||--o{ bureau_vote : "optionnel"

    type_election ||--o{ election : "categorise"
    election ||--o{ election_territoire : "declare"
    election_territoire ||--o{ resultat_participation : "mesure"
    election_territoire ||--o{ resultat_candidat : "mesure"

    candidat ||--o{ candidat_parti : "affilie"
    parti ||--o{ candidat_parti : "accueille"
    candidat ||--o{ resultat_candidat : "obtient"
    parti ||--o| parti : "succede"

    type_indicateur ||--o{ indicateur : "categorise"

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

## 3. Referentiels definis

### Referentiel geographique

| Table | Cle | Exemples | Lignes |
|-------|-----|----------|--------|
| `region` | id_region | Nouvelle-Aquitaine | 1 |
| `departement` | id_departement | Gironde (33) | 1 |
| `commune` | id_commune | Bordeaux (33063), Merignac (33281)... | 534 |

### Referentiel candidats & partis

| Table | Cle | Exemples | Lignes |
|-------|-----|----------|--------|
| `candidat` | id_candidat | Macron, Le Pen, Melenchon... | 16 |
| `parti` | id_parti | RE, RN, LFI... | 15 |
| `candidat_parti` | (id_candidat, id_parti) | Association candidat-parti | 25 |

### Referentiel elections

| Table | Cle | Exemples | Lignes |
|-------|-----|----------|--------|
| `type_election` | id_type | Presidentielle | 1 |
| `election` | id_election | 2017, 2022 | 2 |

### Referentiel indicateurs

| Table | Cle | Exemples | Lignes |
|-------|-----|----------|--------|
| `type_indicateur` | id_type | Criminalite totale, Vols, Atteintes... | 5 |

## 3. Contraintes d'integrite

| Type | Nombre | Exemple |
|------|--------|---------|
| Cles primaires | 17 | `commune.id_commune` |
| Cles etrangeres | 12 | `commune.id_departement → departement` |
| UNIQUE | 8 | `(id_territoire, candidat, tour, annee, version)` |
| CHECK | 10 | `pourcentage BETWEEN 0 AND 100` |
| NOT NULL | ~50 | Colonnes obligatoires |

## 4. Historique des versions

| Version | Date | Changement |
|---------|------|-----------|
| v1.0 | 2026-02-09 | Schema initial (8 tables) |
| v2.0 | 2026-02-10 | Separation participation/resultats |
| v3.0 | 2026-02-12 | Systeme polymorphe, 17 tables, table prediction |

## 5. Dictionnaire de donnees

Extrait pour les tables cles :

| Table.Colonne | Type | Description |
|---------------|------|-------------|
| `commune.id_commune` | VARCHAR(5) | Code INSEE (ex: 33063) |
| `commune.population` | INTEGER | Population municipale |
| `resultat_candidat.pourcentage_voix_exprimes` | NUMERIC(5,2) | % voix (0-100) |
| `prediction.pourcentage_predit` | NUMERIC(5,2) | % predit ML (0-100) |
| `prediction.intervalle_confiance_inf` | NUMERIC(5,2) | Borne inf IC 95% |
| `prediction.metriques_modele` | JSONB | {r2, mae, rmse, feature_importance} |

**Fichiers de reference :**
- Modeles ORM : `src/database/models/`
- MCD : `docs/02-architecture/database/01-mcd.md`
- MLD : `docs/02-architecture/database/02-mld.md`
- Dictionnaire complet : `docs/02-architecture/database/03-dictionnaire-donnees.md`
- Regles de gestion : `docs/02-architecture/database/04-regles-gestion.md`
- Contraintes : `docs/02-architecture/database/05-contraintes-integrite.md`
