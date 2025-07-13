"""
Package fixtures - Données de test pour les tests unitaires

Ce package contient les données d'exemple utilisées dans les tests unitaires.
Il permet de centraliser et réutiliser les données de test entre différents modules.

Organisation :
- Configuration : Exemples de variables d'environnement et config
- MongoDB : Documents d'exemple pour les collections
- RSS : Flux et épisodes d'exemple
- LLM : Transcriptions et réponses d'exemple
- Fichiers : Données brutes (JSON, XML, TXT)

Usage :
    from tests.fixtures.sample_config import TEST_CONFIG
    from tests.fixtures.sample_episode import SAMPLE_EPISODE_DATA
"""

__all__ = [
    # Sera enrichi au fur et à mesure des ajouts
]

# Chemins vers les fichiers de données
import os
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent
SAMPLE_DATA_DIR = FIXTURES_DIR / "data"


# Utilitaires pour charger les données de test
def load_sample_json(filename: str) -> dict:
    """Charge un fichier JSON de test depuis fixtures/data/"""
    file_path = SAMPLE_DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier de test non trouvé : {file_path}")

    import json

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sample_text(filename: str) -> str:
    """Charge un fichier texte de test depuis fixtures/data/"""
    file_path = SAMPLE_DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier de test non trouvé : {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
