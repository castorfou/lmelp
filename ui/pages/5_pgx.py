import sys
from pathlib import Path

import streamlit as st


sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path


add_to_sys_path()

from config import get_pgx_config
from pgx import PgxError, ensure_pgx_ssh_key, run_pgx_diagnostics


st.write("### Configuration PGX")
st.write(
    "PGX est la station GPU utilisée pour la transcription automatisée des épisodes. "
    "Cette page permet de vérifier sa disponibilité et de déployer la clé SSH dédiée."
)

pgx_config = get_pgx_config()
host = pgx_config["host"]
user = pgx_config["user"]
key_path = pgx_config["key_path"]

missing = [
    name
    for name, value in [
        ("PGX_HOST", host),
        ("PGX_USER", user),
        ("PGX_SSH_KEY_PATH", key_path),
        ("PGX_REMOTE_AUDIO_ROOT", pgx_config["remote_audio_root"]),
        ("PGX_REMOTE_TRANSCRIPTION_ROOT", pgx_config["remote_transcription_root"]),
    ]
    if not value
]

if missing:
    st.warning(
        "Variables d'environnement manquantes : "
        + ", ".join(missing)
        + ". Voir docs/user/transcription-pgx.md."
    )
else:
    st.write("#### Statut")

    icons = {"ok": "🟢", "fail": "🔴", "skipped": "⚪"}

    refresh_clicked = st.button("🔄 Relancer les vérifications")
    if refresh_clicked or "pgx_diagnostics" not in st.session_state:
        with st.spinner(f"Vérification de {host}..."):
            st.session_state["pgx_diagnostics"] = run_pgx_diagnostics()

    for result in st.session_state["pgx_diagnostics"]:
        icon = icons[result["status"]]
        st.write(f"{icon} **{result['name']}** — {result['detail']}")

    st.write("#### Clé SSH dédiée")
    try:
        public_key = ensure_pgx_ssh_key(key_path)
    except PgxError as exc:
        st.error(f"Échec de la génération de la clé SSH: {exc}")
    else:
        st.code(public_key, language=None)
        st.write(
            "Si ce n'est pas déjà fait, ajoutez cette clé au `authorized_keys` du compte "
            f"`{user}` sur PGX en exécutant sur PGX :"
        )
        st.code(f"echo '{public_key}' >> ~/.ssh/authorized_keys", language="bash")

    st.write("#### Répertoires distants configurés")
    st.write(f"- Audios : `{pgx_config['remote_audio_root']}/<année>/`")
    st.write(
        f"- Transcriptions : `{pgx_config['remote_transcription_root']}/<année>/<fichier>.txt`"
    )
