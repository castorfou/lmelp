#!/bin/bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
uv venv
source .venv/bin/activate
uv pip install -r .devcontainer/requirements.txt
