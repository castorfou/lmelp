#!/bin/bash
sudo apt update
sudo apt install -y libdbus-1-dev libdbus-glib-1-dev cmake 
sudo apt install -y locales
sudo sed -i 's/^# *\(fr_FR.UTF-8\)/\1/' /etc/locale.gen
sudo dpkg-reconfigure locales -f noninteractive
sudo apt install -y ffmpeg
pip install --upgrade pip

# pip install -r .devcontainer/requirements.txt
cd /workspaces/lmelp
pip install uv
uv venv
source .venv/bin/activate
uv pip install -r .devcontainer/requirements.txt

uv run pre-commit install
uv run pre-commit autoupdate

sudo git config --system --add safe.directory '*'

# Create Streamlit credentials file to avoid the email prompt
mkdir -p ~/.streamlit
cat << 'EOF' > ~/.streamlit/credentials.toml
[general]
email = "your_email@example.com"
EOF

/workspaces/lmelp/.devcontainer/setupZsh.sh