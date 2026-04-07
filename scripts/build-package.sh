#!/usr/bin/env bash
set -euo pipefail

PKG_DIR="${1:-}"

if [[ -z "$PKG_DIR" ]]; then
  echo "Usage: $0 <package-directory>" >&2
  exit 1
fi

if [[ ! -d "$PKG_DIR/debian" ]]; then
  echo "Package directory does not contain debian/: $PKG_DIR" >&2
  exit 1
fi

(
  cd "$PKG_DIR"
  dpkg-buildpackage -us -uc -b
)
