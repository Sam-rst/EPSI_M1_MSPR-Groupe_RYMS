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

```mermaid
erDiagram
    REGION ||--o{ DEPARTEMENT : contient
    DEPARTEMENT ||--o{ COMMUNE : contient
    COMMUNE ||--o{ RESULTAT_PARTICIPATION : "id_territoire"
    COMMUNE ||--o{ RESULTAT_CANDIDAT : "id_territoire"
    COMMUNE ||--o{ INDICATEUR : "id_territoire"
    COMMUNE ||--o{ PREDICTION : "id_territoire"

    ELECTION ||--o{ RESULTAT_PARTICIPATION : concerne
    ELECTION ||--o{ RESULTAT_CANDIDAT : concerne
    CANDIDAT ||--o{ RESULTAT_CANDIDAT : obtient
    CANDIDAT ||--o{ CANDIDAT_PARTI : appartient
    PARTI ||--o{ CANDIDAT_PARTI : regroupe
    TYPE_INDICATEUR ||--o{ INDICATEUR : categorise
    TYPE_ELECTION ||--o{ ELECTION : type

    COMMUNE {
        varchar id_commune PK
        varchar nom_commune
        int population
    }
    CANDIDAT {
        int id_candidat PK
        varchar nom
        varchar prenom
    }
    PREDICTION {
        bigint id_prediction PK
        numeric pourcentage_predit
        numeric ic_inf
        numeric ic_sup
        jsonb metriques_modele
    }
    RESULTAT_CANDIDAT {
        bigint id PK
        int nombre_voix
        numeric pourcentage_voix
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
