"""
Point d'entrée principal du module Load ETL v3.0.

Orchestre le chargement séquentiel dans PostgreSQL.

Ordre d'exécution (respect des FK):
1. Géographie (Region → Departement → Commune)
2. Types d'indicateurs (référentiel statique)
3. Candidats & Élections (TypeElection → Election → Candidat → Parti → CandidatParti)
4. Résultats électoraux (ElectionTerritoire → ResultatParticipation → ResultatCandidat)
5. Indicateurs de sécurité (Indicateur polymorphe)

Auteur: @de (Data Engineer)
"""

import sys
from typing import Dict, Any
from datetime import datetime

from .core import (
    run_load_geographie,
    run_load_types_indicateurs,
    run_load_candidats,
    run_load_elections,
    run_load_securite,
)


def print_header():
    """Affiche le header du pipeline Load."""
    print("\n" + "=" * 80)
    print(" " * 20 + "ETL LOAD v3.0 - ELECTIO-ANALYTICS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Cible: PostgreSQL (electio_analytics)")
    print("=" * 80 + "\n")


def print_footer(total_duration: float):
    """Affiche le footer du pipeline Load."""
    print("\n" + "=" * 80)
    print("[OK] PIPELINE LOAD v3.0 TERMINÉ AVEC SUCCÈS")
    print("=" * 80)
    print(f"  Durée totale: {total_duration:.2f} secondes")
    print("=" * 80 + "\n")


def run_load_pipeline() -> Dict[str, Any]:
    """
    Exécute le pipeline complet de chargement des données v3.0.

    Ordre:
        1. Géographie (Region, Departement, Commune)
        2. Types d'indicateurs
        3. Candidats & Élections (TypeElection, Election, Candidat, Parti)
        4. Résultats électoraux (ElectionTerritoire, ResultatParticipation, ResultatCandidat)
        5. Indicateurs de sécurité

    Returns:
        Dictionnaire avec statistiques globales
    """
    start_time = datetime.now()
    print_header()

    results = {}

    try:
        # =====================================================================
        # ÉTAPE 1 : Hiérarchie géographique
        # =====================================================================
        print("\n> ÉTAPE 1/5: Chargement de la hiérarchie géographique...")
        results["geographie"] = run_load_geographie()

        # =====================================================================
        # ÉTAPE 2 : Types d'indicateurs (référentiel statique)
        # =====================================================================
        print("\n> ÉTAPE 2/5: Chargement des types d'indicateurs...")
        results["types_indicateurs"] = run_load_types_indicateurs()

        # =====================================================================
        # ÉTAPE 3 : Candidats & Élections
        # =====================================================================
        print("\n> ÉTAPE 3/5: Chargement des référentiels électoraux...")
        results["candidats"] = run_load_candidats()

        # =====================================================================
        # ÉTAPE 4 : Résultats électoraux
        # =====================================================================
        print("\n> ÉTAPE 4/5: Chargement des résultats électoraux...")
        results["elections"] = run_load_elections()

        # =====================================================================
        # ÉTAPE 5 : Indicateurs de sécurité
        # =====================================================================
        print("\n> ÉTAPE 5/5: Chargement des indicateurs de sécurité...")
        results["securite"] = run_load_securite()

        # =====================================================================
        # RÉSUMÉ
        # =====================================================================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 80)
        print("> RÉSUMÉ DU CHARGEMENT v3.0")
        print("=" * 80)

        total_inserted = 0
        for key, stats in results.items():
            inserted = stats.get("inserted", 0)
            total_inserted += inserted
            print(f"\n  {key.upper()}")
            print(f"    Insérés: {inserted:,}")
            print(f"    Source:  {stats.get('source', 'N/A')}")

        print(f"\n{'=' * 80}")
        print(f"[OK] TOTAL LIGNES INSÉRÉES: {total_inserted:,}")
        print(f"  DURÉE: {duration:.2f}s")
        print(f"{'=' * 80}\n")

        print_footer(duration)

        results["summary"] = {
            "total_inserted": total_inserted,
            "duration_seconds": duration,
            "success": True,
        }

        return results

    except Exception as e:
        print(f"\n  ERREUR FATALE: {e}")
        print(f"  Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

        results["summary"] = {
            "success": False,
            "error": str(e),
        }

        sys.exit(1)


if __name__ == "__main__":
    run_load_pipeline()
