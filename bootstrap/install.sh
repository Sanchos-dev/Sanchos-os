#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${1:-desktop-virt}"
PROFILE_FILE="$ROOT_DIR/profiles/${PROFILE}.yaml"

log() {
  echo "[sanchos-os] $*"
}

require_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run this script as root." >&2
    exit 1
  fi
}

install_base_packages() {
  apt-get update
  apt-get install -y \
    python3 \
    python3-yaml \
    sudo \
    curl \
    wget \
    git \
    ca-certificates
}

install_profile_packages() {
  python3 - "$PROFILE_FILE" <<'PY' | xargs -r apt-get install -y
import sys
import yaml
from pathlib import Path

path = Path(sys.argv[1])
with path.open() as fh:
    data = yaml.safe_load(fh)
for pkg in data.get("packages", []):
    print(pkg)
PY
}

install_manifests() {
  install -d /etc/sanchos-os/state
  rm -rf /etc/sanchos-os/profiles /etc/sanchos-os/modules /etc/sanchos-os/configs
  cp -r "$ROOT_DIR/profiles" /etc/sanchos-os/
  cp -r "$ROOT_DIR/modules" /etc/sanchos-os/
  cp -r "$ROOT_DIR/configs" /etc/sanchos-os/
}

install_configs() {
  install -d /etc/libvirt/libvirtd.conf.d /etc/qemu
  if [[ -f "$ROOT_DIR/configs/libvirt/10-sanchos.conf" ]]; then
    install -m0644 "$ROOT_DIR/configs/libvirt/10-sanchos.conf" /etc/libvirt/libvirtd.conf.d/10-sanchos.conf
  fi
  if [[ -f "$ROOT_DIR/configs/network/qemu-bridge.conf" ]]; then
    install -m0644 "$ROOT_DIR/configs/network/qemu-bridge.conf" /etc/qemu/bridge.conf
  fi
}

install_sanchosctl() {
  install -Dm755 "$ROOT_DIR/packages/sanchosctl/sanchosctl/cli.py" /usr/local/bin/sanchosctl
}

install_desktop_vpn_client() {
  case "$PROFILE" in
    desktop|desktop-virt|dev)
      log "Installing NekoBox"
      "$ROOT_DIR/scripts/install-nekobox.sh"
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
    if [[ -n "${SUDO_USER:-}" ]] && id "$SUDO_USER" >/dev/null 2>&1; then
      usermod -aG libvirt "$SUDO_USER" || true
      usermod -aG kvm "$SUDO_USER" || true
    fi
  fi
}

main() {
  require_root
  "$ROOT_DIR/bootstrap/check-env.sh"

  if [[ ! -f "$PROFILE_FILE" ]]; then
    echo "Unknown profile: $PROFILE" >&2
    exit 1
  fi

  log "Installing bootstrap dependencies"
  install_base_packages

  log "Installing profile packages: $PROFILE"
  install_profile_packages

  log "Installing manifests and configs"
  install_manifests
  install_configs

  log "Installing sanchosctl"
  install_sanchosctl

  install_desktop_vpn_client

  log "Enabling profile services"
  enable_profile_services

  log "Bootstrap finished for profile: $PROFILE"
  log "Reboot is recommended before regular use."
}

main "$@"
