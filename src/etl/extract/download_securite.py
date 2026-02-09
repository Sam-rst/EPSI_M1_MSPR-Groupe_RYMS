"""
Script de téléchargement des données de sécurité (SSMSI) via API data.gouv.fr.

Télécharge la base statistique communale de la délinquance enregistrée :
- Source : Ministère de l'Intérieur (SSMSI)
- Période : 2016-2025
- Granularité : Communale (toutes les communes de France)
- Format : CSV compressé (gzip)
- 13 indicateurs de criminalité

Note: Le fichier sera filtré pour Bordeaux (33063) après téléchargement.

Usage:
    python -m src.etl.extract.download_securite
"""

import gzip
import logging
import shutil
import sys

import pandas as pd

from .api_datagouv import DataGouvAPI
from .config import (
    CODE_COMMUNE,
    CODE_DEPARTEMENT,
    DATA_RAW_SECURITE,
    FICHIER_SECURITE,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration dataset SSMSI
SSMSI_DATASET_ID = "621df2954fa5a3b5a023e23c"


def download_securite() -> bool:
    """
    Télécharge et filtre les données de sécurité pour Bordeaux via API.

    Returns:
        True si succès, False sinon
    """
    logger.info("=" * 80)
    logger.info("TÉLÉCHARGEMENT DES DONNÉES DE SÉCURITÉ (SSMSI) - VIA API")
    logger.info("=" * 80)
    logger.info("Source : Ministère de l'Intérieur via data.gouv.fr")
    logger.info("Niveau : Communal (toutes les communes de France)")
    logger.info(f"Filtrage : Bordeaux (Dép. {CODE_DEPARTEMENT}, Commune {CODE_COMMUNE})")
    logger.info("=" * 80)

    output_path = DATA_RAW_SECURITE / FICHIER_SECURITE

    # Vérifier si le fichier existe déjà
    if output_path.exists():
        logger.warning(f"  >> Fichier existant, ignoré : {output_path.name}")
        return True

    try:
        # Créer le dossier de destination
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialiser l'API client
        api = DataGouvAPI()

        # Récupérer les infos du dataset
        logger.info("Recherche de la ressource communale...")
        dataset_info = api.get_dataset_info(SSMSI_DATASET_ID)

        if not dataset_info:
            logger.error("  >> [ERREUR] Dataset introuvable")
            return False

        # Chercher la ressource "communale" avec extension .csv.gz
        resource = None
        for r in dataset_info.get("resources", []):
            title = r.get("title", "").lower()
            file_format = r.get("format", "").lower()

            if "communal" in title and file_format in ["csv.gz", "csv"]:
                resource = r
                logger.info(f"  >> Ressource trouvée : {r.get('title')}")
                logger.info(f"     Format : {file_format}")
                logger.info(f"     Taille : {r.get('filesize', 0) / 1024 / 1024:.2f} MB")
                break

        if not resource:
            logger.error("  >> [ERREUR] Ressource communale introuvable")
            return False

        # Télécharger le fichier compressé
        temp_file_gz = output_path.parent / "temp_securite.csv.gz"
        temp_file_csv = output_path.parent / "temp_securite.csv"

        logger.info("\nTéléchargement du fichier complet (fichier volumineux)...")
        success = api.download_resource(
            resource["url"],
            temp_file_gz,
            "Données sécurité SSMSI (communal)"
        )

        if not success:
            return False

        # Décompresser le fichier
        logger.info("Décompression du fichier...")
        with gzip.open(temp_file_gz, "rb") as f_in:
            with open(temp_file_csv, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        logger.info("[OK] Fichier décompressé")

        # Filtrage pour Bordeaux uniquement
        logger.info(f"Filtrage des données pour Bordeaux (code {CODE_COMMUNE})...")

        df = pd.read_csv(temp_file_csv, sep=";", encoding="utf-8", low_memory=False)

        logger.info(f"  Lignes totales : {len(df)}")

        # Identifier les colonnes de code géographique
        # Le fichier utilise CODGEO_2025 qui contient le code INSEE commune
        col_codgeo = "CODGEO_2025" if "CODGEO_2025" in df.columns else next(
            (c for c in df.columns if "codgeo" in c.lower()), None
        )

        if not col_codgeo:
            logger.error("  >> [ERREUR] Colonne CODGEO introuvable")
            logger.error(f"     Colonnes disponibles : {list(df.columns[:10])}")
            return False

        # Filtrer par code INSEE commune (33063 = Bordeaux)
        df_bordeaux = df[df[col_codgeo].astype(str).str.strip() == CODE_COMMUNE]

        logger.info(f"  Lignes après filtrage : {len(df_bordeaux)}")

        if len(df_bordeaux) == 0:
            logger.warning("  >> [ATTENTION] Aucune donnée trouvée pour Bordeaux")
            logger.warning("     Vérifier les codes département/commune")
            return False

        # Sauvegarder le fichier filtré
        df_bordeaux.to_csv(output_path, index=False, encoding="utf-8")

        # Supprimer les fichiers temporaires
        temp_file_gz.unlink(missing_ok=True)
        temp_file_csv.unlink(missing_ok=True)

        logger.info(f"\n[OK] Fichier filtré sauvegardé : {output_path}")
        logger.info(f"     Taille finale : {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"[ERREUR] {e}", exc_info=True)
        return False


def main():
    """Point d'entrée principal du script."""
    try:
        success = download_securite()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.warning("\n[INTERROMPU] Téléchargement annulé par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"[ERREUR FATALE] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
