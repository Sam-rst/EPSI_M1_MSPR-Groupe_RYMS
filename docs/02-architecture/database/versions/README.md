# Versions du Modèle Conceptuel de Données (MCD)

Ce dossier archive les versions historiques du MCD pour traçabilité.

---

## Historique des Versions

### v3.0 (2026-02-12) - **Version Actuelle**
**Fichier :** [v3.0/MCD.md](./v3.0/MCD.md)

**Changements majeurs :**
- ✅ Hiérarchie géographique explicite (Region → Departement → Canton/Commune → Arrondissement → Bureau)
- ✅ Entités Candidat, Parti, CandidatParti
- ✅ Séparation ResultatParticipation / ResultatCandidat
- ✅ Système polymorphe de territoire (id_territoire + type_territoire)
- ✅ Suppression colonne geometry (simplification)
- ✅ Table ElectionTerritoire pour tracker granularités
- ❌ Suppression table TERRITOIRE (remplacée par hiérarchie)
- ❌ Suppression table ELECTION_RESULT (remplacée par resultat_participation + resultat_candidat)

**Tables :** 19 (vs 5 en v2.0)
**Volumétrie POC :** ~69 000 lignes

---

### v2.0 (2026-02-10) - Obsolète
**Changements v1.0 → v2.0 :**
- ✅ Pattern EAV pour indicateurs (TYPE_INDICATEUR + INDICATEUR)
- ✅ Colonne geometry PostGIS
- ✅ JSONB metadata
- ✅ Table PREDICTION

**Tables :** 5 (TERRITOIRE, TYPE_INDICATEUR, INDICATEUR, ELECTION_RESULT, PREDICTION)

---

### v1.0 (2026-02-08) - Obsolète
**Version initiale :**
- Tables basiques : TERRITOIRE, ELECTION_RESULT
- Schéma simple sans normalisation

---

## Migration Entre Versions

**v2.0 → v3.0 :**
```bash
# Nettoyage tables obsolètes
alembic upgrade 5c74986a8b20  # Migration cleanup

# Création schéma v3.0
alembic upgrade head  # Migration 691a1578615b
```

**Migration données :** À prévoir si données v2.0 existantes (script ETL de migration)

---

**Version active :** v3.0
**Dernière mise à jour :** 2026-02-12
