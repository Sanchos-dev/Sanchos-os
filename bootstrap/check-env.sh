#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "[error] $*" >&2
  exit 1
}

warn() {
  echo "[warn] $*" >&2
}

[[ -f /etc/os-release ]] || fail "Cannot determine host OS."
. /etc/os-release

if [[ "${ID:-}" != "debian" ]]; then
  fail "This bootstrap currently supports Debian only."
fi

if [[ "${VERSION_ID:-}" != "12" && "${VERSION_ID:-}" != "13" ]]; then
  warn "Tested targets are Debian 12 and Debian 13. Current version: ${VERSION_ID:-unknown}."
fi

if [[ "$(id -u)" -ne 0 ]]; then
  fail "Run this script as root."
fi

if ! command -v apt-get >/dev/null 2>&1; then
  fail "apt-get is not available."
fi

if systemd-detect-virt --quiet; then
  warn "System appears to be running in a virtual machine. That is fine for prototyping, but nested virtualization may be limited."
fi

echo "[ok] Environment check passed."
