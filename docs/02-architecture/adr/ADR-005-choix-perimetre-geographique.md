# ADR-005 : Choix du Périmètre Géographique

**Status :** ✅ ACCEPTÉ
**Date :** 2026-02-09
**Décideurs :** Project Manager (@pm), Tech Lead (@tech)
**Contexte :** POC Electio-Analytics - Définition de la zone d'étude

---

## Contexte

Le cahier des charges MSPR impose un périmètre géographique unique (une seule ville, arrondissement ou circonscription) afin de limiter la volumétrie et concentrer l'effort sur la preuve de concept.

**Contraintes identifiées :**
- POC limité à 25h de développement
- Nécessité de croiser données électorales + indicateurs socio-économiques
- Sources open data obligatoires (Ministère de l'Intérieur, INSEE, SSMSI)
- Volume de données maîtrisable pour un POC

**Zones candidates évaluées :**
1. **Bordeaux** (commune 33063 - Gironde)
2. **Paris** (75 - Île-de-France)
3. **Lyon** (69123 - Rhône)
4. **Marseille** (13055 - Bouches-du-Rhône)

---

## Décision

**→ Bordeaux (Gironde - 33), commune INSEE 33063**

**Étendu à :** Département Gironde (535 communes) pour la dimension électorale, avec indicateurs socio-économiques centrés sur Bordeaux.

---

## Justification

### 1. Proximité avec l'École EPSI

| Critère | Bordeaux | Paris | Lyon | Marseille |
|---------|----------|-------|------|-----------|
| **Campus EPSI** | ✅ Oui | ✅ Oui | ✅ Oui | ✅ Oui |
| **Connaissance terrain** | ✅ Forte | ❌ Partielle | ❌ Partielle | ❌ Partielle |
| **Validation résultats** | ✅ Intuitive | ❌ Complexe | ❌ Complexe | ❌ Complexe |

**→** L'équipe projet est basée à Bordeaux. La connaissance du terrain local permet de valider intuitivement la cohérence des résultats (ex : quartiers, tendances politiques connues).

---

### 2. Volumétrie Adaptée au POC

| Métrique | Bordeaux | Paris | Lyon | Marseille |
|----------|----------|-------|------|-----------|
| **Population** | ~260 000 | ~2 100 000 | ~520 000 | ~870 000 |
| **Bureaux de vote** | ~80 | ~900 | ~500 | ~450 |
| **IRIS** | ~50 | ~990 | ~500 | ~500 |
| **Communes département** | 535 | 130+ | 290 | 120 |
| **Lignes estimées BDD** | ~26 650 | ~250 000+ | ~130 000+ | ~120 000+ |

**→** Bordeaux offre un volume suffisant pour entraîner un modèle ML (~26 650 lignes) sans exploser le temps de développement. Paris aurait multiplié la volumétrie par 10, incompatible avec 25h.

---

### 3. Disponibilité des Données Open Data

| Source | Bordeaux | Couverture |
|--------|----------|------------|
| **Élections (Ministère Intérieur)** | ✅ Complète | Résultats par bureau de vote 2017 & 2022 |
| **INSEE - Dossier complet** | ✅ Disponible | [Dossier Bordeaux 33063](https://www.insee.fr/fr/statistiques/2011101?geo=COM-33063) |
| **SSMSI - Sécurité** | ✅ Disponible | Données délinquance par commune 2016-2024 |
| **INSEE - Emploi** | ✅ Disponible | Population active, chômage par zone d'emploi |
| **Découpage IRIS** | ✅ Disponible | ~50 IRIS pour granularité infra-communale |

**→** Toutes les sources requises par le cahier des charges sont accessibles en open data pour Bordeaux, sans restriction ni demande d'accès spécifique.

---

### 4. Diversité Socio-Politique

| Critère | Bordeaux |
|---------|----------|
| **Diversité électorale** | Centre-ville progressiste, périphérie plus conservatrice |
| **Alternance politique** | Mairie PS (1947-2006) → UMP/LR (2006-2019) → EELV (2020) |
| **Variation socio-économique** | Quartiers aisés (Chartrons) ↔ QPV (Grand Parc, Bacalan) |
| **Dynamiques récentes** | Forte croissance démographique, gentrification |

**→** Bordeaux présente une diversité politique et socio-économique suffisante pour que les modèles ML captent des corrélations significatives entre indicateurs et votes. Une commune homogène aurait produit des prédictions triviales.

---

### 5. Extensibilité Maîtrisée

Le choix de la Gironde (535 communes) comme périmètre département permet :
- **Entraînement ML :** Suffisamment de communes pour un Random Forest (voir ADR-002)
- **Granularité :** Du département → commune → IRIS → bureau de vote
- **Extension future :** Bordeaux Métropole (28 communes) comme étape intermédiaire naturelle

---

## Alternatives Écartées

### Paris (75)
- ❌ Volumétrie excessive (~900 bureaux, ~990 IRIS) → incompatible avec 25h
- ❌ Spécificité parisienne (arrondissements ≠ communes) complexifie le schéma
- ❌ Données SSMSI agrégées différemment (Préfecture de Police)

### Lyon (69123)
- ⚠️ Volume acceptable mais pas de connaissance terrain de l'équipe
- ❌ Découpage en arrondissements municipaux (comme Paris/Marseille)
- ❌ Données sécurité moins granulaires à l'échelle commune

### Marseille (13055)
- ❌ Découpage en arrondissements municipaux (16 arrondissements, 8 secteurs)
- ❌ Volume élevé (~450 bureaux de vote)
- ❌ Problèmes connus de qualité des données électorales historiques

---

## Conséquences

### Positives
- Volumétrie maîtrisée → respect du budget 25h
- Données complètes et accessibles → pas de blocage data
- Connaissance locale → validation rapide des résultats
- Extensibilité vers Gironde entière puis autres départements

### Négatives
- Résultats non généralisables directement (spécifiques à la dynamique bordelaise)
- Biais potentiel si les tendances bordelaises ne reflètent pas les tendances nationales

### Risques Mitigés
- **Biais local :** Atténué par l'extension au département (535 communes = diversité rurale/urbaine)
- **Données manquantes :** Toutes les sources vérifiées et accessibles avant validation

---

## Références

- Cahier des charges MSPR : "Le POC doit porter sur UNE seule zone pour limiter la volumétrie"
- [INSEE - Dossier Bordeaux](https://www.insee.fr/fr/statistiques/2011101?geo=COM-33063)
- [SSMSI - Bases communales](https://www.interieur.gouv.fr/Interstats/Bases-de-donnees)
- [Ministère Intérieur - Résultats électoraux](https://www.data.gouv.fr/fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-1er-tour/)
