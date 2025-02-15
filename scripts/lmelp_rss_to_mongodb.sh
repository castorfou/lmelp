#!/bin/bash 
export GPG_TTY=$(tty)
cd /workspaces/lmelp
source .venv/bin/activate
pushd /workspaces/lmelp/scripts
python update_emissions.py
popd