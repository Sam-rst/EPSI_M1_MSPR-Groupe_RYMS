"""
Pipeline ETL Complet v3.0 - Electio-Analytics

Orchestre les 3 phases du pipeline ETL:
1. Extract  : Téléchargement données brutes (API + fichiers)
2. Transform: Transformation et nettoyage
3. Load     : Chargement dans PostgreSQL (schéma v3.0)

Usage:
    python -m src.etl.main

Auteur: @de (Data Engineer)
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple


def print_header():
    """Affiche le header du pipeline."""
    print("\n" + "=" * 80)
    print(" " * 25 + "PIPELINE ETL v3.0")
    print(" " * 20 + "ELECTIO-ANALYTICS - GIRONDE")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Perimetre: Gironde (33) - ~535 communes")
    print(f"Donnees: Elections 2017/2022 + Securite SSMSI")
    print(f"Schema: v3.0 (19 tables)")
    print("=" * 80 + "\n")


def print_step_header(phase: str, number: int, total: int):
    """Affiche le header d'une phase."""
    print("\n" + "=" * 80)
    print(f"PHASE {number}/{total}: {phase}")
    print("=" * 80 + "\n")


def check_prerequisites() -> Tuple[bool, Dict[str, Any]]:
    """Vérifie les prérequis avant de lancer le pipeline."""
    print_step_header("VÉRIFICATION PRÉREQUIS", 0, 3)

    details = {}
    all_ok = True

    # 1. PostgreSQL
    print("> Vérification PostgreSQL...")
    try:
        from src.database.config import get_engine
        from sqlalchemy import text

        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"  [OK] PostgreSQL connecté")
            print(f"  Version: {version.split(',')[0]}")
            details["postgres"] = True
    except Exception as e:
        print(f"  [ERREUR] PostgreSQL non disponible: {e}")
        print("\n  Solution: docker-compose up -d")
        details["postgres"] = False
        all_ok = False

    # 2. Tables v3.0
    if details.get("postgres"):
        print("\n> Vérification tables v3.0...")
        try:
            required_tables = [
                'region', 'departement', 'commune',
                'type_election', 'election', 'election_territoire',
                'candidat', 'parti', 'candidat_parti',
                'resultat_participation', 'resultat_candidat',
                'type_indicateur', 'indicateur',
            ]
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public'"
                ))
                existing_tables = {row[0] for row in result}

            missing = [t for t in required_tables if t not in existing_tables]
            if not missing:
                print(f"  [OK] {len(required_tables)} tables requises trouvées")
                details["tables"] = True
            else:
                print(f"  [WARN] Tables manquantes: {missing}")
                print("\n  Solution: cd src/database && alembic upgrade head")
                details["tables"] = False
                all_ok = False
        except Exception as e:
            print(f"  [ERREUR] Vérification tables: {e}")
            details["tables"] = False
            all_ok = False

    # 3. Structure dossiers
    print("\n> Vérification structure dossiers...")
    required_dirs = [
        Path("data/raw/elections"),
        Path("data/raw/securite"),
        Path("data/raw/geographie"),
        Path("data/processed/elections"),
        Path("data/processed/indicateurs"),
        Path("data/processed/geographie"),
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not dir_path.exists():
            missing_dirs.append(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)

    if missing_dirs:
        print(f"  [INFO] {len(missing_dirs)} dossiers créés")
    else:
        print("  [OK] Tous les dossiers existent")

    details["directories"] = True

    return all_ok, details


def run_extract() -> Tuple[bool, Dict[str, Any]]:
    """Exécute la phase Extract."""
    print_step_header("EXTRACT - Téléchargement données", 1, 3)

    try:
        from src.etl.extract.main import main as extract_main

        print("> Lancement extraction données (v3.0)...")
        success = extract_main()

        stats = {"success": success}
        if success:
            print("\n  [OK] Extraction terminée")
        else:
            print("\n  [WARN] Extraction avec avertissements")

        return success, stats

    except Exception as e:
        print(f"\n  [ERREUR] Erreur Extract: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def run_transform() -> Tuple[bool, Dict[str, Any]]:
    """Exécute la phase Transform."""
    print_step_header("TRANSFORM - Transformation données", 2, 3)

    stats = {}

    try:
        from src.etl.transform.main import main as transform_main
        import pandas as pd

        print("> Lancement transformation données (v3.0)...")
        success = transform_main()

        # Vérifier outputs
        geo_outputs = [
            Path("data/processed/geographie/regions.csv"),
            Path("data/processed/geographie/departements.csv"),
            Path("data/processed/geographie/communes.csv"),
        ]
        for f in geo_outputs:
            if f.exists():
                df = pd.read_csv(f)
                stats[f.stem] = len(df)
                print(f"  [OK] {f.stem}: {len(df)} lignes")

        elections_outputs = [
            Path("data/processed/elections/participation_gironde.csv"),
            Path("data/processed/elections/candidats_gironde.csv"),
        ]
        for f in elections_outputs:
            if f.exists():
                df = pd.read_csv(f)
                stats[f.stem] = len(df)
                print(f"  [OK] {f.stem}: {len(df)} lignes")

        securite_csv = Path("data/processed/indicateurs/delinquance_bordeaux.csv")
        if securite_csv.exists():
            df = pd.read_csv(securite_csv)
            stats["securite_rows"] = len(df)
            print(f"  [OK] Securite: {len(df)} lignes")

        return success, stats

    except Exception as e:
        print(f"  [ERREUR] Erreur Transform: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def run_load() -> Tuple[bool, Dict[str, Any]]:
    """Exécute la phase Load."""
    print_step_header("LOAD - Chargement PostgreSQL", 3, 3)

    try:
        from src.etl.load import run_load_pipeline

        results = run_load_pipeline()
        summary = results.get("summary", {})
        success = summary.get("success", False)

        stats = {
            "total_inserted": summary.get("total_inserted", 0),
            "duration": summary.get("duration_seconds", 0),
        }

        if success:
            print(f"\n  [OK] Load terminé: {stats['total_inserted']} lignes insérées")
            return True, stats
        else:
            print("\n  [ERREUR] Load échoué")
            return False, stats

    except Exception as e:
        print(f"\n  [ERREUR] Erreur Load: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def validate_results() -> Tuple[bool, Dict[str, Any]]:
    """Valide les résultats finaux dans PostgreSQL."""
    print("\n" + "=" * 80)
    print("VALIDATION FINALE")
    print("=" * 80 + "\n")

    details = {}
    all_ok = True

    try:
        from src.database.config import get_engine
        from sqlalchemy import text

        engine = get_engine()

        tables_to_check = [
            ("region", "Régions"),
            ("departement", "Départements"),
            ("commune", "Communes"),
            ("type_election", "Types d'élection"),
            ("election", "Élections"),
            ("candidat", "Candidats"),
            ("parti", "Partis"),
            ("candidat_parti", "Affiliations"),
            ("election_territoire", "Élection-Territoire"),
            ("resultat_participation", "Participations"),
            ("resultat_candidat", "Résultats candidats"),
            ("type_indicateur", "Types indicateurs"),
            ("indicateur", "Indicateurs"),
        ]

        # Whitelist des tables autorisées pour validation
        allowed_tables = {t for t, _ in tables_to_check}

        for table_name, label in tables_to_check:
            if table_name not in allowed_tables:
                continue
            try:
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT COUNT(*) FROM information_schema.tables "
                             "WHERE table_schema = 'public' AND table_name = :tbl"),
                        {"tbl": table_name},
                    )
                    exists = result.fetchone()[0] > 0
                    if exists:
                        count_result = conn.execute(
                            text(f'SELECT COUNT(*) FROM "{table_name}"')
                        )
                        count = count_result.fetchone()[0]
                    else:
                        count = 0
                    details[table_name] = count
                    status = "[OK]" if count > 0 else "[WARN]"
                    print(f"  {status} {label}: {count:,}")
            except Exception:
                details[table_name] = 0
                print(f"  [ERREUR] {label}: table introuvable")
                all_ok = False

        # Détail élections par année/tour
        print("\n  Détail résultats par élection:")
        try:
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT e.annee, rp.tour, COUNT(*) AS nb "
                    "FROM resultat_participation rp "
                    "JOIN election e ON rp.id_election = e.id_election "
                    "GROUP BY e.annee, rp.tour "
                    "ORDER BY e.annee, rp.tour"
                ))
                for row in result:
                    print(f"    - {row[0]} Tour {row[1]}: {row[2]} territoires")
        except Exception as e:
            print(f"  [WARN] Détail résultats indisponible: {e}")

        return all_ok, details

    except Exception as e:
        print(f"\n  [ERREUR] Erreur validation: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def print_summary(
    prereqs_ok: bool,
    extract_ok: bool,
    transform_ok: bool,
    load_ok: bool,
    validate_ok: bool,
    extract_stats: Dict[str, Any],
    transform_stats: Dict[str, Any],
    load_stats: Dict[str, Any],
    validate_details: Dict[str, Any],
    total_duration: float,
):
    """Affiche le résumé final."""
    print("\n" + "=" * 80)
    print(" " * 30 + "RÉSUMÉ FINAL")
    print("=" * 80 + "\n")

    phases = [
        ("Prérequis", prereqs_ok),
        ("Extract", extract_ok),
        ("Transform", transform_ok),
        ("Load", load_ok),
        ("Validation", validate_ok),
    ]

    print("> STATUT DES PHASES\n")
    for phase_name, success in phases:
        status = "[OK]" if success else "[ERREUR]"
        print(f"   {status} {phase_name}")

    if validate_details:
        print(f"\n> BASE DE DONNÉES v3.0\n")
        for table, count in validate_details.items():
            print(f"   {table}: {count:,}")

    print(f"\n  Durée totale: {total_duration:.2f}s")

    print("\n" + "=" * 80)
    if all([prereqs_ok, extract_ok, transform_ok, load_ok, validate_ok]):
        print("[OK] PIPELINE ETL v3.0 TERMINÉ AVEC SUCCÈS")
    else:
        print("[ERREUR] PIPELINE ETL v3.0 ÉCHOUÉ")
    print("=" * 80 + "\n")


def main():
    """Point d'entrée principal."""
    start_time = datetime.now()

    print_header()

    extract_stats = {}
    transform_stats = {}
    load_stats = {}
    validate_details = {}

    # 0. Prérequis
    prereqs_ok, prereq_details = check_prerequisites()

    if not prereqs_ok:
        print("\n  [ERREUR] Prérequis non satisfaits. Arrêt du pipeline.")
        print("\n  Vérifiez:")
        print("   1. PostgreSQL démarré: docker-compose up -d")
        print("   2. Migrations appliquées: cd src/database && alembic upgrade head")
        return 1

    # 1. Extract
    extract_ok, extract_stats = run_extract()
    if not extract_ok:
        print("\n  [ERREUR] Extract échoué. Arrêt du pipeline.")
        return 1

    # 2. Transform
    transform_ok, transform_stats = run_transform()
    if not transform_ok:
        print("\n  [ERREUR] Transform échoué. Arrêt du pipeline.")
        return 1

    # 3. Load
    load_ok, load_stats = run_load()
    if not load_ok:
        print("\n  [ERREUR] Load échoué. Arrêt du pipeline.")
        return 1

    # 4. Validation
    validate_ok, validate_details = validate_results()

    # Durée totale
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # Résumé
    print_summary(
        prereqs_ok,
        extract_ok,
        transform_ok,
        load_ok,
        validate_ok,
        extract_stats,
        transform_stats,
        load_stats,
        validate_details,
        total_duration,
    )

    if all([prereqs_ok, extract_ok, transform_ok, load_ok, validate_ok]):
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
