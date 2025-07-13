# devcontainer and uv

As explained in [README](README.md), this project uses devcontainer and uv.

## devcontainer

Everything is in `.devcontainer`

## update requirements

make modifications in `.devcontainer/requirements.txt`

to apply modifications 

```bash
source .venv/bin/activate
export UV_LINK_MODE=copy
uv pip install -r .devcontainer/requirements.txt
```

(or you can decide to rebuild devcontainer but it is longer)

## venv

on this project, virtualenv is in `.venv`

## uv

to execute python code from our venv,

```bash
source .venv/bin/activate
uv run python --version
```