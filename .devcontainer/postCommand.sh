#!/bin/bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
uv venv
source .venv/bin/activate
sudo apt update
sudo apt install -y libdbus-1-dev libdbus-glib-1-dev cmake 
sudo apt install -y locales
sudo sed -i 's/^# *\(fr_FR.UTF-8\)/\1/' /etc/locale.gen
uv pip install -r .devcontainer/requirements.txt
pre-commit install