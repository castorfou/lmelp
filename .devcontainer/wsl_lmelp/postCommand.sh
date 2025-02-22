#!/bin/bash
apt update
apt install -y libdbus-1-dev libdbus-glib-1-dev cmake 
apt install -y locales
sed -i 's/^# *\(fr_FR.UTF-8\)/\1/' /etc/locale.gen
dpkg-reconfigure locales -f noninteractive
pip install --upgrade pip

# pip install -r .devcontainer/requirements.txt
cd /workspaces/lmelp
pip install uv
uv venv
source .venv/bin/activate
uv pip install -r .devcontainer/requirements.txt

uv run pre-commit install
uv run pre-commit autoupdate


git config --system --add safe.directory '*'
 
# Create Streamlit credentials file to avoid the email prompt
mkdir -p ~/.streamlit
cat << 'EOF' > ~/.streamlit/credentials.toml
[general]
email = "your_email@example.com"
EOF

/workspaces/lmelp/.devcontainer/wsl_lmelp/setupZsh.sh