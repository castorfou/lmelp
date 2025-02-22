#!/bin/bash 
export GPG_TTY=$(tty)
export PATH=$PATH:~/.local/bin
source /workspaces/lmelp/.venv/bin/activate
cd /workspaces/lmelp/
uv run python scripts/update_emissions.py