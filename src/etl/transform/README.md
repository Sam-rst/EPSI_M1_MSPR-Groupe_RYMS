# Module Transform - Electio-Analytics

Module de transformation des donnees brutes en CSV normalises.

## Transformations

| Source | Entree | Sortie |
|--------|--------|--------|
| **Geographie** | JSON API | regions.csv, departements.csv, communes.csv |
| **Elections** | JSON + Parquet | participation_gironde.csv, candidats_gironde.csv, referentiels |
| **Securite** | CSV SSMSI | delinquance_bordeaux.csv (~45 lignes) |

## Structure

```
transform/
├── config/settings.py        # Chemins, constantes, mappings
├── core/
│   ├── geographie.py         # JSON API -> CSV referentiels geo
│   ├── elections.py          # JSON + Parquet -> CSV (vectorise, Arrow/pd.NA)
│   └── securite.py           # CSV SSMSI -> indicateurs Bordeaux
├── utils/parsing.py          # parse_french_number()
└── main.py                   # Orchestrateur
```

## Utilisation

```bash
python -m src.etl.transform.main
```

## Documentation complete

Voir [src/etl/README.md](../README.md) pour la documentation complete du pipeline ETL.
