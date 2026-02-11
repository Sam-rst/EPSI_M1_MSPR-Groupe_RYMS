# Conventions de Documentation

**Projet :** Electio-Analytics
**Responsable :** @pm
**Dernière mise à jour :** 2026-02-09

---

## 📋 Règles Générales

### 1. Organisation par Thème

La documentation est **obligatoirement** organisée en dossiers thématiques :

```
docs/
├── 00-cahier-des-charges/    # Sujet officiel, contraintes
├── 01-project-management/    # Roadmap, planning, suivi
├── 02-architecture/          # MCD, ETL, ADRs techniques
├── 03-data-sources/          # Sources de données, URLs
├── 04-setup-installation/    # Installation, validation
└── 05-reports/               # Rapports finaux, livrables
```

### 2. Numérotation des Dossiers

- **Obligatoire** : Préfixer les dossiers par `XX-` (ex: `01-`, `02-`)
- **Ordre logique** : Du général (00) au spécifique (05+)
- **Incréments de 1** : 00, 01, 02, 03, etc.

### 3. Nommage des Fichiers

#### Documents Principaux
- **MAJUSCULES.md** : Documents de référence
  - `ROADMAP.md`, `MCD.md`, `ARCHITECTURE.md`

#### Documents Spécifiques
- **kebab-case.md** : Documents techniques
  - `ADR-001-choix-bdd.md`, `ADR-002-choix-algo-ml.md`

#### ADRs (Architecture Decision Records)
- **Format strict** : `ADR-XXX-description.md`
  - `XXX` = numéro séquentiel (001, 002, 003)
  - `description` = résumé décision (kebab-case)
  - Exemples : `ADR-001-choix-bdd.md`, `ADR-002-choix-algo-ml.md`

### 4. Format des Documents

#### En-tête Obligatoire

Tous les documents markdown doivent commencer par :

```markdown
# Titre du Document

**Date :** YYYY-MM-DD
**Agent :** @role (ex: @pm, @tech, @de)
**Status :** Statut actuel

---
```

#### Sections Recommandées

Pour les documents techniques :
1. **Contexte** : Pourquoi ce document ?
2. **Décision** ou **Objectif** : Quoi ?
3. **Justification** : Pourquoi cette décision ?
4. **Alternatives** : Qu'est-ce qui a été rejeté ?
5. **Conséquences** : Impact de la décision

---

## 📁 Guide par Type de Document

### Type 1 : ROADMAP

**Emplacement :** `01-project-management/ROADMAP.md`

**Contenu obligatoire :**
- Périmètre validé
- Phases du projet (avec durées)
- État d'avancement (tableau)
- Livrables par phase
- Prochaine étape

**Mise à jour :** Fin de chaque phase

---

### Type 2 : MCD (Modèle Conceptuel de Données)

**Emplacement :** `02-architecture/MCD.md`

**Contenu obligatoire :**
- Vue d'ensemble (diagramme)
- Entités avec champs détaillés
- Relations (1-N, N-N) avec FK
- Contraintes d'intégrité
- Volumétrie estimée

**Mise à jour :** Si changement de schéma BDD

---

### Type 3 : ARCHITECTURE

**Emplacement :** `02-architecture/ARCHITECTURE.md`

**Contenu obligatoire :**
- Vue d'ensemble du système
- Diagrammes (Mermaid recommandé)
- Modules et leurs interactions
- Pipeline de données (si applicable)
- Configuration et déploiement

**Mise à jour :** Si changement architectural

---

### Type 4 : ADR (Architecture Decision Record)

**Emplacement :** `02-architecture/adr/ADR-XXX-description.md`

**Template obligatoire :**

```markdown
# ADR-XXX : Titre de la Décision

**Status :** ✅ ACCEPTÉ / 🔄 EN COURS / ❌ REJETÉ
**Date :** YYYY-MM-DD
**Décideurs :** @role1, @role2
**Contexte :** Brève description du projet

---

## Contexte
Pourquoi cette décision est nécessaire ?

## Décision
Quelle solution a été choisie ?

## Justification
Pourquoi cette solution (arguments techniques) ?

## Alternatives Rejetées
Quelles autres options ont été évaluées ?

## Conséquences
Quels sont les impacts (positifs et négatifs) ?

## Références
Liens vers docs externes
```

**Numérotation :** Séquentielle (001, 002, 003, ...)

---

### Type 5 : SOURCES_DONNEES

**Emplacement :** `03-data-sources/SOURCES_DONNEES.md`

**Contenu obligatoire :**
- Liste des sources (URLs complètes)
- Métadonnées (format, granularité, période)
- Champs attendus
- Structure des fichiers téléchargés
- Checklist de téléchargement

**Mise à jour :** Si ajout de nouvelle source

---

### Type 6 : SETUP / Installation

**Emplacement :** `04-setup-installation/`

**Documents :**
- `SETUP_XXX.md` : Guide d'installation
- `VALIDATION_XXX.md` : Rapport de validation

**Contenu SETUP obligatoire :**
- Prérequis
- Installation étape par étape
- Configuration (.env, etc.)
- Tests de validation
- Troubleshooting

**Contenu VALIDATION obligatoire :**
- Résumé exécutif
- Versions des packages
- Tests d'imports
- Rapport de conformité

---

### Type 7 : RAPPORT

**Emplacement :** `05-reports/`

**Documents attendus :**
- `RAPPORT_SYNTHESE.md` : Rapport final du POC
- `METRIQUES.md` : Métriques ML détaillées
- `PRESENTATION.pdf` : Slides exécutives

**Contenu RAPPORT_SYNTHESE :**
1. Résumé exécutif (1 page)
2. Méthodologie (2 pages)
3. Résultats (2 pages)
4. Limites du POC (1 page)
5. Recommandations (1 page)

---

## 📝 Processus de Documentation

### Ajout d'un Nouveau Document

1. **Identifier le thème** : Quel dossier (00-, 01-, 02-, etc.) ?
2. **Nommer correctement** : Respecter les conventions
3. **Utiliser le template** : En-tête + sections obligatoires
4. **Mettre à jour README.md** : Ajouter dans l'index `docs/README.md`
5. **Commit Git** : Message clair (ex: `docs: add ADR-003 choice of visualization tool`)

### Mise à Jour d'un Document

1. **Modifier le document**
2. **Mettre à jour la date** dans l'en-tête
3. **Ajouter une ligne** dans la section "Mises à Jour" de `docs/README.md`
4. **Commit Git** : Message clair (ex: `docs: update ROADMAP - Phase 3 completed`)

---

## 🔍 Checklist Avant Commit

- [ ] Le document est dans le bon dossier thématique
- [ ] Le nom du fichier respecte les conventions
- [ ] L'en-tête est complet (Date, Agent, Status)
- [ ] Le contenu suit le template approprié
- [ ] `docs/README.md` est mis à jour (si nouveau document)
- [ ] Les liens internes fonctionnent
- [ ] Le markdown est valide (pas d'erreurs de syntaxe)

---

## 🚫 À Éviter

### ❌ Ne PAS faire

- Créer des fichiers à la racine de `docs/`
- Utiliser des espaces dans les noms de fichiers
- Utiliser des caractères spéciaux (é, à, ç) dans les noms
- Créer des sous-dossiers non numérotés
- Dupliquer l'information (maintenir une source unique)
- Oublier de mettre à jour `docs/README.md`

### ✅ À faire

- Toujours placer dans un dossier thématique numéroté
- Utiliser kebab-case ou MAJUSCULES selon le type
- Utiliser uniquement ASCII dans les noms de fichiers
- Respecter la structure existante
- Centraliser l'information
- Maintenir l'index à jour

---

## 📊 Structure Complète Attendue

```
docs/
├── README.md                               ← Index complet (TOUJOURS à jour)
├── CONVENTIONS.md                          ← Ce fichier
│
├── 00-cahier-des-charges/
│   └── Sujet_MSPR.pdf                      ← Sujet officiel
│
├── 01-project-management/
│   ├── ROADMAP.md                          ← Planning projet
│   └── RETROSPECTIVE.md                    ← Bilan projet (fin)
│
├── 02-architecture/
│   ├── MCD.md                              ← Base de données
│   ├── ARCHITECTURE.md                     ← Pipeline ETL
│   ├── DIAGRAMMES.md                       ← Schémas techniques
│   └── adr/
│       ├── ADR-001-choix-bdd.md
│       ├── ADR-002-choix-algo-ml.md
│       └── ADR-XXX-nouvelle-decision.md
│
├── 03-data-sources/
│   ├── SOURCES_DONNEES.md                  ← URLs et métadonnées
│   └── DICTIONNAIRE_DONNEES.md             ← Définition des champs
│
├── 04-setup-installation/
│   ├── SETUP_UV.md                         ← Installation UV
│   ├── SETUP_POSTGRES.md                   ← Installation PostgreSQL
│   ├── VALIDATION_UV.md                    ← Rapport validation UV
│   └── TROUBLESHOOTING.md                  ← Résolution problèmes
│
└── 05-reports/
    ├── README.md                           ← Guide des livrables
    ├── RAPPORT_SYNTHESE.md                 ← Rapport final
    ├── METRIQUES.md                        ← Métriques ML
    └── PRESENTATION.pdf                    ← Slides exécutives
```

---

## 🔄 Versioning Documentation

### Principe

Chaque document majeur doit avoir un **historique de versions** en bas de page :

```markdown
---

## Historique des Versions

| Version | Date | Auteur | Changements |
|---------|------|--------|-------------|
| 1.0 | 2026-02-09 | @tech | Création initiale |
| 1.1 | 2026-02-10 | @tech | Ajout section validation |
| 2.0 | 2026-02-15 | @pm | Refonte complète suite Phase 3 |
```

---

## 📞 Responsabilités

| Rôle | Responsabilité Documentation |
|------|------------------------------|
| **@pm** | Maintien de `docs/README.md`, ROADMAP, conventions |
| **@tech** | MCD, ARCHITECTURE, ADRs techniques |
| **@de** | SOURCES_DONNEES, documentation ETL |
| **@ds** | Documentation modèles ML, métriques |
| **@analyst** | Rapports, présentations |
| **@review** | Validation qualité documentation |

---

## 🎯 Objectif

**Une documentation claire, structurée et maintenable pour :**
- ✅ Faciliter l'onboarding de nouveaux membres
- ✅ Traçabilité des décisions techniques
- ✅ Reproductibilité du projet
- ✅ Transfert de connaissances
- ✅ Conformité MSPR / EPSI

---

**Maintenu par :** @pm
**Dernière révision :** 2026-02-09
