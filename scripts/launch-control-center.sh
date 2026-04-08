#!/usr/bin/env bash
set -euo pipefail
VENV="/opt/sanchos-os/venv"
APP="/usr/local/lib/sanchos-os/control-center.py"
if [[ -x "$VENV/bin/python" ]]; then exec "$VENV/bin/python" "$APP" "$@"; fi
exec python3 "$APP" "$@"
