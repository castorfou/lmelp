#!/bin/bash
apt update
apt install -y locales
sed -i 's/^# *\(fr_FR.UTF-8\)/\1/' /etc/locale.gen
dpkg-reconfigure locales -f noninteractive
pip install --upgrade pip

# Charger le fichier repo_name.env depuis le répertoire parent du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../repo_name.env"

cd /workspaces/${REPO_NAME}

git config --global --add safe.directory /workspaces/${REPO_NAME}

pip install uv
uv venv
source .venv/bin/activate
# propre à WSL
export UV_LINK_MODE=copy
uv pip install  --extra-index-url https://artifactory.michelin.com/artifactory/api/pypi/pypi/simple -r .devcontainer/wsl/requirements.txt

uv run pre-commit install
uv run pre-commit autoupdate

# Create Streamlit credentials file to avoid the email prompt
mkdir -p ~/.streamlit
cat << 'EOF' > ~/.streamlit/credentials.toml
[general]
email = "your_email@example.com"
EOF

/workspaces/${REPO_NAME}/.devcontainer/wsl/setupZsh.sh