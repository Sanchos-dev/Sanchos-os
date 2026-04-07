#!/usr/bin/env bash
set -euo pipefail

state_dir="${HOME:-$(getent passwd "$(id -un)" | cut -d: -f6)}/.config/sanchos-os"
stamp_file="$state_dir/default-wallpaper-applied"
mkdir -p "$state_dir"

if [[ -f "$stamp_file" ]]; then
  exit 0
fi

if ! command -v sanchosctl >/dev/null 2>&1; then
  exit 0
fi

sanchosctl wallpaper apply-default --quiet >/dev/null 2>&1 || true
printf '%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$stamp_file"
