# Sources de Données - Electio-Analytics

**Version :** 1.0
**Date :** 2026-02-09
**Périmètre :** Bordeaux - Présidentielles 2017 & 2022 (**1er et 2nd tours obligatoires**)

---

## 1. Élections Présidentielles 2017

### 1er Tour (23 avril 2017)

**Dataset principal :** Résultats par bureaux de vote
- **URL :** [Elections présidentielles 2017 - 1er tour](https://www.data.gouv.fr/datasets/elections-presidentielle-2017-resultats-bureaux-vote-tour-1)
- **Format :** CSV
- **Granularité :** Bureau de vote
- **Téléchargement direct :**
  ```
  https://www.data.gouv.fr/fr/datasets/r/[RESOURCE_ID]
  ```

**Alternative (Communes) :**
- **URL :** [Résultats définitifs du 1er tour par communes](https://www.data.gouv.fr/datasets/election-presidentielle-des-23-avril-et-7-mai-2017-resultats-definitifs-du-1er-tour-par-communes/)
- **Granularité :** Commune

### 2ème Tour (7 mai 2017)

**Dataset principal :** Résultats par bureaux de vote
- **URL :** [Présidentielle 2017 Résultats bureaux vote Tour 2](https://www.data.gouv.fr/datasets/5cddfde49ce2e76d93bdb18b)
- **Format :** CSV
- **Granularité :** Bureau de vote
- **Resource ID :** `b69f0710-1c14-442e-995f-ff280553bd8d`

---

## 2. Élections Présidentielles 2022

### 1er Tour (10 avril 2022)

**Dataset principal :** Résultats officiels Ministère de l'Intérieur
- **URL :** [Election présidentielle 2022 - Résultats du 1er tour](https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-du-1er-tour)
- **Format :** CSV, Excel, JSON
- **Granularité :** Bureau de vote, Commune, Département, Circonscription
- **Téléchargement direct CSV :**
  ```
  https://www.data.gouv.fr/fr/datasets/r/[RESOURCE_ID]
  ```

**Alternative (Par commune et département) :**
- **URL :** [Résultats du 1er tour par commune et département](https://www.data.gouv.fr/datasets/resultats-du-premier-tour-de-lelection-presidentielle-2022-par-commune-et-par-departement)

### 2ème Tour (24 avril 2022)

**Dataset principal :** Résultats officiels Ministère de l'Intérieur
- **URL :** [Election présidentielle 2022 - Résultats du second tour](https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-du-second-tour)
- **Format :** CSV, Excel, JSON
- **Granularité :** Bureau de vote, Commune, Département, Circonscription

---

## 3. Sécurité / Criminalité (SSMSI)

**Dataset :** Bases statistiques de la délinquance enregistrée
- **URL :** [Délinquance enregistrée - Bases communale, départementale et régionale](https://www.data.gouv.fr/datasets/bases-statistiques-communale-departementale-et-regionale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales)
- **Format :** CSV
- **Période :** 2016-2024
- **Granularité :** Commune (pas de détail IRIS public)
- **13 indicateurs :** Cambriolages, Vols de véhicules, Coups et blessures, etc.

**Filtrage requis :** Département 33, Commune 33063 (Bordeaux)

---

## 4. Emploi / Chômage (INSEE)

### Données IRIS (Granularité fine)

**Dataset 1 :** Demandeurs d'emploi en 2022 - Données au niveau IRIS
- **URL :** [Demandeurs d'emploi 2022 - Niveau IRIS](https://www.insee.fr/fr/statistiques/7654804)
- **Format :** Excel (à convertir en CSV)
- **Granularité :** IRIS
- **Champs clés :** Taux de chômage, Population active

**Dataset 2 :** Dossier complet commune de Bordeaux
- **URL :** [Dossier complet - Bordeaux (33063)](https://www.insee.fr/fr/statistiques/2011101?geo=COM-33063)
- **Format :** CSV, Excel
- **Données :** Population active, emploi, chômage, revenus

### Données trimestrielles (France Travail / DARES)

- **URL :** [DARES Open Data](https://dares.travail-emploi.gouv.fr/dossier/open-data)
- **Format :** CSV
- **Mise à jour :** Trimestrielle

---

## 5. Référentiels Géographiques

### Table de correspondance Bureau de Vote → IRIS

**Source :** INSEE - Table d'appartenance géographique des bureaux de vote
- **URL :** [Table passage Bureau de vote → IRIS](https://www.insee.fr/fr/information/2008354)
- **Format :** CSV
- **Usage :** Harmonisation géographique pour jointures

### Contours IRIS (Cartographie)

**Source :** IGN / INSEE
- **URL :** [Contours IRIS 2023](https://geoservices.ign.fr/contoursiris)
- **Format :** Shapefile, GeoJSON
- **Usage :** Visualisation cartographique (PostGIS)

---

## 6. Structure des Fichiers Téléchargés

### ⚠️ IMPORTANT : 4 fichiers CSV obligatoires

Le POC nécessite **les 2 tours pour chaque élection** :

### Élections 2017 (2 fichiers)

```
/data/raw/elections/
    ├── presidentielles_2017_tour1_bureaux_vote.csv  ✅ 1er tour (23 avril 2017)
    ├── presidentielles_2017_tour2_bureaux_vote.csv  ✅ 2nd tour (7 mai 2017)
```

**Champs attendus :**
- `Code département`, `Code commune`, `Code bureau de vote`
- `Nom`, `Prénom` (candidat)
- `Voix`, `% Voix/Exp`, `Inscrits`, `Votants`, `Exprimés`

### Élections 2022 (2 fichiers)

```
/data/raw/elections/
    ├── presidentielles_2022_tour1_bureaux_vote.csv  ✅ 1er tour (10 avril 2022)
    ├── presidentielles_2022_tour2_bureaux_vote.csv  ✅ 2nd tour (24 avril 2022)
```

**Champs attendus :** (similaires à 2017, format standardisé Ministère Intérieur)

**Total à télécharger :** 4 fichiers CSV (2 tours × 2 années)

### Sécurité SSMSI

```
/data/raw/securite/
    └── delinquance_bordeaux_2016_2024.csv
```

**Champs attendus :**
- `Code département`, `Code commune`, `Année`, `Mois`
- 13 colonnes d'indicateurs (cambriolages, vols, etc.)

### Emploi INSEE

```
/data/raw/emploi/
    ├── demandeurs_emploi_iris_2022.csv
    ├── population_active_bordeaux_2017_2024.csv
```

**Champs attendus :**
- `CODE_IRIS`, `Année`, `Trimestre`
- `Taux de chômage`, `Population active`, `Revenus médian`

---

## 7. Méthodes de Téléchargement

### Option A : Téléchargement Manuel

1. Accéder aux URLs listées ci-dessus
2. Cliquer sur "Télécharger" ou "Exporter en CSV"
3. Enregistrer dans `/data/raw/`

### Option B : Script Python Automatisé

**Script :** `src/etl/extract/download_all.py`

```python
import requests
import os

def download_file(url: str, output_path: str):
    """Télécharge un fichier depuis une URL."""
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Téléchargé : {output_path}")

# Élections 2017
download_file(
    "https://www.data.gouv.fr/fr/datasets/r/[RESOURCE_ID_2017_T1]",
    "data/raw/elections/presidentielles_2017_tour1_bureaux_vote.csv"
)

# Élections 2022
download_file(
    "https://www.data.gouv.fr/fr/datasets/r/[RESOURCE_ID_2022_T1]",
    "data/raw/elections/presidentielles_2022_tour1_bureaux_vote.csv"
)
```

### Option C : API data.gouv.fr

**Documentation :** [API data.gouv.fr](https://doc.data.gouv.fr/)

```python
import requests

def get_dataset_resources(dataset_id: str):
    """Récupère les resources d'un dataset via l'API."""
    url = f"https://www.data.gouv.fr/api/1/datasets/{dataset_id}/"
    response = requests.get(url)
    data = response.json()

    for resource in data['resources']:
        print(f"- {resource['title']}: {resource['url']}")

# Exemple : Élections 2022
get_dataset_resources("election-presidentielle-des-10-et-24-avril-2022-resultats-du-1er-tour")
```

---

## 8. Checklist Téléchargement

### ✅ Données Électorales (OBLIGATOIRE - 4 fichiers)
- [ ] **Élections 2017 Tour 1** (23 avril 2017 - CSV bureaux de vote)
- [ ] **Élections 2017 Tour 2** (7 mai 2017 - CSV bureaux de vote)
- [ ] **Élections 2022 Tour 1** (10 avril 2022 - CSV bureaux de vote)
- [ ] **Élections 2022 Tour 2** (24 avril 2022 - CSV bureaux de vote)

### ✅ Données Socio-Économiques (OBLIGATOIRE)
- [ ] Sécurité SSMSI 2017-2024 (CSV commune Bordeaux)
- [ ] Emploi INSEE IRIS 2017-2024 (Excel/CSV)

### 📌 Référentiels Géographiques (OPTIONNEL mais recommandé)
- [ ] Table correspondance Bureau → IRIS (CSV)
- [ ] Contours IRIS Bordeaux (GeoJSON, pour cartographie)

---

## 9. Licences & Conformité

**Toutes les données sont sous Licence Ouverte v2.0 (Etalab)**
- ✅ Utilisation libre (y compris commerciale)
- ✅ Réutilisation autorisée
- ⚠️ Attribution obligatoire : Mentionner "Source : data.gouv.fr, Ministère de l'Intérieur, INSEE"

**Conformité RGPD :**
- ✅ Aucune donnée personnelle (résultats agrégés par bureau/commune)
- ✅ Pas de noms d'électeurs individuels

---

## Sources

- [Elections présidentielles 2017 - 1er tour | data.gouv.fr](https://www.data.gouv.fr/datasets/elections-presidentielle-2017-resultats-bureaux-vote-tour-1)
- [Election présidentielle 2022 - 1er tour | data.gouv.fr](https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-du-1er-tour)
- [Election présidentielle 2022 - Second tour | data.gouv.fr](https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-du-second-tour)
- [Délinquance enregistrée | data.gouv.fr](https://www.data.gouv.fr/datasets/bases-statistiques-communale-departementale-et-regionale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales)
- [INSEE - Dossier Bordeaux](https://www.insee.fr/fr/statistiques/2011101?geo=COM-33063)
- [DARES Open Data](https://dares.travail-emploi.gouv.fr/dossier/open-data)
