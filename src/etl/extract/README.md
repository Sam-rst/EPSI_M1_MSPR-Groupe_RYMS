# Module Extract - Electio-Analytics

Module d'extraction des donnees brutes depuis les APIs externes.

## Sources

| Source | API | Format |
|--------|-----|--------|
| **Geographie** | geo.api.gouv.fr | JSON |
| **Elections** | data.gouv.fr (API tabulaire + Parquet) | JSON + Parquet |
| **Securite** | data.gouv.fr (SSMSI) | CSV gzip |

## Structure

```
extract/
├── config/settings.py        # URLs API, chemins, constantes
├── core/
│   ├── geographie.py         # geo.api.gouv.fr (regions, departements, communes)
│   ├── elections.py          # API tabulaire + Parquet candidats
│   └── securite.py           # SSMSI CSV gzip
├── utils/download.py         # download_file() avec barre de progression
└── main.py                   # Orchestrateur
```

## Utilisation

```bash
python -m src.etl.extract.main
```

## Documentation complete

Voir [src/etl/README.md](../README.md) pour la documentation complete du pipeline ETL.
