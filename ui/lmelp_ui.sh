#!/bin/bash 
# to be launched externally with 
# docker exec -u vscode loving_bose /workspaces/lmelp/ui/lmelp_ui.sh
export PATH="$HOME/.local/bin:$PATH"
export GPG_TTY=$(tty)
pushd /workspaces/lmelp/
streamlit run ui/lmelp.py
popd