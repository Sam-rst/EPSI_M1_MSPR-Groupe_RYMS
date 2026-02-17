# Audit RGPD - Electio-Analytics

> **Analyse de conformite au Reglement General sur la Protection des Donnees**
> Groupe RYMS - EPSI M1 - Bloc 3 RNCP35584
> Date d'audit : 18 fevrier 2026

---

## 1. Objet de l'audit

Cet audit evalue la conformite du POC Electio-Analytics aux obligations du RGPD (Reglement UE 2016/679) et aux procedures de securite des donnees, conformement au cahier des charges du Bloc 3 RNCP35584 :

> *"Appliquer les procedures de securite etablies par le/la RSSI de l'entreprise afin d'assurer la confidentialite et la securite des donnees et garantir une mise en conformite avec les obligations legales du RGPD."*

---

## 2. Classification des donnees

### 2.1 Inventaire des donnees traitees

| Categorie | Donnees | Granularite | Source | Caractere personnel |
|-----------|---------|-------------|--------|---------------------|
| Geographie | Communes, departements, regions | Commune | geo.api.gouv.fr | **NON** |
| Elections | Nombre de voix, % par candidat | Bureau / Commune | data.gouv.fr | **NON** |
| Participation | Inscrits, votants, abstentions | Bureau / Commune | data.gouv.fr | **NON** |
| Candidats | Nom, prenom, nuance politique | National | data.gouv.fr | **NON** (personnages publics) |
| Securite | Faits de delinquance par type | Commune | SSMSI / data.gouv.fr | **NON** |
| Predictions | % predit par candidat et commune | Commune | Modele ML interne | **NON** |

### 2.2 Verdict : absence de donnees personnelles

**Aucune donnee a caractere personnel n'est collectee, stockee ou traitee dans ce POC.**

- Pas de noms d'electeurs individuels
- Pas d'adresses, emails ou numeros de telephone
- Pas de donnees de localisation individuelle
- Pas de donnees sensibles (opinions politiques individuelles, sante, religion)
- Toutes les donnees sont **agregees** au niveau commune ou bureau de vote
- Les noms de candidats sont des **informations publiques** (personnalites politiques)

### 2.3 Base legale du traitement

| Critere RGPD | Application |
|--------------|-------------|
| Article 6.1(e) - Mission d'interet public | Donnees electorales publiees par le Ministere de l'Interieur |
| Article 6.1(f) - Interet legitime | Analyse statistique a partir de donnees publiques agregees |
| Licence ouverte Etalab 2.0 | Toutes les sources data.gouv.fr sont sous licence ouverte |

---

## 3. Sources de donnees et tracabilite

### 3.1 Registre des sources

| # | Source | URL | Licence | Date collecte | Format |
|---|--------|-----|---------|--------------|--------|
| 1 | API Geo Communes | `geo.api.gouv.fr/departements/33/communes` | Licence ouverte Etalab 2.0 | 2026-02 | JSON |
| 2 | Elections Presidentielles 2017 | `data.gouv.fr` (Ministere Interieur) | Licence ouverte Etalab 2.0 | 2026-02 | JSON |
| 3 | Elections Presidentielles 2022 | `data.gouv.fr` (Ministere Interieur) | Licence ouverte Etalab 2.0 | 2026-02 | Parquet |
| 4 | Delinquance SSMSI | `data.gouv.fr` (SSMSI) | Licence ouverte Etalab 2.0 | 2026-02 | CSV gzip |

### 3.2 Attribution

La documentation des sources est maintenue dans `docs/01-project-management/SOURCES_DONNEES.md` avec les URLs exactes, formats et instructions de telechargement.

---

## 4. Mesures de securite techniques

### 4.1 Gestion des secrets

| Mesure | Implementation | Fichier de reference |
|--------|---------------|---------------------|
| Variables d'environnement | Credentials PostgreSQL charges via `python-dotenv` | `src/database/config.py` |
| Fichier .env exclu du depot | `.env` present dans `.gitignore` (2 entrees) | `.gitignore` (lignes 26, 77) |
| Template fourni | `.env.example` avec valeurs factices | `.env.example` |
| Encodage mot de passe | `urllib.parse.quote_plus()` pour les caracteres speciaux | `src/database/config.py:68` |

**Verification :**
```
# .gitignore contient :
.env
```
→ Le fichier `.env` contenant les credentials reels ne sera jamais commite.

### 4.2 Prevention injection SQL

| Mesure | Implementation | Fichier de reference |
|--------|---------------|---------------------|
| ORM SQLAlchemy | Requetes parametrees par defaut via l'ORM | `src/etl/load/core/*.py` |
| Bind parameters | `text("SELECT ... WHERE x = :param")` avec dictionnaire | `src/database/config.py:219` |
| Validation regex | Nom de base de donnees valide par `^[a-zA-Z_][a-zA-Z0-9_]*$` | `src/database/config.py:204` |

### 4.3 Securite de la base de donnees

| Mesure | Implementation | Fichier de reference |
|--------|---------------|---------------------|
| Connection pooling | `pool_pre_ping=True`, `pool_recycle=3600` | `src/database/config.py:125-126` |
| Singleton engine | Instance unique pour eviter les fuites de connexions | `src/database/config.py:118` |
| Transaction safety | `try/except IntegrityError` avec rollback | `src/etl/load/core/*.py` |
| Contraintes d'integrite | FK, UNIQUE, CHECK (0-100%) sur toutes les tables | `src/database/models/*.py` |

### 4.4 Securite de l'infrastructure Docker

| Mesure | Implementation | Fichier de reference |
|--------|---------------|---------------------|
| Reseau isole | Bridge network `electio_network` | `docker-compose.yml` |
| Health checks | `pg_isready` toutes les 10s, 5 retries | `docker-compose.yml:19-23` |
| Init script read-only | Mount `:ro` pour `init-db.sql` | `docker-compose.yml:16` |
| Credentials via env | `${POSTGRES_PASSWORD:-secure_password}` | `docker-compose.yml:10` |
| Volume persistant | `postgres_data` pour les donnees | `docker-compose.yml:14` |

### 4.5 Validation des donnees (ETL)

14 fonctions de validation implementees dans `src/etl/load/utils/validators.py` :

| Validation | Description |
|------------|-------------|
| `validate_csv_exists` | Verification existence fichier |
| `validate_dataframe_not_empty` | Detection jeux de donnees vides |
| `validate_required_columns` | Validation schema (colonnes attendues) |
| `validate_no_nulls` | Detection valeurs NULL interdites |
| `validate_year_range` | Bornes temporelles (annees coherentes) |
| `validate_positive_values` | Types de donnees positifs |
| `validate_percentage_range` | Plage 0-100% |
| `validate_unique_key` | Unicite des cles primaires |

### 4.6 Journalisation

| Mesure | Implementation |
|--------|---------------|
| Logs ETL | Chaque phase (extract/transform/load) journalise succes/echec |
| Logs exclus du depot | `logs/*.log` et `*.log` dans `.gitignore` |
| SQL debug configurable | `DB_ECHO_SQL=True/False` via variable d'environnement |

---

## 5. Analyse des droits des personnes

| Droit RGPD | Applicabilite | Justification |
|------------|---------------|---------------|
| Droit d'acces (Art. 15) | **Non applicable** | Aucune donnee personnelle collectee |
| Droit de rectification (Art. 16) | **Non applicable** | Donnees publiques, pas de collecte individuelle |
| Droit a l'effacement (Art. 17) | **Non applicable** | Aucune donnee individuelle a effacer |
| Droit a la portabilite (Art. 20) | **Non applicable** | Pas de donnees personnelles a transferer |
| Droit d'opposition (Art. 21) | **Non applicable** | Pas de profilage individuel |
| Decision automatisee (Art. 22) | **Non applicable** | Predictions agregees par commune, pas de decision individuelle |

**Justification globale :** le traitement porte exclusivement sur des donnees statistiques agregees publiees en open data. Aucun individu n'est identifiable directement ou indirectement a partir des donnees traitees.

---

## 6. Analyse des risques

### 6.1 Risques identifies et mitigation

| Risque | Probabilite | Impact | Mitigation | Risque residuel |
|--------|-------------|--------|-----------|-----------------|
| Fuite de credentials BDD | Faible | Moyen | `.env` dans `.gitignore`, `quote_plus` | Faible |
| Injection SQL | Tres faible | Eleve | ORM SQLAlchemy, bind parameters, regex | Tres faible |
| Acces non autorise a la BDD | Faible | Moyen | Reseau Docker isole, credentials env | Faible |
| Corruption des donnees | Faible | Moyen | Contraintes FK/CHECK/UNIQUE, validators | Tres faible |
| Re-identification individuelle | Nulle | Eleve | Donnees agregees par commune (>40 hab.) | Nul |

### 6.2 Risques acceptes (perimetre POC)

| Risque | Justification |
|--------|---------------|
| Pas de chiffrement TLS PostgreSQL | Connexion locale uniquement (Docker bridge) |
| Utilisateur unique BDD | POC mono-application, pas de multi-tenant |
| Pas de politique de mot de passe | Credentials locaux pour developpement |

---

## 7. Conformite aux exigences du cahier des charges

| Exigence CdC (Bloc 3) | Implementation | Conforme |
|------------------------|---------------|----------|
| Assurer la confidentialite des donnees | Credentials en `.env`, `.gitignore`, reseau Docker isole | OUI |
| Assurer la securite des donnees | Injection SQL prevenue, contraintes BDD, validators ETL | OUI |
| Garantir la mise en conformite RGPD | Aucune donnee personnelle, sources publiques, audit documente | OUI |
| Assurer la tracabilite des donnees | Sources documentees, logs ETL, versioning Alembic | OUI |
| Assurer l'exactitude des donnees | 14 validators, contraintes CHECK, code review 7/10 | OUI |
| Assurer la coherence des donnees | Schema 3NF, FK strictes, normalisation ETL | OUI |
| Satisfaire les besoins d'accessibilite | ORM SQLAlchemy, API models, documentation complete | OUI |

---

## 8. Conclusion et recommandations

### 8.1 Conclusion

Le POC Electio-Analytics est **conforme au RGPD** dans son perimetre actuel. L'absence totale de donnees a caractere personnel, combinee aux mesures de securite technique implementees (injection SQL, gestion des secrets, validation des donnees), garantit un niveau de conformite adequat pour une preuve de concept.

### 8.2 Recommandations pour la mise en production

| # | Recommandation | Priorite |
|---|---------------|----------|
| 1 | Activer le chiffrement TLS pour PostgreSQL | Haute |
| 2 | Implementer un controle d'acces par roles (RBAC) | Haute |
| 3 | Ajouter des tests de securite automatises (CI/CD) | Moyenne |
| 4 | Mettre en place un DPO (Delegue a la Protection des Donnees) | Moyenne |
| 5 | Realiser une AIPD si extension a des donnees de sondages | Haute |
| 6 | Implementer le chiffrement au repos (encryption at rest) | Moyenne |
| 7 | Politique de rotation des mots de passe | Faible |

---

## Annexe : Checklist de conformite

| # | Point de controle | Statut |
|---|-------------------|--------|
| 1 | Registre des traitements | FAIT (ce document) |
| 2 | Inventaire des donnees personnelles | FAIT (aucune identifiee) |
| 3 | Base legale du traitement | FAIT (donnees publiques, licence Etalab) |
| 4 | Droits des personnes | FAIT (non applicable) |
| 5 | Securite des donnees | FAIT (injection SQL, secrets, Docker) |
| 6 | Notification de violation | NON APPLICABLE (pas de donnees personnelles) |
| 7 | Analyse d'impact (AIPD) | NON REQUISE (pas de donnees sensibles) |
| 8 | DPO designe | NON REQUIS (POC < 250 salaries, pas de donnees sensibles) |
| 9 | Transferts hors UE | AUCUN (donnees hebergees localement) |
| 10 | Sous-traitants | AUCUN (traitement interne uniquement) |
