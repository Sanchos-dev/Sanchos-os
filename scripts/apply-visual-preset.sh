#!/usr/bin/env bash
set -euo pipefail
user_name="${SANCHOS_DESKTOP_USER:-${USER:-$(id -un)}}"
state_dir="${HOME:-$(getent passwd "$user_name" | cut -d: -f6)}/.config/sanchos-os"
stamp_file="$state_dir/visual-preset-applied-v13"
mkdir -p "$state_dir"
[[ -f "$stamp_file" ]] && exit 0
sleep 7
if [[ -x /usr/local/lib/sanchos-os/configure-desktop-style.py ]]; then python3 /usr/local/lib/sanchos-os/configure-desktop-style.py --user "$user_name" --apply-now --disable-tiling --skip-layout >/dev/null 2>&1 || true; fi
if [[ -x /usr/local/lib/sanchos-os/apply-plasma-layout.py ]]; then python3 /usr/local/lib/sanchos-os/apply-plasma-layout.py --quiet >/dev/null 2>&1 || true; fi
printf '%s
' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$stamp_file"
