#!/usr/bin/env bash
set -euo pipefail
VENV="/opt/sanchos-os/venv"
APP="/usr/local/lib/sanchos-os/control-center.py"
session_user="${SANCHOS_DESKTOP_USER:-${SUDO_USER:-${USER:-$(id -un)}}}"
if [[ "${1:-}" == "--as-root" ]]; then shift; fi
if [[ $(id -u) -ne 0 ]]; then
  exec pkexec env DISPLAY="${DISPLAY:-}" WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}" XAUTHORITY="${XAUTHORITY:-}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-}" DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-}" HOME="${HOME:-}" USER="$session_user" LOGNAME="$session_user" SANCHOS_DESKTOP_USER="$session_user" QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-}" "$0" --as-root "$@"
fi
export SANCHOS_DESKTOP_USER="$session_user"
if [[ -x "$VENV/bin/python" ]]; then exec "$VENV/bin/python" "$APP" "$@"; fi
exec python3 "$APP" "$@"
