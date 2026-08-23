"""
Tests pour le module nbs.pgx.

Pipeline de transcription automatisé via la station GPU PGX (thinkstationpgx-d7ba.local) :
- Vérification de disponibilité (PGX doit être allumée manuellement, pas de réveil à distance)
- Envoi du fichier audio par scp (clé SSH dédiée)
- Attente de la transcription générée par le watcher PGX
- Rapatriement de la transcription

Aucun de ces tests ne fait de vrai appel réseau : socket/subprocess/time.sleep sont mockés.
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


os.environ.setdefault("AUDIO_PATH", "/tmp/test_audio")

nbs_path = Path(__file__).parent.parent.parent / "nbs"
if str(nbs_path) not in sys.path:
    sys.path.insert(0, str(nbs_path))


class TestEnsurePgxSshKey:
    """Tests pour ensure_pgx_ssh_key (génération idempotente de la clé SSH dédiée)."""

    def test_generates_key_when_absent(self, tmp_path):
        from nbs.pgx import ensure_pgx_ssh_key

        key_path = str(tmp_path / "pgx_lmelp_ed25519")

        def fake_keygen(command, **kwargs):
            with open(key_path, "w") as f:
                f.write("fake-private-key")
            with open(key_path + ".pub", "w") as f:
                f.write("ssh-ed25519 AAAAfake lmelp-pgx\n")
            return MagicMock(returncode=0)

        with patch("nbs.pgx.subprocess.run", side_effect=fake_keygen) as mock_run:
            result = ensure_pgx_ssh_key(key_path)

            assert result == "ssh-ed25519 AAAAfake lmelp-pgx"
            args, _kwargs = mock_run.call_args
            command = args[0]
            assert command[0] == "ssh-keygen"
            assert "-f" in command
            assert key_path in command

    def test_does_not_regenerate_when_key_already_exists(self, tmp_path):
        from nbs.pgx import ensure_pgx_ssh_key

        key_path = str(tmp_path / "pgx_lmelp_ed25519")
        with open(key_path, "w") as f:
            f.write("existing-private-key")
        with open(key_path + ".pub", "w") as f:
            f.write("ssh-ed25519 AAAAexisting lmelp-pgx\n")

        with patch("nbs.pgx.subprocess.run") as mock_run:
            result = ensure_pgx_ssh_key(key_path)

            mock_run.assert_not_called()
            assert result == "ssh-ed25519 AAAAexisting lmelp-pgx"

    def test_keygen_failure_raises_pgx_error(self, tmp_path):
        from nbs.pgx import PgxError, ensure_pgx_ssh_key

        key_path = str(tmp_path / "pgx_lmelp_ed25519")

        with (
            patch(
                "nbs.pgx.subprocess.run",
                side_effect=subprocess.CalledProcessError(
                    1, ["ssh-keygen"], stderr="boom"
                ),
            ),
            pytest.raises(PgxError),
        ):
            ensure_pgx_ssh_key(key_path)


class TestPgxError:
    def test_pgx_error_is_runtime_error(self):
        from nbs.pgx import PgxError

        assert issubclass(PgxError, RuntimeError)


class TestWaitForPgxReachable:
    def test_returns_true_when_reachable_immediately(self):
        from nbs.pgx import wait_for_pgx_reachable

        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = False

        with patch("nbs.pgx.socket.create_connection", return_value=mock_conn):
            assert (
                wait_for_pgx_reachable(
                    "thinkstationpgx-d7ba.local", timeout_s=5, poll_interval_s=1
                )
                is True
            )

    def test_returns_false_after_timeout_when_unreachable(self):
        from nbs.pgx import wait_for_pgx_reachable

        with (
            patch(
                "nbs.pgx.socket.create_connection", side_effect=OSError("unreachable")
            ),
            patch("nbs.pgx.time.sleep"),
        ):
            assert (
                wait_for_pgx_reachable(
                    "thinkstationpgx-d7ba.local", timeout_s=0.01, poll_interval_s=0.01
                )
                is False
            )

    def test_retries_before_succeeding(self):
        from nbs.pgx import wait_for_pgx_reachable

        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = False

        with (
            patch(
                "nbs.pgx.socket.create_connection",
                side_effect=[OSError("unreachable"), mock_conn],
            ),
            patch("nbs.pgx.time.sleep") as mock_sleep,
        ):
            assert (
                wait_for_pgx_reachable(
                    "thinkstationpgx-d7ba.local", timeout_s=5, poll_interval_s=1
                )
                is True
            )
            mock_sleep.assert_called_once_with(1)


class TestKnownHostsIsolation:
    """La commande ssh/scp ne doit jamais dépendre du ~/.ssh/known_hosts par défaut
    (potentiellement en lecture seule, ex: bind-mount ro en devcontainer, ou l'emplacement
    de la clé elle-même peut être en lecture seule) — elle doit utiliser un fichier dans un
    répertoire toujours accessible en écriture (tmp), sans dépendre d'où vit la clé SSH.
    """

    def test_scp_command_uses_writable_known_hosts(self):
        from nbs.pgx import _known_hosts_path, send_audio_to_pgx

        with patch("nbs.pgx.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            send_audio_to_pgx(
                "/audios/2024/episode.m4a",
                "/remote/audios/2024",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/home/vscode/.ssh/pgx_id_ed25519",
            )

            args, _kwargs = mock_run.call_args
            command = args[0]
            assert f"UserKnownHostsFile={_known_hosts_path()}" in command
            assert not _known_hosts_path().startswith("/home/vscode/.ssh")

    def test_ssh_command_uses_writable_known_hosts(self):
        from nbs.pgx import _known_hosts_path, wait_for_pgx_transcription

        with patch(
            "nbs.pgx.subprocess.run", return_value=MagicMock(returncode=0)
        ) as mock_run:
            wait_for_pgx_transcription(
                "/remote/transcriptions/2024/episode.txt",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/home/vscode/.ssh/pgx_id_ed25519",
                timeout_s=60,
                poll_interval_s=1,
            )
            args, _kwargs = mock_run.call_args
            command = args[0]
            assert f"UserKnownHostsFile={_known_hosts_path()}" in command


class TestSendAudioToPgx:
    def test_success_builds_expected_scp_command(self):
        from nbs.pgx import send_audio_to_pgx

        with patch("nbs.pgx.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            send_audio_to_pgx(
                "/audios/2024/episode.m4a",
                "/remote/audios/2024",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
            )

            args, kwargs = mock_run.call_args
            command = args[0]
            assert command[0] == "scp"
            assert "-i" in command
            assert "/keys/pgx_id_ed25519" in command
            assert "/audios/2024/episode.m4a" in command
            assert (
                command[-1] == "f279814@thinkstationpgx-d7ba.local:/remote/audios/2024/"
            )
            assert kwargs.get("check") is True

    def test_creates_remote_directory_before_scp(self):
        """Le répertoire distant (ex: année) peut ne pas encore exister sur PGX — scp ne
        peut pas le créer lui-même, il faut donc un mkdir -p préalable via ssh."""
        from nbs.pgx import send_audio_to_pgx

        with patch("nbs.pgx.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            send_audio_to_pgx(
                "/audios/2024/episode.m4a",
                "/remote/audios/2024",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
            )

            assert mock_run.call_count == 2
            mkdir_args, _ = mock_run.call_args_list[0]
            mkdir_command = mkdir_args[0]
            assert mkdir_command[0] == "ssh"
            assert "mkdir -p '/remote/audios/2024'" in mkdir_command[-1]
            scp_args, _ = mock_run.call_args_list[1]
            assert scp_args[0][0] == "scp"

    def test_mkdir_failure_raises_pgx_error_without_scp(self):
        from nbs.pgx import PgxError, send_audio_to_pgx

        with patch(
            "nbs.pgx.subprocess.run",
            side_effect=subprocess.CalledProcessError(
                1, ["ssh"], stderr="permission denied"
            ),
        ) as mock_run:
            with pytest.raises(PgxError):
                send_audio_to_pgx(
                    "/audios/2024/episode.m4a",
                    "/remote/audios/2024",
                    host="thinkstationpgx-d7ba.local",
                    user="f279814",
                    key_path="/keys/pgx_id_ed25519",
                )
            mock_run.assert_called_once()

    def test_scp_failure_raises_pgx_error(self):
        from nbs.pgx import PgxError, send_audio_to_pgx

        with (
            patch(
                "nbs.pgx.subprocess.run",
                side_effect=subprocess.CalledProcessError(
                    1, ["scp"], stderr="permission denied"
                ),
            ),
            pytest.raises(PgxError),
        ):
            send_audio_to_pgx(
                "/audios/2024/episode.m4a",
                "/remote/audios/2024",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
            )

    def test_scp_timeout_raises_pgx_error(self):
        from nbs.pgx import PgxError, send_audio_to_pgx

        with (
            patch(
                "nbs.pgx.subprocess.run",
                side_effect=[
                    MagicMock(returncode=0),  # mkdir -p réussit
                    subprocess.TimeoutExpired(["scp"], 30),
                ],
            ),
            pytest.raises(PgxError),
        ):
            send_audio_to_pgx(
                "/audios/2024/episode.m4a",
                "/remote/audios/2024",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
                timeout_s=30,
            )


class TestWaitForPgxTranscription:
    def test_returns_true_when_file_exists_immediately(self):
        from nbs.pgx import wait_for_pgx_transcription

        with patch("nbs.pgx.subprocess.run", return_value=MagicMock(returncode=0)):
            result = wait_for_pgx_transcription(
                "/remote/transcriptions/2024/episode.txt",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
                timeout_s=60,
                poll_interval_s=1,
            )
            assert result is True

    def test_returns_false_after_timeout(self):
        from nbs.pgx import wait_for_pgx_transcription

        with (
            patch("nbs.pgx.subprocess.run", return_value=MagicMock(returncode=1)),
            patch("nbs.pgx.time.sleep"),
        ):
            result = wait_for_pgx_transcription(
                "/remote/transcriptions/2024/episode.txt",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
                timeout_s=0.01,
                poll_interval_s=0.01,
            )
            assert result is False

    def test_ssh_command_checks_remote_file_existence(self):
        from nbs.pgx import wait_for_pgx_transcription

        with patch(
            "nbs.pgx.subprocess.run", return_value=MagicMock(returncode=0)
        ) as mock_run:
            wait_for_pgx_transcription(
                "/remote/transcriptions/2024/episode.txt",
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
                timeout_s=60,
                poll_interval_s=1,
            )
            args, _kwargs = mock_run.call_args
            command = args[0]
            assert command[0] == "ssh"
            assert "f279814@thinkstationpgx-d7ba.local" in command
            assert "/remote/transcriptions/2024/episode.txt" in command[-1]


class TestFetchTranscriptionFromPgx:
    def test_success_returns_file_content(self, tmp_path):
        from nbs.pgx import fetch_transcription_from_pgx

        local_txt_path = str(tmp_path / "episode.txt")

        def fake_scp(command, **kwargs):
            with open(local_txt_path, "w") as f:
                f.write("Transcription de test")
            return MagicMock(returncode=0)

        with patch("nbs.pgx.subprocess.run", side_effect=fake_scp):
            result = fetch_transcription_from_pgx(
                "/remote/transcriptions/2024/episode.txt",
                local_txt_path,
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
            )

            assert result == "Transcription de test"

    def test_scp_failure_raises_pgx_error(self, tmp_path):
        from nbs.pgx import PgxError, fetch_transcription_from_pgx

        local_txt_path = str(tmp_path / "episode.txt")

        with (
            patch(
                "nbs.pgx.subprocess.run",
                side_effect=subprocess.CalledProcessError(
                    1, ["scp"], stderr="no such file"
                ),
            ),
            pytest.raises(PgxError),
        ):
            fetch_transcription_from_pgx(
                "/remote/transcriptions/2024/episode.txt",
                local_txt_path,
                host="thinkstationpgx-d7ba.local",
                user="f279814",
                key_path="/keys/pgx_id_ed25519",
            )


class TestExtractWhisperPgx:
    """Tests de l'orchestrateur extract_whisper_pgx (vérification -> envoi -> attente -> rapatriement)."""

    def _patch_config(self):
        return patch(
            "nbs.pgx.get_pgx_config",
            return_value={
                "host": "thinkstationpgx-d7ba.local",
                "user": "f279814",
                "key_path": "/keys/pgx_id_ed25519",
                "remote_audio_root": "/remote/audios",
                "remote_transcription_root": "/remote/transcriptions",
            },
        )

    def test_nominal_path_when_reachable(self):
        from nbs.pgx import extract_whisper_pgx

        progress_messages = []

        with (
            self._patch_config(),
            patch(
                "nbs.pgx.wait_for_pgx_reachable", return_value=True
            ) as mock_reachable,
            patch("nbs.pgx.send_audio_to_pgx") as mock_send,
            patch(
                "nbs.pgx.wait_for_pgx_transcription", return_value=True
            ) as mock_wait_txt,
            patch(
                "nbs.pgx.fetch_transcription_from_pgx",
                return_value="Transcription finale",
            ) as mock_fetch,
        ):
            result = extract_whisper_pgx(
                "/audios/2024/episode.m4a",
                year="2024",
                on_progress=progress_messages.append,
            )

            assert result == "Transcription finale"
            mock_reachable.assert_called_once()
            mock_send.assert_called_once()
            mock_wait_txt.assert_called_once()
            mock_fetch.assert_called_once()
            assert len(progress_messages) >= 3

    def test_raises_pgx_error_when_unreachable_no_wake_attempted(self):
        from nbs.pgx import PgxError, extract_whisper_pgx

        with (
            self._patch_config(),
            patch(
                "nbs.pgx.wait_for_pgx_reachable", return_value=False
            ) as mock_reachable,
            patch("nbs.pgx.send_audio_to_pgx") as mock_send,
        ):
            with pytest.raises(PgxError):
                extract_whisper_pgx("/audios/2024/episode.m4a", year="2024")

            # Une seule vérification, aucune tentative de réveil
            mock_reachable.assert_called_once()
            mock_send.assert_not_called()

    def test_raises_pgx_error_when_transcription_never_appears(self):
        from nbs.pgx import PgxError, extract_whisper_pgx

        with (
            self._patch_config(),
            patch("nbs.pgx.wait_for_pgx_reachable", return_value=True),
            patch("nbs.pgx.send_audio_to_pgx"),
            patch("nbs.pgx.wait_for_pgx_transcription", return_value=False),
            patch("nbs.pgx.fetch_transcription_from_pgx") as mock_fetch,
        ):
            with pytest.raises(PgxError):
                extract_whisper_pgx("/audios/2024/episode.m4a", year="2024")

            mock_fetch.assert_not_called()

    def test_propagates_pgx_error_from_send_audio(self):
        from nbs.pgx import PgxError, extract_whisper_pgx

        with (
            self._patch_config(),
            patch("nbs.pgx.wait_for_pgx_reachable", return_value=True),
            patch("nbs.pgx.send_audio_to_pgx", side_effect=PgxError("scp failed")),
            pytest.raises(PgxError),
        ):
            extract_whisper_pgx("/audios/2024/episode.m4a", year="2024")

    def test_works_without_on_progress_callback(self):
        from nbs.pgx import extract_whisper_pgx

        with (
            self._patch_config(),
            patch("nbs.pgx.wait_for_pgx_reachable", return_value=True),
            patch("nbs.pgx.send_audio_to_pgx"),
            patch("nbs.pgx.wait_for_pgx_transcription", return_value=True),
            patch("nbs.pgx.fetch_transcription_from_pgx", return_value="ok"),
        ):
            # Ne doit pas lever si on_progress n'est pas fourni
            result = extract_whisper_pgx("/audios/2024/episode.m4a", year="2024")
            assert result == "ok"


class TestRunPgxDiagnostics:
    """Tests pour run_pgx_diagnostics() : checklist de vérifications affichée par la page
    Streamlit PGX (joignabilité, authentification SSH, répertoires distants)."""

    def _patch_config(self):
        return patch(
            "nbs.pgx.get_pgx_config",
            return_value={
                "host": "thinkstationpgx-d7ba.local",
                "user": "f279814",
                "key_path": "/keys/pgx_id_ed25519",
                "remote_audio_root": "/remote/audios",
                "remote_transcription_root": "/remote/transcriptions",
            },
        )

    def test_all_checks_pass(self):
        from nbs.pgx import run_pgx_diagnostics

        with (
            self._patch_config(),
            patch("nbs.pgx.wait_for_pgx_reachable", return_value=True),
            patch(
                "nbs.pgx.subprocess.run",
                return_value=MagicMock(returncode=0, stdout="ok"),
            ),
        ):
            results = run_pgx_diagnostics()

            names = [r["name"] for r in results]
            statuses = [r["status"] for r in results]
            assert "Machine joignable" in names
            assert "Authentification SSH (clé dédiée)" in names
            assert "Répertoire audio distant" in names
            assert "Répertoire transcriptions distant" in names
            assert statuses == ["ok", "ok", "ok", "ok"]

    def test_unreachable_skips_remaining_checks(self):
        from nbs.pgx import run_pgx_diagnostics

        with (
            self._patch_config(),
            patch("nbs.pgx.wait_for_pgx_reachable", return_value=False),
            patch("nbs.pgx.subprocess.run") as mock_run,
        ):
            results = run_pgx_diagnostics()

            statuses = {r["name"]: r["status"] for r in results}
            assert statuses["Machine joignable"] == "fail"
            assert statuses["Authentification SSH (clé dédiée)"] == "skipped"
            assert statuses["Répertoire audio distant"] == "skipped"
            assert statuses["Répertoire transcriptions distant"] == "skipped"
            mock_run.assert_not_called()

    def test_ssh_auth_failure_skips_directory_checks(self):
        from nbs.pgx import run_pgx_diagnostics

        with (
            self._patch_config(),
            patch("nbs.pgx.wait_for_pgx_reachable", return_value=True),
            patch(
                "nbs.pgx.subprocess.run",
                return_value=MagicMock(returncode=255, stdout="", stderr="denied"),
            ),
        ):
            results = run_pgx_diagnostics()

            statuses = {r["name"]: r["status"] for r in results}
            assert statuses["Machine joignable"] == "ok"
            assert statuses["Authentification SSH (clé dédiée)"] == "fail"
            assert statuses["Répertoire audio distant"] == "skipped"
            assert statuses["Répertoire transcriptions distant"] == "skipped"

    def test_missing_remote_directory_reported_as_fail(self):
        from nbs.pgx import run_pgx_diagnostics

        def fake_run(command, **kwargs):
            if "/remote/audios" in command[-1]:
                return MagicMock(returncode=1, stdout="", stderr="")
            return MagicMock(returncode=0, stdout="ok", stderr="")

        with (
            self._patch_config(),
            patch("nbs.pgx.wait_for_pgx_reachable", return_value=True),
            patch("nbs.pgx.subprocess.run", side_effect=fake_run),
        ):
            results = run_pgx_diagnostics()

            statuses = {r["name"]: r["status"] for r in results}
            assert statuses["Authentification SSH (clé dédiée)"] == "ok"
            assert statuses["Répertoire audio distant"] == "fail"
            assert statuses["Répertoire transcriptions distant"] == "ok"
