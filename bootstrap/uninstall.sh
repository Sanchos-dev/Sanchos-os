#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="/etc/sanchos-os/state"

log() {
  echo "[sanchos-os] $*"
}

require_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run this script as root." >&2
    exit 1
  fi
}

read_list_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    grep -v '^\s*$' "$file" || true
  fi
}

remove_external_artifacts() {
  if grep -qx 'nekobox' "$STATE_DIR/external-artifacts" 2>/dev/null; then
    rm -f /usr/local/bin/nekobox
    rm -f /usr/share/applications/nekobox.desktop
    rm -rf /opt/nekobox
  fi
}

remove_packages() {
  mapfile -t packages < <(read_list_file "$STATE_DIR/profile-packages")
  if [[ ${#packages[@]} -gt 0 ]]; then
    log "Removing profile packages"
    apt-get remove -y "${packages[@]}" || true
    apt-get autoremove -y || true
  fi
}

remove_system_files() {
  rm -f /usr/local/bin/sanchosctl
  rm -f /usr/local/bin/sanchos-control-center
  rm -f /usr/share/applications/sanchos-control-center.desktop
  rm -f /usr/local/lib/sanchos-os/firstboot.py
  rm -f /etc/xdg/autostart/sanchos-firstboot.desktop
  rm -rf /usr/local/lib/sanchos-os
  rm -rf /usr/local/share/sanchos-os
  rm -rf /usr/share/backgrounds/sanchos-os
  rm -rf /usr/share/sddm/themes/sanchos-os
  rm -f /etc/libvirt/libvirtd.conf.d/10-sanchos.conf
  rm -f /etc/qemu/bridge.conf
  rm -rf /etc/sanchos-os
}

main() {
  require_root
  log "Removing external artifacts"
  remove_external_artifacts
  remove_packages
  log "Removing installed files"
  remove_system_files
  log "sanchos-os bootstrap content removed"
}

main "$@"
