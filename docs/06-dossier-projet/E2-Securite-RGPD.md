# E2 - Sécurité & Conformité RGPD

> **Compétence C9 :** Appliquer les procédures de sécurité établies par le/la RSSI afin d'assurer la confidentialité et la sécurité des données et garantir une mise en conformité avec les obligations légales du RGPD.

---

## 1. Classification des données

**Verdict : AUCUNE donnée à caractère personnel.**

| Catégorie | Granularité | Personnel ? |
|-----------|-------------|------------|
| Résultats électoraux | Commune / Bureau | NON (agrégé) |
| Participation | Commune / Bureau | NON (agrégé) |
| Candidats | Nom, prénom | NON (personnages publics) |
| Sécurité (SSMSI) | Commune | NON (statistiques) |
| Prédictions ML | Commune | NON (généré) |

Aucun électeur individuel n'est identifiable directement ou indirectement.

## 2. Base légale

- **Article 6.1(e) RGPD** : données publiées dans le cadre d'une mission d'intérêt public
- **Licence ouverte Etalab 2.0** : réutilisation autorisée (y compris commerciale)

## 3. Mesures de sécurité implémentées

### Gestion des secrets

| Mesure | Implémentation |
|--------|---------------|
| Credentials en variables d'environnement | `.env` chargé via `python-dotenv` |
| `.env` exclu du dépôt Git | 2 entrées dans `.gitignore` |
| Template fourni | `.env.example` avec valeurs factices |
| Encodage mot de passe | `urllib.parse.quote_plus()` |

### Prévention injection SQL

| Mesure | Implémentation |
|--------|---------------|
| ORM SQLAlchemy | Requêtes paramétrées par défaut |
| Bind parameters | `text("SELECT ... WHERE x = :param")` |
| Validation regex | Nom BDD validé par `^[a-zA-Z_][a-zA-Z0-9_]*$` |

### Infrastructure Docker

| Mesure | Implémentation |
|--------|---------------|
| Réseau isolé | Bridge network `electio_network` |
| Health checks | `pg_isready` toutes les 10s |
| Init script read-only | Mount `:ro` |
| Volume persistant | `postgres_data` |

## 4. Droits des personnes (non applicables)

| Droit RGPD | Applicabilité |
|------------|---------------|
| Accès (Art. 15) | Non applicable - aucune donnée personnelle |
| Rectification (Art. 16) | Non applicable |
| Effacement (Art. 17) | Non applicable |
| Portabilité (Art. 20) | Non applicable |
| Opposition (Art. 21) | Non applicable |

## 5. Checklist de conformité

| # | Point de contrôle | Statut |
|---|-------------------|--------|
| 1 | Registre des traitements | FAIT |
| 2 | Inventaire données personnelles | FAIT (aucune) |
| 3 | Base légale | FAIT (Etalab 2.0) |
| 4 | Sécurité des données | FAIT |
| 5 | Notification de violation | Non applicable |
| 6 | AIPD | Non requise |
| 7 | DPO | Non requis (POC) |
| 8 | Transferts hors UE | Aucun |

**Fichier de référence :**
- Audit complet : `docs/05-reports/AUDIT_RGPD.md`
