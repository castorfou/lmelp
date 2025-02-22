#!/bin/bash 
export GPG_TTY=$(tty)
pushd /workspaces/lmelp/scripts
uv run python update_emissions.py
popd