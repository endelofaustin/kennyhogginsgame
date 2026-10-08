#!/bin/sh

set -e

find_python() {
    for candidate in python3.13 python3.12 python3.11 python3.10; do
        if command -v "$candidate" >/dev/null 2>&1; then
            printf '%s' "$candidate"
            return 0
        fi
    done
    return 1
}

PYTHON=$(find_python || true)

if [ -z "$PYTHON" ]; then
    printf '%s\n' "Kenny Hoggins Game requires Python 3.10 or newer." >&2
    printf '%s\n' "No compatible Python was found on this Mac." >&2
    if command -v brew >/dev/null 2>&1; then
        printf '%s\n' "Install one with: brew install python@3.12" >&2
    else
        printf '%s\n' "Install Python 3.12+ from python.org, then run this script again." >&2
    fi
    exit 1
fi

printf 'Using %s: ' "$PYTHON"
"$PYTHON" --version

if [ -d .venv ]; then
    printf '%s\n' "Removing the existing .venv so it cannot keep using Python 3.9..."
    rm -rf .venv
fi

"$PYTHON" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

printf '%s\n' ""
printf '%s\n' "Setup complete. Start the game with:"
printf '%s\n' "  ./runit"
