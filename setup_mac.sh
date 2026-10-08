#!/bin/sh

set -e

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"

UV_BIN="$ROOT/.uv-bin/uv"
PYTHON_DIR="$ROOT/.python"
VENV_DIR="$ROOT/.venv"

if [ ! -x "$UV_BIN" ]; then
    printf '%s\n' "Installing project-local uv into .uv-bin ..."
    mkdir -p "$ROOT/.uv-bin"
    curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="$ROOT/.uv-bin" sh
fi

printf '%s\n' "Installing project-local Python 3.11 into .python ..."
UV_PYTHON_INSTALL_DIR="$PYTHON_DIR" "$UV_BIN" python install 3.11 --install-dir "$PYTHON_DIR"

if [ -d "$VENV_DIR" ]; then
    printf '%s\n' "Removing existing .venv ..."
    rm -rf "$VENV_DIR"
fi

printf '%s\n' "Creating .venv from the project-local Python 3.11 ..."
UV_PYTHON_INSTALL_DIR="$PYTHON_DIR" "$UV_BIN" venv "$VENV_DIR" --python 3.11 --seed

printf '%s\n' "Installing Kenny Hoggins dependencies into .venv ..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

printf '%s\n' ""
printf '%s\n' "Setup complete. Nothing was installed as your system/default Python."
printf '%s\n' "Python used by this repo:"
"$VENV_DIR/bin/python" --version
printf '%s\n' "Start the game with:"
printf '%s\n' "  ./runit"
