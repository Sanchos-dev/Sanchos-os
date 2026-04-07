#!/usr/bin/env bash
set -euo pipefail

log() {
  echo "[sanchos-os] $*"
}

require_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run this script as root." >&2
    exit 1
  fi
}

remove_path() {
  local target="$1"
  if [[ -e "$target" || -L "$target" ]]; then
    rm -rf "$target"
  fi
}

remove_profile_packages() {
  local state_file="/etc/sanchos-os/state/profile-packages"
  if [[ -f "$state_file" ]]; then
    mapfile -t packages < "$state_file"
    if [[ ${#packages[@]} -gt 0 ]]; then
      log "Removing profile packages"
      apt-get remove -y "${packages[@]}" || true
      apt-get autoremove -y || true
    fi
  fi
}

remove_external_artifacts() {
  if [[ -f /etc/sanchos-os/state/external-artifacts ]]; then
    if grep -qx 'nekobox' /etc/sanchos-os/state/external-artifacts; then
      remove_path /opt/nekobox
      remove_path /usr/local/bin/nekobox
      remove_path /usr/share/applications/nekobox.desktop
    fi
  fi
}

remove_plasma_wallpaper_packages() {
  if [[ -d /usr/share/wallpapers ]]; then
    find /usr/share/wallpapers -maxdepth 1 -mindepth 1 -type d -name 'SanchosOs-*' -exec rm -rf {} + 2>/dev/null || true
  fi
}

main() {
  require_root
  remove_profile_packages
  remove_external_artifacts
  remove_plasma_wallpaper_packages

  log "Removing installed files"
  remove_path /etc/sanchos-os
  remove_path /usr/local/bin/sanchosctl
  remove_path /usr/local/bin/sanchos-control-center
  remove_path /usr/local/lib/sanchos-os
  remove_path /usr/local/share/sanchos-os
  remove_path /usr/share/applications/sanchos-control-center.desktop
  remove_path /etc/xdg/autostart/sanchos-firstboot.desktop
  remove_path /etc/xdg/autostart/sanchos-apply-default-wallpaper.desktop
  remove_path /usr/share/backgrounds/sanchos-os
  remove_path /usr/share/sddm/themes/sanchos-os

  log "Bootstrap content removed"
}

main "$@"
