"""Pipeline de transcription automatisé via la station GPU PGX.

Remplace le workflow manuel scp/ssh vers thinkstationpgx-d7ba.local : un service watcher
tourne sur PGX et transcrit automatiquement tout fichier audio déposé dans le répertoire
surveillé. Ce module vérifie que PGX est joignable, envoie l'audio, attend la
transcription puis la rapatrie. PGX (Wi-Fi uniquement, veille système désactivée pour
raisons GPU) doit être allumée manuellement — aucun réveil à distance n'est tenté.
"""

import os
import socket
import subprocess
import tempfile
import time
from collections.abc import Callable

from config import get_pgx_config


class PgxError(RuntimeError):
    """Erreur levée lorsqu'une étape du pipeline de transcription PGX échoue."""


def ensure_pgx_ssh_key(key_path: str) -> str:
    """Génère la paire de clés SSH dédiée à PGX si elle n'existe pas encore.

    Idempotent : ne régénère rien si la clé privée existe déjà à cet emplacement — elle
    doit rester stable dans le temps (stockée sur un support persistant), sous peine
    d'invalider l'autorisation déjà déployée sur PGX.

    Returns:
        str: Le contenu de la clé publique correspondante.
    """
    if not os.path.exists(key_path):
        parent_dir = os.path.dirname(key_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        try:
            subprocess.run(
                [
                    "ssh-keygen",
                    "-t",
                    "ed25519",
                    "-f",
                    key_path,
                    "-N",
                    "",
                    "-C",
                    "lmelp-pgx",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise PgxError(
                f"Échec de la génération de la clé SSH PGX: {exc.stderr}"
            ) from exc

    with open(f"{key_path}.pub") as f:
        return f.read().strip()


def wait_for_pgx_reachable(
    host: str, port: int = 22, timeout_s: float = 120, poll_interval_s: float = 5
) -> bool:
    """Poll la disponibilité de PGX (connexion TCP) jusqu'à dispo ou expiration du délai."""
    deadline = time.monotonic() + timeout_s
    while True:
        try:
            with socket.create_connection((host, port), timeout=poll_interval_s):
                return True
        except OSError:
            if time.monotonic() >= deadline:
                return False
            time.sleep(poll_interval_s)


def _known_hosts_path() -> str:
    """Fichier known_hosts dédié, dans un répertoire toujours accessible en écriture.

    Jamais le ~/.ssh/known_hosts par défaut (potentiellement en lecture seule, ex:
    bind-mount ro en devcontainer), ni un chemin dérivé de PGX_SSH_KEY_PATH (qui peut lui
    aussi vivre dans un emplacement en lecture seule pour un usage local/dev). Pas besoin
    de persistance : StrictHostKeyChecking=accept-new réaccepte la clé d'hôte à chaque
    redémarrage, sans risque sur un réseau local de confiance.
    """
    return os.path.join(tempfile.gettempdir(), "lmelp_pgx_known_hosts")


def _ssh_base_command(user: str, host: str, key_path: str) -> list:
    return [
        "ssh",
        "-i",
        key_path,
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        f"UserKnownHostsFile={_known_hosts_path()}",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{user}@{host}",
    ]


def _scp_base_command(key_path: str) -> list:
    return [
        "scp",
        "-i",
        key_path,
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        f"UserKnownHostsFile={_known_hosts_path()}",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def _ensure_remote_dir(remote_dir: str, *, host: str, user: str, key_path: str) -> None:
    """Crée le répertoire distant (ex: année) s'il n'existe pas encore — scp ne peut pas
    le créer lui-même."""
    command = _ssh_base_command(user, host, key_path) + [f"mkdir -p '{remote_dir}'"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        raise PgxError(
            f"Échec de la création du répertoire distant sur PGX: {exc.stderr}"
        ) from exc


def send_audio_to_pgx(
    local_path: str,
    remote_dir: str,
    *,
    host: str,
    user: str,
    key_path: str,
    timeout_s: float | None = None,
) -> None:
    """Envoie le fichier audio vers PGX par scp (clé SSH dédiée, pas de mot de passe)."""
    _ensure_remote_dir(remote_dir, host=host, user=user, key_path=key_path)

    command = _scp_base_command(key_path) + [
        local_path,
        f"{user}@{host}:{remote_dir}/",
    ]
    try:
        subprocess.run(
            command, check=True, capture_output=True, text=True, timeout=timeout_s
        )
    except subprocess.CalledProcessError as exc:
        raise PgxError(
            f"Échec de l'envoi du fichier audio vers PGX: {exc.stderr}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise PgxError("Timeout lors de l'envoi du fichier audio vers PGX") from exc


def wait_for_pgx_transcription(
    remote_txt_path: str,
    *,
    host: str,
    user: str,
    key_path: str,
    timeout_s: float = 1800,
    poll_interval_s: float = 10,
) -> bool:
    """Poll (via ssh) l'apparition du fichier de transcription sur PGX."""
    command = _ssh_base_command(user, host, key_path) + [f"test -f '{remote_txt_path}'"]
    deadline = time.monotonic() + timeout_s
    while True:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode == 0:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(poll_interval_s)


def fetch_transcription_from_pgx(
    remote_txt_path: str,
    local_txt_path: str,
    *,
    host: str,
    user: str,
    key_path: str,
) -> str:
    """Rapatrie le fichier de transcription depuis PGX par scp et retourne son contenu."""
    command = _scp_base_command(key_path) + [
        f"{user}@{host}:{remote_txt_path}",
        local_txt_path,
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        raise PgxError(
            f"Échec du rapatriement de la transcription depuis PGX: {exc.stderr}"
        ) from exc

    with open(local_txt_path) as f:
        return f.read()


def _check_ssh_auth(*, host: str, user: str, key_path: str) -> tuple[bool, str]:
    """Teste une authentification SSH réelle avec la clé dédiée (pas juste le port ouvert)."""
    command = _ssh_base_command(user, host, key_path) + ["echo ok"]
    try:
        completed = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=10
        )
    except subprocess.TimeoutExpired:
        return False, "Timeout lors de la tentative d'authentification"
    if completed.returncode == 0 and "ok" in completed.stdout:
        return True, "Authentification réussie avec la clé dédiée"
    return (
        False,
        (
            "Échec de l'authentification — vérifiez que la clé publique est bien "
            "dans authorized_keys sur PGX"
        ),
    )


def _check_remote_dir_exists(
    remote_dir: str, *, host: str, user: str, key_path: str
) -> tuple[bool, str]:
    """Vérifie qu'un répertoire distant existe sur PGX."""
    command = _ssh_base_command(user, host, key_path) + [f"test -d '{remote_dir}'"]
    completed = subprocess.run(
        command, check=False, capture_output=True, text=True, timeout=10
    )
    if completed.returncode == 0:
        return True, f"{remote_dir} existe"
    return False, f"{remote_dir} n'existe pas ou n'est pas accessible"


def run_pgx_diagnostics() -> list[dict]:
    """Exécute une checklist de vérifications PGX (joignabilité, authentification SSH,
    répertoires distants) — chaque vérification arrête les suivantes si elle échoue,
    puisqu'elles en dépendent (inutile de tester l'authentification si injoignable, etc.).

    Returns:
        list[dict]: une entrée par vérification, avec les clés "name" (str), "status"
        ("ok", "fail" ou "skipped") et "detail" (str).
    """
    config = get_pgx_config()
    host = config["host"]
    user = config["user"]
    key_path = config["key_path"]
    remote_audio_root = config["remote_audio_root"]
    remote_transcription_root = config["remote_transcription_root"]

    results = []

    reachable = wait_for_pgx_reachable(host, timeout_s=5, poll_interval_s=2)
    results.append(
        {
            "name": "Machine joignable",
            "status": "ok" if reachable else "fail",
            "detail": (
                f"{host} répond sur le port 22"
                if reachable
                else f"{host} ne répond pas sur le port 22 — vérifiez qu'elle est allumée"
            ),
        }
    )
    if not reachable:
        for name in (
            "Authentification SSH (clé dédiée)",
            "Répertoire audio distant",
            "Répertoire transcriptions distant",
        ):
            results.append(
                {"name": name, "status": "skipped", "detail": "PGX injoignable"}
            )
        return results

    ssh_ok, ssh_detail = _check_ssh_auth(host=host, user=user, key_path=key_path)
    results.append(
        {
            "name": "Authentification SSH (clé dédiée)",
            "status": "ok" if ssh_ok else "fail",
            "detail": ssh_detail,
        }
    )
    if not ssh_ok:
        for name in ("Répertoire audio distant", "Répertoire transcriptions distant"):
            results.append(
                {
                    "name": name,
                    "status": "skipped",
                    "detail": "Authentification SSH impossible",
                }
            )
        return results

    audio_ok, audio_detail = _check_remote_dir_exists(
        remote_audio_root, host=host, user=user, key_path=key_path
    )
    results.append(
        {
            "name": "Répertoire audio distant",
            "status": "ok" if audio_ok else "fail",
            "detail": audio_detail,
        }
    )

    txt_ok, txt_detail = _check_remote_dir_exists(
        remote_transcription_root, host=host, user=user, key_path=key_path
    )
    results.append(
        {
            "name": "Répertoire transcriptions distant",
            "status": "ok" if txt_ok else "fail",
            "detail": txt_detail,
        }
    )

    return results


def extract_whisper_pgx(
    mp3_filename: str,
    *,
    year: str,
    on_progress: Callable[[str], None] | None = None,
) -> str:
    """Orchestre le pipeline PGX complet : vérification -> envoi -> attente -> rapatriement.

    Lève PgxError si une étape échoue (aucun fallback automatique vers whisper.cpp/HF, et
    aucune tentative de réveil à distance — PGX doit être allumée manuellement).
    """

    def notify(message: str) -> None:
        if on_progress:
            on_progress(message)

    config = get_pgx_config()
    host = config["host"]
    user = config["user"]
    key_path = config["key_path"]
    remote_audio_root = config["remote_audio_root"]
    remote_transcription_root = config["remote_transcription_root"]

    transcription_timeout_s = float(os.getenv("PGX_TRANSCRIPTION_TIMEOUT_S", "1800"))
    poll_interval_s = float(os.getenv("PGX_POLL_INTERVAL_S", "10"))

    notify("Vérification de la disponibilité de PGX…")
    if not wait_for_pgx_reachable(host, timeout_s=10, poll_interval_s=2):
        raise PgxError(
            "PGX injoignable — vérifiez qu'elle est allumée et sur le réseau, puis "
            "réessayez (aucun réveil automatique n'est tenté)"
        )

    notify("PGX disponible, envoi du fichier audio…")
    basename = os.path.basename(mp3_filename)
    stem = os.path.splitext(basename)[0]
    remote_audio_dir = f"{remote_audio_root}/{year}"
    send_audio_to_pgx(
        mp3_filename, remote_audio_dir, host=host, user=user, key_path=key_path
    )

    notify("Fichier envoyé, attente de la transcription sur PGX…")
    remote_txt_path = f"{remote_transcription_root}/{year}/{stem}.txt"
    if not wait_for_pgx_transcription(
        remote_txt_path,
        host=host,
        user=user,
        key_path=key_path,
        timeout_s=transcription_timeout_s,
        poll_interval_s=poll_interval_s,
    ):
        raise PgxError(
            f"Timeout: transcription non disponible sur PGX après {transcription_timeout_s}s"
        )

    notify("Transcription disponible, rapatriement…")
    local_txt_path = os.path.splitext(mp3_filename)[0] + ".txt"
    transcription_text = fetch_transcription_from_pgx(
        remote_txt_path, local_txt_path, host=host, user=user, key_path=key_path
    )
    notify("Transcription rapatriée avec succès")
    return transcription_text
