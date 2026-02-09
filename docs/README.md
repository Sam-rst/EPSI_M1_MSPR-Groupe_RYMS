# Documentation Electio-Analytics

**Projet MSPR - M1 EPSI - Groupe RYMS**
**Dernière mise à jour :** 2026-02-09

---

## 📚 Organisation de la Documentation

La documentation est organisée par **thème** pour faciliter la navigation et la maintenance.

### Structure des Dossiers

```
docs/
├── README.md                         ← Vous êtes ici
│
├── 00-cahier-des-charges/           ← Sujet et contraintes projet
│   └── Sujet MSPR TPRE813.pdf
│
├── 01-project-management/           ← Gestion de projet
│   └── ROADMAP.md
│
├── 02-architecture/                 ← Décisions techniques
│   ├── MCD.md
│   ├── ARCHITECTURE.md
│   └── adr/
│       ├── ADR-001-choix-bdd.md
│       └── ADR-002-choix-algo-ml.md
│
├── 03-data-sources/                 ← Sources de données
│   └── SOURCES_DONNEES.md
│
├── 04-setup-installation/           ← Installation et configuration
│   ├── SETUP_UV.md
│   └── VALIDATION_UV.md
│
└── 05-reports/                      ← Rapports et livrables
    └── (rapports de synthèse, présentations)
```

---

## 📋 Index des Documents

### 00. Cahier des Charges

| Document | Description | Statut |
|----------|-------------|--------|
| [Sujet MSPR](00-cahier-des-charges/Sujet%20MSPR%20TPRE813%20EISI_DEV_INFRA.pdf) | Cahier des charges officiel EPSI | ✅ Original |

---

### 01. Project Management

| Document | Description | Statut |
|----------|-------------|--------|
| [ROADMAP.md](01-project-management/ROADMAP.md) | Planning 25h, 6 phases, avancement 6h/25h (24%) | ✅ Jour |

**Contenu :**
- Périmètre validé (Bordeaux, Présidentielles 2017/2022)
- Phases détaillées (Cadrage, Architecture, Data Eng, Data Science, Visualisation, Qualité)
- État d'avancement (Phase 1 & 2 terminées)
- Prochaine étape : Phase 3 - Data Engineering

---

### 02. Architecture

#### 2.1 Modèles & Schémas

| Document | Description | Statut |
|----------|-------------|--------|
| [MCD.md](02-architecture/MCD.md) | Modèle Conceptuel de Données (5 entités) | ✅ Complet |
| [ARCHITECTURE.md](02-architecture/ARCHITECTURE.md) | Pipeline ETL (Extract, Transform, Load) | ✅ Complet |

**MCD - Entités :**
1. `Territoire` (IRIS, Bureaux de vote)
2. `Election_Result` (Présidentielles 2017/2022)
3. `Indicateur_Securite` (SSMSI, 13 indicateurs)
4. `Indicateur_Emploi` (INSEE, chômage)
5. `Prediction` (Résultats 2027 prédits)

**Architecture ETL - Phases :**
1. **Extract :** Téléchargement data.gouv.fr, INSEE, SSMSI
2. **Transform :** Nettoyage, harmonisation géographique (Bureau → IRIS)
3. **Load :** Chargement PostgreSQL, validation intégrité

#### 2.2 Architecture Decision Records (ADRs)

| Document | Décision | Justification | Statut |
|----------|----------|---------------|--------|
| [ADR-001](02-architecture/adr/ADR-001-choix-bdd.md) | **PostgreSQL** (SQL) | Relations 1-N, jointures, ACID, volumétrie faible | ✅ Approuvé |
| [ADR-002](02-architecture/adr/ADR-002-choix-algo-ml.md) | **Random Forest** | Non-linéaire, feature importance, peu de tuning | ✅ Approuvé |

**ADR-001 - Alternatives rejetées :**
- ❌ MongoDB (NoSQL) : Relations complexes mal adaptées
- ❌ Neo4j (Graph) : Pas de réseau à modéliser

**ADR-002 - Alternatives évaluées :**
- ✅ Régression Linéaire (baseline)
- ✅ Random Forest (principal) ← **CHOISI**
- ⏳ XGBoost (fallback si temps disponible)
- ❌ Deep Learning (nécessite >1000 points, on en a 100)

---

### 03. Sources de Données

| Document | Description | Statut |
|----------|-------------|--------|
| [SOURCES_DONNEES.md](03-data-sources/SOURCES_DONNEES.md) | URLs, métadonnées, 4 fichiers élections obligatoires | ✅ Complet |

**Données à collecter :**

| Source | Données | Granularité | Période | Statut |
|--------|---------|-------------|---------|--------|
| **data.gouv.fr** | Élections Présidentielles | Bureau de vote | 2017 T1/T2, 2022 T1/T2 | 📥 À télécharger |
| **SSMSI** | Criminalité (13 indicateurs) | Commune | 2017-2024 | 📥 À télécharger |
| **INSEE** | Chômage, Emploi, Revenus | IRIS | 2017-2024 | 📥 À télécharger |

**Fichiers requis (4 CSV) :**
1. `presidentielles_2017_tour1_bureaux_vote.csv`
2. `presidentielles_2017_tour2_bureaux_vote.csv`
3. `presidentielles_2022_tour1_bureaux_vote.csv`
4. `presidentielles_2022_tour2_bureaux_vote.csv`

---

### 04. Setup & Installation

| Document | Description | Statut |
|----------|-------------|--------|
| [SETUP_UV.md](04-setup-installation/SETUP_UV.md) | Guide d'installation UV (20 pages) | ✅ Complet |
| [VALIDATION_UV.md](04-setup-installation/VALIDATION_UV.md) | Rapport validation environnement (10 pages) | ✅ Validé |

**SETUP_UV.md - Sections :**
- Qu'est-ce que UV ? (10-100x plus rapide que pip)
- Installation (Windows/macOS/Linux)
- Initialisation projet (`uv sync --all-extras`)
- Commandes essentielles
- Troubleshooting

**VALIDATION_UV.md - Résultats :**
- ✅ 153 packages installés (~4 minutes)
- ✅ Python 3.11.12
- ✅ 19/19 packages critiques validés (pandas, scikit-learn, xgboost, geopandas, etc.)
- ✅ Environnement prêt pour Phase 3

---

### 05. Reports & Livrables

| Document | Description | Statut |
|----------|-------------|--------|
| `RAPPORT_SYNTHESE.md` | Rapport final (méthodologie, résultats, limites) | ⏸️ Phase 5 |
| `METRIQUES.md` | Métriques ML (R², MAE, RMSE) | ⏸️ Phase 4 |
| `PRESENTATION.pdf` | Slides exécutives (10 slides max) | ⏸️ Phase 5 |

---

## 🔍 Navigation Rapide par Besoin

### Je veux...

**...comprendre le projet**
→ [ROADMAP.md](01-project-management/ROADMAP.md)

**...installer l'environnement**
→ [SETUP_UV.md](04-setup-installation/SETUP_UV.md)

**...comprendre la base de données**
→ [MCD.md](02-architecture/MCD.md)

**...comprendre le pipeline ETL**
→ [ARCHITECTURE.md](02-architecture/ARCHITECTURE.md)

**...télécharger les données**
→ [SOURCES_DONNEES.md](03-data-sources/SOURCES_DONNEES.md)

**...comprendre pourquoi PostgreSQL ?**
→ [ADR-001](02-architecture/adr/ADR-001-choix-bdd.md)

**...comprendre pourquoi Random Forest ?**
→ [ADR-002](02-architecture/adr/ADR-002-choix-algo-ml.md)

**...vérifier l'installation**
→ [VALIDATION_UV.md](04-setup-installation/VALIDATION_UV.md)

---

## 📊 Statistiques Documentation

| Métrique | Valeur |
|----------|--------|
| **Documents totaux** | 9 |
| **Pages totales** | ~50 pages |
| **ADRs** | 2 |
| **Taille totale** | ~500 Ko (hors PDF) |

---

## 🔄 Mises à Jour

| Date | Document | Changement |
|------|----------|------------|
| 2026-02-09 | VALIDATION_UV.md | ✅ Création (validation environnement) |
| 2026-02-09 | ADR-002 | ✅ Création (choix Random Forest) |
| 2026-02-09 | ARCHITECTURE.md | ✅ Création (pipeline ETL) |
| 2026-02-09 | ROADMAP.md | 🔄 Mise à jour (Phase 2 terminée 100%) |
| 2026-02-09 | README.md (docs) | ✅ Création (index documentation) |

---

## 📝 Conventions de Nommage

### Fichiers Markdown
- **MAJUSCULES** : Documents principaux (ex: `ROADMAP.md`, `MCD.md`)
- **PascalCase** : Documents spécifiques (ex: `Sujet_MSPR.pdf`)
- **kebab-case** : ADRs (ex: `ADR-001-choix-bdd.md`)

### Dossiers
- **00-XX-nom/** : Numérotation pour ordre logique
- **kebab-case** : Noms de dossiers (ex: `project-management`, `data-sources`)

---

## 🚀 Prochaines Étapes

1. ⏳ **Phase 3 - Data Engineering** : Téléchargement et transformation données
2. ⏸️ **Phase 4 - Data Science** : Entraînement modèle Random Forest
3. ⏸️ **Phase 5 - Visualisation** : Rapport de synthèse + Présentation

---

## 📞 Maintenance Documentation

**Responsable :** @pm
**Fréquence révision :** Fin de chaque phase
**Format :** Markdown (compatible GitHub, MkDocs)

**Règles :**
- ✅ Toujours mettre à jour README.md lors d'ajout de document
- ✅ Respecter la structure par thème
- ✅ Numéroter les dossiers (00-, 01-, 02-, etc.)
- ✅ Utiliser des noms de fichiers explicites

---

**Dernière révision :** 2026-02-09 par @pm
