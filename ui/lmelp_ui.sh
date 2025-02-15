#!/bin/bash 
export GPG_TTY=$(tty)
cd /workspaces/lmelp
source .venv/bin/activate
pushd /workspaces/lmelp/
streamlit run ui/lmelp.py
popd