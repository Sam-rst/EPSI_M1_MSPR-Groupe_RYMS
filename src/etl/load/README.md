# Module Load - Electio-Analytics

Module de chargement des CSV normalises dans PostgreSQL (schema v3.0, 17 tables).

## Ordre de chargement (respect FK)

1. **Geographie** : Region -> Departement -> Commune
2. **TypeIndicateur** : 5 categories securite
3. **Candidats & Elections** : TypeElection, Election, Candidat, Parti, CandidatParti
4. **Resultats** : ElectionTerritoire, ResultatParticipation, ResultatCandidat
5. **Indicateurs** : Securite Bordeaux 2016-2024

## Structure

```
load/
├── config/settings.py           # Chemins CSV, configs batch
├── core/
│   ├── geographie.py            # Region, Departement, Commune
│   ├── candidats.py             # TypeElection, Election, Candidat, Parti
│   ├── elections.py             # ElectionTerritoire, ResultatParticipation, ResultatCandidat
│   ├── indicateurs.py           # Indicateur (batch 1000 rows)
│   └── type_indicateur.py       # TypeIndicateur
├── utils/validators.py          # Validation CSV
└── main.py                      # Orchestrateur
```

## Patterns

- **Check-before-insert** : Verifie existence avant creation
- **Batch loading** : Insert par lots de 1000 lignes
- **Cache pre-load** : References en memoire (N+1 elimination)
- **Transaction safety** : IntegrityError + session.rollback()

## Utilisation

```bash
python -m src.etl.load.main
```

## Documentation complete

Voir [src/etl/README.md](../README.md) pour la documentation complete du pipeline ETL.
