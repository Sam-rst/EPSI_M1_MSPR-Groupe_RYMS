# ADR-001 : Choix du Système de Gestion de Base de Données

**Status :** ✅ ACCEPTÉ
**Date :** 2026-02-09
**Décideurs :** Tech Lead (@archi)
**Contexte :** POC Electio-Analytics - Bordeaux Arrondissement Centre

---

## Contexte

Le projet nécessite une base de données pour centraliser :
- Résultats électoraux présidentielles (2017, 2022)
- Indicateurs socio-économiques (Sécurité SSMSI, Emploi INSEE)
- Prédictions générées par modèle ML (2027)

**Volumétrie :** ~26 650 lignes, ~50 Mo
**Périmètre :** Bordeaux Arrondissement Centre (~50 IRIS, ~80 bureaux de vote)
**Durée projet :** 25h (POC)

---

## Décision

**→ Base de données RELATIONNELLE (SQL) : PostgreSQL**

**Alternative évaluée :** NoSQL (MongoDB, DynamoDB)

---

## Justification

### 1. Nature des Données : **Structurées et Relationnelles**

| Critère | SQL | NoSQL |
|---------|-----|-------|
| **Structure** | Schéma fixe, tables normalisées | Flexible, documents JSON |
| **Relations** | Jointures natives (FK) | Références manuelles |
| **Intégrité** | Contraintes ACID garanties | Eventual consistency |

**➜ Nos données** : Relations 1-N strictes (Territoire ↔ Élections, Territoire ↔ Indicateurs)
**➜ Besoin** : Intégrité référentielle forte (pas de résultat électoral sans territoire associé)

**Verdict :** ✅ SQL adapté (relations complexes, intégrité critique)

---

### 2. Requêtes Analytiques : **Jointures Multi-Tables**

**Exemple de requête type :**
```sql
SELECT
    t.nom_territoire,
    er.candidat,
    er.pourcentage_voix,
    ie.taux_chomage,
    AVG(is.taux_pour_1000_hab) AS criminalite_moyenne
FROM Territoire t
JOIN Election_Result er ON t.id_territoire = er.id_territoire
JOIN Indicateur_Emploi ie ON t.id_territoire = ie.id_territoire AND ie.annee = er.annee
JOIN Indicateur_Securite is ON t.id_territoire = is.id_territoire AND is.annee = er.annee
WHERE t.type_territoire = 'IRIS' AND er.tour = 2
GROUP BY t.nom_territoire, er.candidat, er.pourcentage_voix, ie.taux_chomage;
```

**SQL :** Jointures optimisées nativement (indexes, query planner)
**NoSQL :** Nécessite agrégations MongoDB ($lookup) ou multiples requêtes applicatives (N+1)

**Verdict :** ✅ SQL performant pour analyses croisées

---

### 3. Volumétrie : **Faible (~50 Mo)**

| Base | Seuil optimal | Notre projet |
|------|---------------|--------------|
| **SQL** | < 10 Go | ~50 Mo ✅ |
| **NoSQL** | > 100 Go, millions documents | ~26k lignes ❌ Overkill |

**Verdict :** ✅ SQL suffisant (pas besoin de scalabilité NoSQL)

---

### 4. Consistance & Transactions : **ACID Requis**

**Scénario :** Import ETL en 3 étapes (Élections → Sécurité → Emploi)
- Si **Étape 2 échoue** → Rollback total (pas de données incohérentes)
- **SQL :** Transactions ACID natives (`BEGIN/COMMIT/ROLLBACK`)
- **NoSQL :** Cohérence éventuelle (risque de données partielles)

**Verdict :** ✅ SQL garantit intégrité transactionnelle

---

### 5. Outils ML/Data Science : **Compatibilité Python**

| Librairie | SQL | NoSQL |
|-----------|-----|-------|
| **Pandas** | `pd.read_sql()` natif | `pymongo` + conversions manuelles |
| **SQLAlchemy** | ORM complet | Support limité |
| **Scikit-Learn** | Pipeline direct depuis SQL | Requiert ETL intermédiaire |

**Verdict :** ✅ SQL s'intègre nativement aux pipelines data science

---

### 6. Requêtes Temporelles : **Time-Series**

**Besoin :** Évolution chômage 2017-2024, tendances criminalité, séries électorales

**SQL :** `WHERE annee BETWEEN 2017 AND 2024`, `ORDER BY annee`, `LAG/LEAD` (window functions)
**NoSQL :** Indexation manuelle dates, agrégations $match/$sort

**Verdict :** ✅ SQL optimisé pour analyses temporelles

---

## Comparaison Finale

| Critère | SQL (PostgreSQL) | NoSQL (MongoDB) | Gagnant |
|---------|------------------|-----------------|---------|
| **Structure relationnelle** | ✅ Natif | ⚠️ Références manuelles | SQL |
| **Jointures complexes** | ✅ Optimisé | ⚠️ Lookups lents | SQL |
| **Intégrité ACID** | ✅ Garanti | ❌ Eventual consistency | SQL |
| **Volumétrie faible** | ✅ Adapté | ⚠️ Overkill | SQL |
| **Analyses temporelles** | ✅ Window functions | ⚠️ Agrégations manuelles | SQL |
| **Compatibilité ML** | ✅ Pandas natif | ⚠️ Conversions requises | SQL |
| **Scalabilité horizontale** | ⚠️ Limitée | ✅ Excellente | NoSQL |
| **Flexibilité schéma** | ❌ Rigide | ✅ Dynamique | NoSQL |

**Score :** SQL 6/8 | NoSQL 2/8

---

## Choix de l'Implémentation SQL

### Option A : **PostgreSQL** ✅ RETENU

**Avantages :**
- Open-source, gratuit, mature
- Support JSONB (flexibilité future sans perdre SQL)
- Extension PostGIS (cartographie géographique)
- Window functions avancées (LAG, LEAD, RANK)
- Excellent support Python (psycopg2, SQLAlchemy)

**Inconvénients :**
- Installation requise (Docker recommandé pour POC)

### Option B : SQLite

**Avantages :**
- Zéro configuration (fichier .db local)
- Parfait pour POC rapide

**Inconvénients :**
- Pas de support GEOMETRY (cartographie limitée)
- Performances moindres sur jointures complexes
- Pas de concurrent access (monoutilisateur)

### Option C : MySQL/MariaDB

**Avantages :**
- Très répandu, bonne documentation

**Inconvénients :**
- Window functions limitées (vs PostgreSQL)
- Pas de support JSONB
- Moins adapté pour analytics

---

## Décision Finale : PostgreSQL

**Justification :**
1. **PostGIS** : Support cartographique natif (polygones IRIS, visualisations)
2. **JSONB** : Flexibilité future (ajout métadonnées sans migration schema)
3. **Window Functions** : Calculs évolutions temporelles (LAG chômage année N-1)
4. **Performance** : Query planner avancé pour jointures 4+ tables
5. **Écosystème Python** : SQLAlchemy ORM + Pandas seamless

**Setup recommandé :**
```bash
# Docker Compose (déploiement rapide)
docker run -d \
  --name electio-postgres \
  -e POSTGRES_DB=electio_analytics \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgis/postgis:15-3.3
```

---

## Conséquences

### Positives ✅
- Intégrité des données garantie (ACID)
- Requêtes analytiques performantes (jointures optimisées)
- Compatibilité native avec stack data science Python
- Évolutivité suffisante pour phase industrielle (hors POC)
- Support cartographique via PostGIS

### Négatives ⚠️
- Installation/configuration requise (vs SQLite zero-config)
- Schéma rigide (migrations nécessaires si changements structure)
- Scalabilité horizontale limitée (mais non requis pour périmètre POC)

### Risques Atténués 🛡️
- **Risque :** Perte de données lors ETL
  - **Mitigation :** Transactions SQL avec rollback automatique
- **Risque :** Lenteur jointures (4 tables)
  - **Mitigation :** Indexes composés sur (id_territoire, annee)
- **Risque :** Complexité setup PostgreSQL
  - **Mitigation :** Docker Compose one-liner (5 min setup)

---

## Alternatives Rejetées

### ❌ MongoDB (NoSQL Document)
- **Raison rejet :** Relations 1-N complexes nécessitent $lookup lents
- **Cas usage valide :** Si données non structurées (tweets, commentaires)

### ❌ Neo4j (Graph Database)
- **Raison rejet :** Pas de relations de type graphe (pas de réseau social, pas de hiérarchies complexes)
- **Cas usage valide :** Si analyse réseaux d'influence électorale

### ❌ InfluxDB (Time-Series)
- **Raison rejet :** Pas d'optimisation temps réel, données batch annuelles/trimestrielles
- **Cas usage valide :** Si streaming temps réel (sondages minute par minute)

---

## Plan de Migration (Si Évolution Future)

**Scénario :** Passage à l'échelle nationale (96 départements, 36k communes)

1. **Volumétrie estimée :** ~10 Go de données
2. **Solution :**
   - Conserver PostgreSQL
   - Sharding par département (partitionnement horizontal)
   - Cache Redis pour requêtes fréquentes
   - Réplication read-replicas pour analytics

**Pas de migration NoSQL nécessaire** (PostgreSQL scale jusqu'à plusieurs To avec optimisations)

---

## Validation

- [x] Compatibilité avec stack Python (Pandas, SQLAlchemy)
- [x] Support des relations 1-N (5 entités liées)
- [x] Transactions ACID pour intégrité ETL
- [x] Requêtes analytiques performantes (jointures 4 tables)
- [x] Volumétrie adaptée (~50 Mo)
- [x] Setup rapide pour POC (Docker Compose)

---

## Références

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [PostGIS Spatial Database](https://postgis.net/)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- [Pandas SQL Integration](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)

---

**Statut :** ✅ Décision approuvée
**Prochaine étape :** Phase 3 - Data Engineering (`@dataeng` crée scripts ETL + setup PostgreSQL)
