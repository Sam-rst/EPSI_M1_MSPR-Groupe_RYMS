"""
Point d'entrée principal du module Load ETL.

Orchestre le chargement séquentiel de toutes les données transformées
dans PostgreSQL.

Ordre d'exécution :
1. Types d'indicateurs (référentiel)
2. Territoires (Bordeaux)
3. Résultats électoraux
4. Indicateurs socio-économiques

Auteur: @de (Data Engineer)
Supervisé par: @tech (Tech Lead)
"""

import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Imports locaux
from .core import (
    run_load_types_indicateurs,
    run_load_territoire,
    run_load_elections,
    run_load_securite,
)


def print_header():
    """Affiche le header du pipeline Load."""
    print("\n" + "=" * 80)
    print(" " * 20 + "ETL LOAD - ELECTIO-ANALYTICS")
    print("=" * 80)
    print(f"Date Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Cible Cible : PostgreSQL (electio_analytics)")
    print("=" * 80 + "\n")


def print_footer(total_duration: float):
    """Affiche le footer du pipeline Load."""
    print("\n" + "=" * 80)
    print("[OK] PIPELINE LOAD TERMINÉ AVEC SUCCÈS")
    print("=" * 80)
    print(f"[TIME]  Durée totale : {total_duration:.2f} secondes")
    print("=" * 80 + "\n")


def run_load_pipeline() -> Dict[str, Any]:
    """
    Exécute le pipeline complet de chargement des données.

    Returns:
        Dictionnaire avec statistiques globales

    Raises:
        Exception: Si une étape échoue
    """
    start_time = datetime.now()
    print_header()

    results = {}

    try:
        # =====================================================================
        # ÉTAPE 1 : Types d'indicateurs (référentiel statique)
        # =====================================================================
        print("\n> ÉTAPE 1/4 : Chargement des types d'indicateurs...")
        results["types_indicateurs"] = run_load_types_indicateurs()

        # =====================================================================
        # ÉTAPE 2 : Territoire Bordeaux
        # =====================================================================
        print("\n>  ÉTAPE 2/4 : Chargement du territoire...")
        results["territoire"] = run_load_territoire()

        # =====================================================================
        # ÉTAPE 3 : Résultats électoraux
        # =====================================================================
        print("\n>  ÉTAPE 3/4 : Chargement des résultats électoraux...")
        results["elections"] = run_load_elections()

        # =====================================================================
        # ÉTAPE 4 : Indicateurs de sécurité
        # =====================================================================
        print("\n> ÉTAPE 4/4 : Chargement des indicateurs de sécurité...")
        results["securite"] = run_load_securite()

        # =====================================================================
        # RÉSUMÉ GLOBAL
        # =====================================================================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 80)
        print("> RÉSUMÉ DU CHARGEMENT")
        print("=" * 80)

        total_inserted = 0

        for key, stats in results.items():
            inserted = stats.get("inserted", 0)
            total_inserted += inserted
            print(f"\n{key.upper()}")
            print(f"  - Insérés : {inserted:,}")
            print(f"  - Source : {stats.get('source', 'N/A')}")

        print(f"\n{'=' * 80}")
        print(f"[OK] TOTAL LIGNES INSÉRÉES : {total_inserted:,}")
        print(f"[TIME]  DURÉE : {duration:.2f}s")
        print(f"{'=' * 80}\n")

        print_footer(duration)

        results["summary"] = {
            "total_inserted": total_inserted,
            "duration_seconds": duration,
            "success": True,
        }

        return results

    except Exception as e:
        print(f"\n ERREUR FATALE : {e}")
        print(f"Type : {type(e).__name__}")
        import traceback
        traceback.print_exc()

        results["summary"] = {
            "success": False,
            "error": str(e),
        }

        sys.exit(1)


if __name__ == "__main__":
    run_load_pipeline()
