"""
Script de téléchargement des données de sécurité (SSMSI).

Télécharge la base statistique de la délinquance enregistrée :
- Période : 2016-2024
- Granularité : Communale (Bordeaux - 33063)
- 13 indicateurs de criminalité

Usage:
    python -m src.etl.extract.download_securite
"""

import logging
import sys

import pandas as pd
import requests
from tqdm import tqdm

from .config import (
    CODE_COMMUNE,
    CODE_DEPARTEMENT,
    DATA_RAW_SECURITE,
    FICHIER_SECURITE,
    SECURITE_COMMUNALE_URL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def download_securite() -> bool:
    """
    Télécharge et filtre les données de sécurité pour Bordeaux.

    Returns:
        True si succès, False sinon
    """
    logger.info("=" * 70)
    logger.info("TÉLÉCHARGEMENT DES DONNÉES DE SÉCURITÉ (SSMSI)")
    logger.info("=" * 70)
    logger.info("Source : Base statistique de la délinquance enregistrée")
    logger.info(f"Filtrage : Département {CODE_DEPARTEMENT}, Commune {CODE_COMMUNE}")
    logger.info("Période : 2016-2024")
    logger.info("=" * 70)

    output_path = DATA_RAW_SECURITE / FICHIER_SECURITE

    # Vérifier si le fichier existe déjà
    if output_path.exists():
        logger.warning(f"⚠️ Fichier existant : {output_path}")
        logger.warning("   Téléchargement ignoré. Supprimer le fichier pour re-télécharger.")
        return True

    try:
        # Créer le dossier de destination
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Télécharger le fichier complet
        logger.info(f"Téléchargement depuis : {SECURITE_COMMUNALE_URL}")
        logger.info("⚠️ Ce fichier peut être volumineux (plusieurs centaines de MB)")

        response = requests.get(SECURITE_COMMUNALE_URL, stream=True, timeout=120)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        # Téléchargement temporaire
        temp_file = output_path.parent / "temp_securite.csv"

        with open(temp_file, "wb") as f:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc="Téléchargement",
                leave=True,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        logger.info("✅ Téléchargement terminé")

        # Filtrage pour Bordeaux uniquement
        logger.info("Filtrage des données pour Bordeaux...")

        df = pd.read_csv(temp_file, sep=";", encoding="utf-8", low_memory=False)

        # Filtrer par département et commune
        df_bordeaux = df[
            (df["Code.département"].astype(str) == CODE_DEPARTEMENT)
            & (df["Code.commune"].astype(str) == CODE_COMMUNE)
        ]

        # Filtrer par année (2016-2024)
        if "annee" in df_bordeaux.columns:
            df_bordeaux = df_bordeaux[df_bordeaux["annee"] >= 2016]

        logger.info(f"Lignes après filtrage : {len(df_bordeaux)}")

        # Sauvegarder le fichier filtré
        df_bordeaux.to_csv(output_path, index=False, encoding="utf-8")

        # Supprimer le fichier temporaire
        temp_file.unlink()

        logger.info(f"✅ Fichier filtré sauvegardé : {output_path}")
        logger.info("=" * 70)

        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur de téléchargement : {e}")
        return False
    except pd.errors.ParserError as e:
        logger.error(f"❌ Erreur de parsing CSV : {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur inattendue : {e}")
        return False


def main():
    """Point d'entrée principal du script."""
    try:
        success = download_securite()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.warning("\n⚠️ Téléchargement interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Erreur fatale : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
