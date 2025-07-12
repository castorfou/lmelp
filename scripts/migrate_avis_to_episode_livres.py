#!/usr/bin/env python3
"""
Script de migration one-shot des avis critiques existants vers la collection episode_livres.

Ce script :
1. Parcourt tous les épisodes existants
2. Extrait les livres/auteurs via AvisCritiquesParser
3. Crée/met à jour les documents EpisodeLivre
4. Valide la migration avec rapports détaillés
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Ajout du répertoire nbs au path pour imports
nbs_path = Path(__file__).parent.parent / "nbs"
sys.path.insert(0, str(nbs_path))

from avis_critiques_parser import AvisCritiquesParser
from mongo_episode_livre import EpisodeLivre
from mongo_episode import Episode, Episodes
import mongo


@dataclass
class MigrationStats:
    episodes_traites: int = 0
    episodes_avec_avis: int = 0
    livres_extraits: int = 0
    documents_crees: int = 0
    documents_mis_a_jour: int = 0
    erreurs: int = 0
    erreurs_details: List[str] = None

    def __post_init__(self):
        if self.erreurs_details is None:
            self.erreurs_details = []


class MigrationAvisToEpisodeLivres:
    """Gestionnaire de migration des avis critiques vers episode_livres"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.parser = AvisCritiquesParser()
        self.stats = MigrationStats()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Configuration du logging pour la migration"""
        logger = logging.getLogger("migration_avis")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # Handler console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Handler fichier
            log_file = (
                Path(__file__).parent
                / f"migration_avis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)

            # Format
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger

    def migrate_all_episodes(self, limit: Optional[int] = None) -> MigrationStats:
        """Migration principale de tous les épisodes"""
        self.logger.info(f"Début migration (dry_run={self.dry_run}, limit={limit})")

        try:
            # Récupération des épisodes via Episodes
            episodes_manager = Episodes()
            episodes_manager.get_entries(limit=limit if limit else -1)

            # Conversion des OIDs en instances Episode
            episodes = []
            for oid in episodes_manager.oid_episodes:
                try:
                    episode = Episode.from_oid(oid)
                    episodes.append(episode)
                except Exception as e:
                    self.logger.warning(f"Impossible de charger épisode {oid}: {e}")

            self.logger.info(f"Trouvé {len(episodes)} épisodes à traiter")

            for i, episode in enumerate(episodes, 1):
                if i % 100 == 0:
                    self.logger.info(
                        f"Progression: {i}/{len(episodes)} épisodes traités"
                    )

                self._migrate_episode(episode)

            self._log_final_stats()
            return self.stats

        except Exception as e:
            self.logger.error(f"Erreur fatale migration: {e}")
            self.stats.erreurs += 1
            self.stats.erreurs_details.append(f"Erreur fatale: {e}")
            raise

    def _migrate_episode(self, episode: Episode) -> None:
        """Migration d'un épisode spécifique"""
        try:
            self.stats.episodes_traites += 1
            episode_id = episode.get_oid()

            # Vérification présence avis critiques
            avis_critiques = getattr(episode, "avis_critiques", None)
            if (
                not avis_critiques
                or not isinstance(avis_critiques, str)
                or len(avis_critiques.strip()) < 50
            ):
                return  # Pas d'avis ou trop court

            self.stats.episodes_avec_avis += 1

            # Extraction des livres via parser
            livres = self.parser.extraire_livres_auteurs(avis_critiques)
            if not livres:
                return  # Aucun livre extrait

            self.stats.livres_extraits += len(livres)

            # Création/mise à jour des documents EpisodeLivre
            for livre_data in livres:
                self._create_or_update_episode_livre(episode, livre_data)

        except Exception as e:
            self.stats.erreurs += 1
            error_msg = f"Erreur épisode {getattr(episode, 'titre', 'unknown')}: {e}"
            self.stats.erreurs_details.append(error_msg)
            self.logger.error(error_msg)

    def _create_or_update_episode_livre(
        self, episode: Episode, livre_data: Dict
    ) -> None:
        """Création ou mise à jour d'un document EpisodeLivre"""
        try:
            episode_id = episode.get_oid()

            # Recherche document existant
            existing = EpisodeLivre.find_by_episode_and_book(
                episode_id=episode_id,
                livre=livre_data.get("livre", ""),
                auteur=livre_data.get("auteur", ""),
            )

            if existing:
                # Mise à jour
                if not self.dry_run:
                    updated = self._update_episode_livre(existing, episode, livre_data)
                    if updated:
                        self.stats.documents_mis_a_jour += 1
            else:
                # Création nouveau document
                if not self.dry_run:
                    self._create_new_episode_livre(episode, livre_data)
                self.stats.documents_crees += 1

        except Exception as e:
            self.stats.erreurs += 1
            error_msg = f"Erreur création/MAJ EpisodeLivre: {e}"
            self.stats.erreurs_details.append(error_msg)
            self.logger.error(error_msg)

    def _create_new_episode_livre(self, episode: Episode, livre_data: Dict) -> None:
        """Création d'un nouveau document EpisodeLivre"""
        episode_livre = EpisodeLivre()

        # Données épisode
        episode_livre.set_field("episode_id", episode.get_oid())
        episode_livre.set_field("emission", getattr(episode, "emission", ""))
        episode_livre.set_field("date_diffusion", getattr(episode, "date", None))
        episode_livre.set_field("titre_episode", getattr(episode, "titre", ""))
        episode_livre.set_field(
            "url_episode", getattr(episode, "url_telechargement", "")
        )

        # Données livre
        episode_livre.set_field("livre", livre_data.get("livre", ""))
        episode_livre.set_field("auteur", livre_data.get("auteur", ""))
        episode_livre.set_field("type_oeuvre", livre_data.get("type", "livre"))
        episode_livre.set_field("avis_critique", livre_data.get("avis", ""))

        # Métadonnées migration
        episode_livre.set_field("migration_source", "avis_critiques_parser")
        episode_livre.set_field("migration_date", datetime.now())
        episode_livre.set_field("migration_version", "1.0")

        # Sauvegarde
        episode_livre.save()

        self.logger.debug(
            f"Créé EpisodeLivre: {livre_data.get('livre')} - {livre_data.get('auteur')}"
        )

    def _update_episode_livre(
        self, existing: EpisodeLivre, episode: Episode, livre_data: Dict
    ) -> bool:
        """Mise à jour d'un document EpisodeLivre existant"""
        updated = False

        # Vérification si mise à jour nécessaire
        current_avis = existing.get_field("avis_critique", "")
        new_avis = livre_data.get("avis", "")

        if current_avis != new_avis:
            existing.set_field("avis_critique", new_avis)
            existing.set_field("migration_date", datetime.now())
            existing.save()
            updated = True
            self.logger.debug(f"MAJ EpisodeLivre: {livre_data.get('livre')}")

        return updated

    def _log_final_stats(self) -> None:
        """Affichage des statistiques finales"""
        self.logger.info("=" * 60)
        self.logger.info("STATISTIQUES MIGRATION")
        self.logger.info("=" * 60)
        self.logger.info(f"Épisodes traités: {self.stats.episodes_traites}")
        self.logger.info(f"Épisodes avec avis: {self.stats.episodes_avec_avis}")
        self.logger.info(f"Livres extraits: {self.stats.livres_extraits}")
        self.logger.info(f"Documents créés: {self.stats.documents_crees}")
        self.logger.info(f"Documents mis à jour: {self.stats.documents_mis_a_jour}")
        self.logger.info(f"Erreurs: {self.stats.erreurs}")

        if self.stats.erreurs_details:
            self.logger.info("\nDÉTAILS ERREURS:")
            for error in self.stats.erreurs_details[:10]:  # Limite à 10 erreurs
                self.logger.info(f"  - {error}")
            if len(self.stats.erreurs_details) > 10:
                self.logger.info(
                    f"  ... et {len(self.stats.erreurs_details) - 10} autres erreurs"
                )

    def validate_migration(self) -> Dict[str, any]:
        """Validation de la migration avec contrôles qualité"""
        self.logger.info("Validation de la migration...")

        validation = {
            "total_episode_livres": 0,
            "episodes_uniques": 0,
            "livres_uniques": 0,
            "auteurs_uniques": 0,
            "coherence_ok": True,
            "exemples": [],
        }

        try:
            # Accès direct à la collection MongoDB
            from mongo import get_DB_VARS, get_collection

            DB_HOST, DB_NAME, _ = get_DB_VARS()
            collection = get_collection(
                target_db=DB_HOST, client_name=DB_NAME, collection_name="episode_livres"
            )

            # Comptages
            validation["total_episode_livres"] = collection.count_documents({})

            # Episodes uniques
            episodes_uniques = collection.distinct("episode_id")
            validation["episodes_uniques"] = len(episodes_uniques)

            # Livres uniques
            livres_uniques = collection.distinct("livre_titre")
            validation["livres_uniques"] = len(livres_uniques)

            # Auteurs uniques
            auteurs_uniques = collection.distinct("auteur_nom")
            validation["auteurs_uniques"] = len(auteurs_uniques)

            # Exemples récents
            exemples_cursor = collection.find({}).sort("_id", -1).limit(5)
            for exemple in exemples_cursor:
                validation["exemples"].append(
                    {
                        "livre": exemple.get("livre_titre", ""),
                        "auteur": exemple.get("auteur_nom", ""),
                        "episode": exemple.get("episode_titre", ""),
                    }
                )

            # Log validation
            self.logger.info(
                f"Validation: {validation['total_episode_livres']} documents EpisodeLivre"
            )
            self.logger.info(f"  - {validation['episodes_uniques']} épisodes uniques")
            self.logger.info(f"  - {validation['livres_uniques']} livres uniques")
            self.logger.info(f"  - {validation['auteurs_uniques']} auteurs uniques")

        except Exception as e:
            self.logger.error(f"Erreur validation: {e}")
            validation["coherence_ok"] = False

        return validation


def main():
    """Point d'entrée principal du script"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migration des avis critiques vers episode_livres"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulation sans écriture en base"
    )
    parser.add_argument(
        "--limit", type=int, help="Limite le nombre d'épisodes à traiter"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validation seulement, sans migration",
    )

    args = parser.parse_args()

    # Initialisation migration
    migration = MigrationAvisToEpisodeLivres(dry_run=args.dry_run)

    if args.validate_only:
        # Validation seulement
        validation = migration.validate_migration()
        print(f"Validation terminée. Documents: {validation['total_episode_livres']}")
    else:
        # Migration complète
        stats = migration.migrate_all_episodes(limit=args.limit)

        # Validation post-migration
        if not args.dry_run:
            validation = migration.validate_migration()

    return 0


if __name__ == "__main__":
    sys.exit(main())
