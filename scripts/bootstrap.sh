#!/usr/bin/env bash
# Usage: bash scripts/bootstrap.sh [--install-system]
# Ubuntu/Debian/WSL: --install-system installs GHDL, Python venv, make, and git.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ${1:-} == --install-system ]]; then
    if [[ $(id -u) -eq 0 ]]; then
        installer=(apt-get)
    elif command -v sudo >/dev/null; then
        installer=(sudo apt-get)
    else
        echo 'System installation requires root or sudo. Install ghdl python3-venv make git, then rerun.' >&2
        exit 1
    fi
    "${installer[@]}" update
    "${installer[@]}" install -y ghdl python3 python3-venv make git
elif [[ $# -gt 0 ]]; then
    echo 'Usage: bash scripts/bootstrap.sh [--install-system]' >&2
    exit 2
fi
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
if ! command -v "${GHDL:-ghdl}" >/dev/null; then
    echo 'GHDL is missing. Ubuntu/WSL: bash scripts/bootstrap.sh --install-system' >&2
    echo 'On macOS: brew install ghdl python make' >&2
    exit 1
fi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
"${GHDL:-ghdl}" --version
.venv/bin/python --version
echo 'Ready. Run: source .venv/bin/activate'
echo 'Then run: make check'
