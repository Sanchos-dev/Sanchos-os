#!/usr/bin/env bash
set -euo pipefail

if command -v kwriteconfig5 >/dev/null 2>&1; then
  kwriteconfig5 --file kdeglobals --group KDE --key SingleClick false || true
fi

if command -v systemctl >/dev/null 2>&1; then
  systemctl daemon-reload || true
fi

echo "sanchos-os post-install hooks completed."
