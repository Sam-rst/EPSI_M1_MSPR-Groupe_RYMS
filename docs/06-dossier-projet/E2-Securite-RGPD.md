# E2 - Securite & Conformite RGPD

> **Competence C9 :** Appliquer les procedures de securite etablies par le/la RSSI afin d'assurer la confidentialite et la securite des donnees et garantir une mise en conformite avec les obligations legales du RGPD.

---

## 1. Classification des donnees

**Verdict : AUCUNE donnee a caractere personnel.**

| Categorie | Granularite | Personnel ? |
|-----------|-------------|------------|
| Resultats electoraux | Commune / Bureau | NON (agrege) |
| Participation | Commune / Bureau | NON (agrege) |
| Candidats | Nom, prenom | NON (personnages publics) |
| Securite (SSMSI) | Commune | NON (statistiques) |
| Predictions ML | Commune | NON (genere) |

Aucun electeur individuel n'est identifiable directement ou indirectement.

## 2. Base legale

- **Article 6.1(e) RGPD** : donnees publiees dans le cadre d'une mission d'interet public
- **Licence ouverte Etalab 2.0** : reutilisation autorisee (y compris commerciale)

## 3. Mesures de securite implementees

### Gestion des secrets

| Mesure | Implementation |
|--------|---------------|
| Credentials en variables d'environnement | `.env` charge via `python-dotenv` |
| `.env` exclu du depot Git | 2 entrees dans `.gitignore` |
| Template fourni | `.env.example` avec valeurs factices |
| Encodage mot de passe | `urllib.parse.quote_plus()` |

### Prevention injection SQL

| Mesure | Implementation |
|--------|---------------|
| ORM SQLAlchemy | Requetes parametrees par defaut |
| Bind parameters | `text("SELECT ... WHERE x = :param")` |
| Validation regex | Nom BDD valide par `^[a-zA-Z_][a-zA-Z0-9_]*$` |

### Infrastructure Docker

| Mesure | Implementation |
|--------|---------------|
| Reseau isole | Bridge network `electio_network` |
| Health checks | `pg_isready` toutes les 10s |
| Init script read-only | Mount `:ro` |
| Volume persistant | `postgres_data` |

## 4. Droits des personnes (non applicables)

| Droit RGPD | Applicabilite |
|------------|---------------|
| Acces (Art. 15) | Non applicable - aucune donnee personnelle |
| Rectification (Art. 16) | Non applicable |
| Effacement (Art. 17) | Non applicable |
| Portabilite (Art. 20) | Non applicable |
| Opposition (Art. 21) | Non applicable |

## 5. Checklist de conformite

| # | Point de controle | Statut |
|---|-------------------|--------|
| 1 | Registre des traitements | FAIT |
| 2 | Inventaire donnees personnelles | FAIT (aucune) |
| 3 | Base legale | FAIT (Etalab 2.0) |
| 4 | Securite des donnees | FAIT |
| 5 | Notification de violation | Non applicable |
| 6 | AIPD | Non requise |
| 7 | DPO | Non requis (POC) |
| 8 | Transferts hors UE | Aucun |

**Fichier de reference :**
- Audit complet : `docs/05-reports/AUDIT_RGPD.md`
