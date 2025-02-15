#!/bin/bash 
export GPG_TTY=$(tty)
pushd /workspaces/lmelp/scripts
python update_emissions.py
popd