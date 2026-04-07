#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${1:-desktop-virt}"
PROFILE_FILE="$ROOT_DIR/profiles/${PROFILE}.yaml"
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

read_profile_value() {
  local key="$1"
  python3 - "$PROFILE_FILE" "$key" <<'PY'
import sys
import yaml
from pathlib import Path

path = Path(sys.argv[1])
key = sys.argv[2]
with path.open() as fh:
    data = yaml.safe_load(fh) or {}
value = data.get(key)
if isinstance(value, list):
    for item in value:
        print(item)
elif value is not None:
    print(value)
PY
}

install_base_packages() {
  apt-get update
  apt-get install -y \
    python3 \
    python3-yaml \
    python3-tk \
    sudo \
    curl \
    wget \
    git \
    ca-certificates
}

install_profile_packages() {
  mapfile -t packages < <(read_profile_value packages)
  if [[ ${#packages[@]} -gt 0 ]]; then
    apt-get install -y "${packages[@]}"
    printf '%s\n' "${packages[@]}" > "$STATE_DIR/profile-packages"
  else
    : > "$STATE_DIR/profile-packages"
  fi
}

install_manifests() {
  install -d "$STATE_DIR"
  rm -rf /etc/sanchos-os/profiles /etc/sanchos-os/modules /etc/sanchos-os/configs /etc/sanchos-os/branding
  cp -r "$ROOT_DIR/profiles" /etc/sanchos-os/
  cp -r "$ROOT_DIR/modules" /etc/sanchos-os/
  cp -r "$ROOT_DIR/configs" /etc/sanchos-os/
  cp -r "$ROOT_DIR/branding" /etc/sanchos-os/
  printf '%s\n' "$PROFILE" > "$STATE_DIR/installed-profile"
}

install_configs() {
  install -d /etc/libvirt/libvirtd.conf.d /etc/qemu /usr/share/backgrounds/sanchos-os /usr/share/sddm/themes/sanchos-os /usr/local/share/sanchos-os
  if [[ -f "$ROOT_DIR/configs/libvirt/10-sanchos.conf" ]]; then
    install -m0644 "$ROOT_DIR/configs/libvirt/10-sanchos.conf" /etc/libvirt/libvirtd.conf.d/10-sanchos.conf
  fi
  if [[ -f "$ROOT_DIR/configs/network/qemu-bridge.conf" ]]; then
    install -m0644 "$ROOT_DIR/configs/network/qemu-bridge.conf" /etc/qemu/bridge.conf
  fi
  if [[ -f "$ROOT_DIR/configs/plasma/kdeglobals" ]]; then
    install -d /etc/skel/.config
    install -m0644 "$ROOT_DIR/configs/plasma/kdeglobals" /etc/skel/.config/kdeglobals
  fi
  if [[ -f "$ROOT_DIR/branding/wallpapers/sanchos-default.svg" ]]; then
    install -m0644 "$ROOT_DIR/branding/wallpapers/sanchos-default.svg" /usr/share/backgrounds/sanchos-os/sanchos-default.svg
  fi
  if [[ -f "$ROOT_DIR/branding/sddm/Main.qml" ]]; then
    install -m0644 "$ROOT_DIR/branding/sddm/Main.qml" /usr/share/sddm/themes/sanchos-os/Main.qml
  fi
  if [[ -f "$ROOT_DIR/branding/sddm/metadata.desktop" ]]; then
    install -m0644 "$ROOT_DIR/branding/sddm/metadata.desktop" /usr/share/sddm/themes/sanchos-os/metadata.desktop
  fi
  printf 'profile=%s\ninstalled_at=%s\n' "$PROFILE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /usr/local/share/sanchos-os/install.env
}

install_sanchosctl() {
  install -Dm755 "$ROOT_DIR/packages/sanchosctl/sanchosctl/cli.py" /usr/local/bin/sanchosctl
}

install_ui_bits() {
  install -Dm755 "$ROOT_DIR/firstboot/firstboot.py" /usr/local/lib/sanchos-os/firstboot.py
  install -Dm755 "$ROOT_DIR/ui/control-center/main.py" /usr/local/bin/sanchos-control-center
  install -Dm755 "$ROOT_DIR/bootstrap/uninstall.sh" /usr/local/share/sanchos-os/uninstall.sh
  install -Dm644 "$ROOT_DIR/configs/system/firstboot.desktop" /etc/xdg/autostart/sanchos-firstboot.desktop
  install -Dm644 "$ROOT_DIR/configs/system/control-center.desktop" /usr/share/applications/sanchos-control-center.desktop
}

install_desktop_vpn_client() {
  case "$PROFILE" in
    desktop|desktop-virt|dev)
      log "Installing NekoBox"
      "$ROOT_DIR/scripts/install-nekobox.sh"
      printf '%s\n' nekobox > "$STATE_DIR/external-artifacts"
      ;;
  esac
}

enable_profile_services() {
  case "$PROFILE" in
    desktop|desktop-virt|dev)
      systemctl enable sddm || true
      systemctl enable NetworkManager || true
      ;;
  esac

  if [[ "$PROFILE" == "desktop-virt" ]]; then
    systemctl enable libvirtd || true
    systemctl start libvirtd || true
  fi

  local target_user="${SUDO_USER:-${PKEXEC_UID:-}}"
  if [[ -z "$target_user" && -n "${USER:-}" && "$USER" != "root" ]]; then
    target_user="$USER"
  fi
  if [[ -n "$target_user" ]] && id "$target_user" >/dev/null 2>&1; then
    usermod -aG libvirt "$target_user" || true
    usermod -aG kvm "$target_user" || true
    printf '%s\n' "$target_user" > "$STATE_DIR/desktop-user"
  fi
}

run_postinstall() {
  "$ROOT_DIR/bootstrap/postinstall.sh" || true
}

main() {
  require_root
  "$ROOT_DIR/bootstrap/check-env.sh"

  if [[ ! -f "$PROFILE_FILE" ]]; then
    echo "Unknown profile: $PROFILE" >&2
    exit 1
  fi

  install -d "$STATE_DIR"

  log "Installing bootstrap dependencies"
  install_base_packages

  log "Installing profile packages: $PROFILE"
  install_profile_packages

  log "Installing manifests and configs"
  install_manifests
  install_configs

  log "Installing control tooling"
  install_sanchosctl
  install_ui_bits

  install_desktop_vpn_client

  log "Enabling profile services"
  enable_profile_services

  log "Running post-install hooks"
  run_postinstall

  log "Bootstrap finished for profile: $PROFILE"
  log "Reboot is recommended before regular use."
}

main "$@"
