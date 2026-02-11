# Versions Archivées - Schéma Base de Données

Ce dossier archive les anciennes versions du schéma de base de données Electio-Analytics.

---

## 📂 Structure

```
versions/
├── README.md           # Ce fichier
├── CHANGELOG.md        # Historique détaillé des changements
├── VERSIONS.md         # Tableau comparatif versions
└── v1.0/               # Archive version 1.0
    ├── MCD.md          # Modèle Conceptuel v1.0 (5 tables séparées)
│   └── MCD.md          # Modèle Conceptuel v1.0 (5 tables séparées)
└── v2.0/               # Archive version 2.0
    └── MCD.md          # Proposition architecture scalable (snapshot v2.0)
```

---

## 🗂️ Versions Disponibles

### [v1.0] - 2026-02-09 - Schéma Initial (Archivée)

**Statut :** 🗄️ Archivée - Non maintenue

**Caractéristiques :**
- Architecture relationnelle classique (3FN)
- 5 tables : `territoire`, `election_result`, `indicateur_securite`, `indicateur_emploi`, `prediction`
- Tables séparées par type d'indicateur

**Documentation :**
- [MCD v1.0](v1.0/MCD.md)

**Raison d'archivage :**
- Remplacée par v2.0 (Architecture EAV Hybride)
- Limitations de scalabilité identifiées
- Maintenance complexe pour ajout de nouvelles sources

---

### [v2.0] - 2026-02-10 - Architecture Scalable (ACTUELLE) ⭐

**Statut :** ✅ Production - Activement maintenue

**Caractéristiques :**
- Architecture EAV Hybride
- 5 tables : `territoire`, `type_indicateur`, `indicateur`, `election_result`, `prediction`
- Table générique `indicateur` pour extensibilité maximale

**Documentation :**
- [README Principal](../README.md)
- [MCD v2.0 (Documentation Structurée)](../01-mcd.md)
- [MCD v2.0 (Snapshot Original)](v2.0/MCD.md)
- [MLD v2.0](../02-mld.md)
- [Dictionnaire de données](../03-dictionnaire-donnees.md)

---

## 📖 Documentation de Référence

### Pour Consulter l'Historique
📄 **[CHANGELOG.md](CHANGELOG.md)** - Historique détaillé des changements entre versions

### Pour Comparer les Versions
📊 **[VERSIONS.md](VERSIONS.md)** - Tableau comparatif v1.0 vs v2.0

### Pour Utiliser la Version Actuelle
📚 **[Documentation v2.0](../README.md)** - Documentation complète de la version en production

---

## 🔄 Politique de Versioning

### Numérotation Sémantique
```
MAJOR.MINOR.PATCH

MAJOR : Breaking change (incompatibilité)
MINOR : Nouvelle fonctionnalité compatible
PATCH : Correction bug ou optimisation
```

### Rétention des Archives
- **Versions MAJOR** : Archivées définitivement
- **Versions MINOR** : Conservées 1 an
- **Versions PATCH** : Non archivées (Git uniquement)

### Migration entre Versions
- **v1.0 → v2.0** : Migration manuelle requise (script fourni)
- **v2.x → v2.y** : Migration automatique (compatible)

---

## 🚀 Accès Rapide

| Besoin | Document |
|--------|----------|
| **Voir les changements récents** | [CHANGELOG.md](CHANGELOG.md) |
| **Comparer deux versions** | [VERSIONS.md](VERSIONS.md) |
| **Consulter schéma v1.0** | [v1.0/MCD.md](v1.0/MCD.md) |
| **Utiliser version actuelle** | [Documentation v2.0](../README.md) |
| **Migrer de v1.0 à v2.0** | [CHANGELOG.md - Section Migration](CHANGELOG.md#migration-v10--v20) |

---

## ⚠️ Important

> **Les versions archivées ne sont plus maintenues.**
>
> Pour les nouveaux projets, utilisez toujours la **version actuelle (v2.0)**.
>
> Les anciennes versions sont conservées uniquement à des fins de référence historique et pour faciliter les migrations.

---

**Dernière mise à jour :** 2026-02-10
**Version actuelle :** v2.0 (Architecture Scalable)
**Mainteneur :** @tech
