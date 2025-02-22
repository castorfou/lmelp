#!/bin/bash 
export GPG_TTY=$(tty)
export PATH=$PATH:~/.local/bin
source /workspaces/lmelp/.venv/bin/activate
cd /workspaces/lmelp/
ulimit -n 4096
uv run python scripts/get_one_transcription.py