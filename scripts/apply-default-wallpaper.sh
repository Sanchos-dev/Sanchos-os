#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  exit 0
fi

sleep 4
exec sanchosctl wallpaper apply-default --quiet
