"""
Pipeline ETL Complet - Electio-Analytics

Orchestre les 3 phases du pipeline ETL :
1. Extract  : Téléchargement données brutes
2. Transform: Transformation et nettoyage
3. Load     : Chargement dans PostgreSQL

Vérifie chaque étape et affiche un rapport détaillé.

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)

Usage:
    python -m src.etl.main
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple


def print_header():
    """Affiche le header du pipeline."""
    print("\n" + "=" * 80)
    print(" " * 25 + "PIPELINE ETL COMPLET")
    print(" " * 20 + "ELECTIO-ANALYTICS - BORDEAUX")
    print("=" * 80)
    print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Perimetre : Bordeaux (33063)")
    print(f"Donnees : Elections 2017/2022 + Securite SSMSI")
    print("=" * 80 + "\n")


def print_step_header(phase: str, number: int, total: int):
    """Affiche le header d'une phase."""
    print("\n" + "=" * 80)
    print(f"PHASE {number}/{total} : {phase}")
    print("=" * 80 + "\n")


def check_prerequisites() -> Tuple[bool, Dict[str, Any]]:
    """
    Vérifie les prérequis avant de lancer le pipeline.

    Returns:
        (success, details)
    """
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
            print(f"[OK] PostgreSQL connecté")
            print(f"   Version : {version.split(',')[0]}")
            details["postgres"] = True
    except Exception as e:
        print(f"[ERREUR] PostgreSQL non disponible : {e}")
        print("\n[INFO] Solution :")
        print("   docker-compose up -d")
        details["postgres"] = False
        all_ok = False

    # 2. Tables Alembic
    if details.get("postgres"):
        print("\n> Vérification tables...")
        try:
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name IN "
                    "('territoire', 'type_indicateur', 'indicateur', 'election_result')"
                ))
                count = result.fetchone()[0]

                if count == 4:
                    print(f"[OK] {count}/4 tables créées")
                    details["tables"] = True
                else:
                    print(f"[WARN]  {count}/4 tables créées")
                    print("\n[INFO] Solution :")
                    print("   cd src/database && alembic upgrade head")
                    details["tables"] = False
                    all_ok = False
        except Exception as e:
            print(f"[ERREUR] Erreur vérification tables : {e}")
            details["tables"] = False
            all_ok = False

    # 3. Structure dossiers
    print("\n> Vérification structure dossiers...")
    required_dirs = [
        Path("data/raw/elections"),
        Path("data/raw/securite"),
        Path("data/processed/elections"),
        Path("data/processed/indicateurs"),
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not dir_path.exists():
            missing_dirs.append(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)

    if missing_dirs:
        print(f"[WARN]  {len(missing_dirs)} dossiers créés")
    else:
        print("[OK] Tous les dossiers existent")

    details["directories"] = True

    return all_ok, details


def run_extract() -> Tuple[bool, Dict[str, Any]]:
    """
    Exécute la phase Extract.

    Returns:
        (success, stats)
    """
    print_step_header("EXTRACT - Téléchargement données", 1, 3)

    try:
        from src.etl.extract.main import main as extract_main

        print("> Lancement extraction données...")
        success = extract_main()

        # Vérifier les résultats
        stats = {"success": success}

        if success:
            print("\n[OK] Extraction terminée")
        else:
            print("\n[WARN] Extraction avec avertissements")

        return True, stats  # Toujours retourner True si pas d'exception

    except Exception as e:
        print(f"\n[ERREUR] Erreur Extract : {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def run_transform() -> Tuple[bool, Dict[str, Any]]:
    """
    Exécute la phase Transform.

    Returns:
        (success, stats)
    """
    print_step_header("TRANSFORM - Transformation données", 2, 3)

    stats = {}

    try:
        from src.etl.transform.main import main as transform_main
        import pandas as pd

        print("> Lancement transformation données...")
        success = transform_main()

        # Vérifier outputs
        elections_csv = Path("data/processed/elections/resultats_elections_bordeaux.csv")
        securite_csv = Path("data/processed/indicateurs/delinquance_bordeaux.csv")

        if elections_csv.exists():
            df = pd.read_csv(elections_csv)
            stats["elections_rows"] = len(df)
            print(f"[OK] Elections: {len(df)} lignes")

        if securite_csv.exists():
            df = pd.read_csv(securite_csv)
            stats["securite_rows"] = len(df)
            print(f"[OK] Securite: {len(df)} lignes")

        return True, stats

    except Exception as e:
        print(f"[ERREUR] Erreur Transform : {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def run_load() -> Tuple[bool, Dict[str, Any]]:
    """
    Exécute la phase Load.

    Returns:
        (success, stats)
    """
    print_step_header("LOAD - Chargement PostgreSQL", 3, 3)

    try:
        from src.etl.load import run_load_pipeline

        results = run_load_pipeline()

        # Extraire statistiques
        summary = results.get("summary", {})
        success = summary.get("success", False)

        stats = {
            "total_inserted": summary.get("total_inserted", 0),
            "duration": summary.get("duration_seconds", 0),
        }

        if success:
            print(f"\n[OK] Load terminé : {stats['total_inserted']} lignes insérées")
            return True, stats
        else:
            print("\n[ERREUR] Load échoué")
            return False, stats

    except Exception as e:
        print(f"\n[ERREUR] Erreur Load : {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def validate_results() -> Tuple[bool, Dict[str, Any]]:
    """
    Valide les résultats finaux dans PostgreSQL.

    Returns:
        (success, details)
    """
    print("\n" + "=" * 80)
    print("VALIDATION FINALE")
    print("=" * 80 + "\n")

    details = {}
    all_ok = True

    try:
        from src.database.config import get_engine
        from sqlalchemy import text

        engine = get_engine()

        # 1. Types d'indicateurs
        print("> Types d'indicateurs...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM type_indicateur"))
            count = result.fetchone()[0]
            details["types_indicateurs"] = count
            print(f"   [OK] {count} types")

        # 2. Territoires
        print("\n>  Territoires...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM territoire"))
            count = result.fetchone()[0]
            details["territoires"] = count
            print(f"   [OK] {count} territoire(s)")

        # 3. Résultats électoraux
        print("\n>  Résultats électoraux...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM election_result"))
            count = result.fetchone()[0]
            details["election_results"] = count

            if count > 0:
                print(f"   [OK] {count} résultats")

                # Détail par année/tour
                result = conn.execute(text(
                    "SELECT annee, tour, COUNT(*) AS nb "
                    "FROM election_result "
                    "GROUP BY annee, tour "
                    "ORDER BY annee, tour"
                ))
                for row in result:
                    print(f"      - {row[0]} Tour {row[1]} : {row[2]} candidats")
            else:
                print(f"   [WARN]  Aucun résultat")
                all_ok = False

        # 4. Indicateurs
        print("\n> Indicateurs...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM indicateur"))
            count = result.fetchone()[0]
            details["indicateurs"] = count

            if count > 0:
                print(f"   [OK] {count} indicateurs")

                # Détail par type
                result = conn.execute(text(
                    "SELECT ti.code_type, COUNT(*) AS nb "
                    "FROM indicateur i "
                    "JOIN type_indicateur ti ON i.id_type = ti.id_type "
                    "GROUP BY ti.code_type "
                    "ORDER BY ti.code_type"
                ))
                for row in result:
                    print(f"      - {row[0]} : {row[1]} mesures")
            else:
                print(f"   [WARN]  Aucun indicateur")
                all_ok = False

        return all_ok, details

    except Exception as e:
        print(f"\n[ERREUR] Erreur validation : {e}")
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

    # Statut des phases
    phases = [
        ("Prérequis", prereqs_ok),
        ("Extract", extract_ok),
        ("Transform", transform_ok),
        ("Load", load_ok),
        ("Validation", validate_ok),
    ]

    print("> STATUT DES PHASES\n")
    for phase_name, success in phases:
        status = "[OK] PASS" if success else "[ERREUR] FAIL"
        print(f"   {status} - {phase_name}")

    # Statistiques
    print("\n📈 STATISTIQUES\n")

    if extract_stats:
        print(f"   Extract  : {extract_stats.get('total', 0)} fichier(s) téléchargé(s)")

    if transform_stats:
        elections_rows = transform_stats.get("elections_rows", 0)
        securite_rows = transform_stats.get("securite_rows", 0)
        print(f"   Transform: {elections_rows} élections, {securite_rows} indicateurs")

    if load_stats:
        print(f"   Load     : {load_stats.get('total_inserted', 0)} lignes insérées")

    if validate_details:
        print(f"\n   Base de données finale :")
        print(f"      - Types indicateurs : {validate_details.get('types_indicateurs', 0)}")
        print(f"      - Territoires       : {validate_details.get('territoires', 0)}")
        print(f"      - Résultats élect.  : {validate_details.get('election_results', 0)}")
        print(f"      - Indicateurs       : {validate_details.get('indicateurs', 0)}")

    # Durée totale
    print(f"\n⏱️  Durée totale : {total_duration:.2f}s")

    # Résultat global
    print("\n" + "=" * 80)
    if all([prereqs_ok, extract_ok, transform_ok, load_ok, validate_ok]):
        print("[OK] PIPELINE ETL TERMINÉ AVEC SUCCÈS")
    else:
        print("[ERREUR] PIPELINE ETL ÉCHOUÉ")
    print("=" * 80 + "\n")


def main():
    """Point d'entrée principal."""
    start_time = datetime.now()

    print_header()

    # Variables pour le résumé
    extract_stats = {}
    transform_stats = {}
    load_stats = {}
    validate_details = {}

    # 0. Vérification prérequis
    prereqs_ok, prereq_details = check_prerequisites()

    if not prereqs_ok:
        print("\n[ERREUR] Prérequis non satisfaits. Arrêt du pipeline.")
        print("\n[INFO] Vérifiez :")
        print("   1. PostgreSQL démarré : docker-compose up -d")
        print("   2. Migrations appliquées : cd src/database && alembic upgrade head")
        return 1

    # 1. Extract
    extract_ok, extract_stats = run_extract()

    if not extract_ok:
        print("\n[ERREUR] Extract échoué. Arrêt du pipeline.")
        return 1

    # 2. Transform
    transform_ok, transform_stats = run_transform()

    if not transform_ok:
        print("\n[ERREUR] Transform échoué. Arrêt du pipeline.")
        return 1

    # 3. Load
    load_ok, load_stats = run_load()

    if not load_ok:
        print("\n[ERREUR] Load échoué. Arrêt du pipeline.")
        return 1

    # 4. Validation finale
    validate_ok, validate_details = validate_results()

    # Calcul durée totale
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # Résumé final
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

    # Code de sortie
    if all([prereqs_ok, extract_ok, transform_ok, load_ok, validate_ok]):
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
