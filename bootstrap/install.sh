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
    ca-certificates \
    rsync
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

install_wallpapers() {
  install -d /usr/share/backgrounds/sanchos-os /usr/share/wallpapers
  if [[ -d "$ROOT_DIR/branding/wallpapers" ]]; then
    rsync -a --delete --exclude 'index.json' "$ROOT_DIR/branding/wallpapers/" /usr/share/backgrounds/sanchos-os/
  fi
  if [[ -x "$ROOT_DIR/scripts/rebuild-wallpaper-index.py" ]]; then
    python3 "$ROOT_DIR/scripts/rebuild-wallpaper-index.py" /usr/share/backgrounds/sanchos-os >/dev/null
  fi
  if [[ -x "$ROOT_DIR/scripts/install-plasma-wallpaper-packages.py" ]]; then
    python3 "$ROOT_DIR/scripts/install-plasma-wallpaper-packages.py" /usr/share/backgrounds/sanchos-os /usr/share/wallpapers >/dev/null || true
  fi
}

install_icon_theme() {
  install -d /usr/share/icons/sanchos-mono
  if [[ -f "$ROOT_DIR/branding/icons/sanchos-mono/index.theme" ]]; then
    install -m0644 "$ROOT_DIR/branding/icons/sanchos-mono/index.theme" /usr/share/icons/sanchos-mono/index.theme
  fi
}

install_configs() {
  install -d /etc/libvirt/libvirtd.conf.d /etc/qemu /usr/share/sddm/themes/sanchos-os /usr/local/share/sanchos-os
  install -d /etc/skel/.config /etc/skel/.local/share/color-schemes /etc/skel/.config/i3 /etc/skel/.config/plasma-workspace/env
  if [[ -f "$ROOT_DIR/configs/libvirt/10-sanchos.conf" ]]; then
    install -m0644 "$ROOT_DIR/configs/libvirt/10-sanchos.conf" /etc/libvirt/libvirtd.conf.d/10-sanchos.conf
  fi
  if [[ -f "$ROOT_DIR/configs/network/qemu-bridge.conf" ]]; then
    install -m0644 "$ROOT_DIR/configs/network/qemu-bridge.conf" /etc/qemu/bridge.conf
  fi
  for name in kdeglobals kwinrc plasmarc; do
    if [[ -f "$ROOT_DIR/configs/plasma/${name}" ]]; then
      install -m0644 "$ROOT_DIR/configs/plasma/${name}" "/etc/skel/.config/${name}"
    fi
  done
  if [[ -f "$ROOT_DIR/configs/plasma/SanchosPurple.colors" ]]; then
    install -m0644 "$ROOT_DIR/configs/plasma/SanchosPurple.colors" /etc/skel/.local/share/color-schemes/SanchosPurple.colors
  fi
  if [[ -f "$ROOT_DIR/configs/i3/config" ]]; then
    install -m0644 "$ROOT_DIR/configs/i3/config" /etc/skel/.config/i3/config
  fi
  cat > /etc/skel/.config/plasma-workspace/env/90-sanchos-wm.sh <<'EOF'
#!/usr/bin/env sh
export KDEWM=/usr/bin/i3
EOF
  chmod +x /etc/skel/.config/plasma-workspace/env/90-sanchos-wm.sh
  install_wallpapers
  install_icon_theme
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
  install -d /usr/local/lib/sanchos-os
  install -Dm755 "$ROOT_DIR/firstboot/firstboot.py" /usr/local/lib/sanchos-os/firstboot.py
  install -Dm755 "$ROOT_DIR/ui/control-center/main.py" /usr/local/bin/sanchos-control-center
  install -Dm755 "$ROOT_DIR/bootstrap/uninstall.sh" /usr/local/share/sanchos-os/uninstall.sh
  install -Dm755 "$ROOT_DIR/scripts/apply-plasma-wallpaper.py" /usr/local/lib/sanchos-os/apply-plasma-wallpaper.py
  install -Dm755 "$ROOT_DIR/scripts/install-plasma-wallpaper-packages.py" /usr/local/lib/sanchos-os/install-plasma-wallpaper-packages.py
  install -Dm755 "$ROOT_DIR/scripts/apply-default-wallpaper.sh" /usr/local/lib/sanchos-os/apply-default-wallpaper.sh
  install -Dm755 "$ROOT_DIR/scripts/apply-plasma-layout.py" /usr/local/lib/sanchos-os/apply-plasma-layout.py
  install -Dm755 "$ROOT_DIR/scripts/configure-desktop-style.py" /usr/local/lib/sanchos-os/configure-desktop-style.py
  install -Dm755 "$ROOT_DIR/scripts/apply-visual-preset.sh" /usr/local/lib/sanchos-os/apply-visual-preset.sh
  install -Dm644 "$ROOT_DIR/configs/system/firstboot.desktop" /etc/xdg/autostart/sanchos-firstboot.desktop
  install -Dm644 "$ROOT_DIR/configs/system/apply-default-wallpaper.desktop" /etc/xdg/autostart/sanchos-apply-default-wallpaper.desktop
  install -Dm644 "$ROOT_DIR/configs/system/apply-visual-preset.desktop" /etc/xdg/autostart/sanchos-apply-visual-preset.desktop
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
  if [[ -z "$target_user" ]]; then
    target_user="$(awk -F: '$3 >= 1000 && $1 != "nobody" {print $1; exit}' /etc/passwd || true)"
  fi
  if [[ -n "$target_user" ]] && id "$target_user" >/dev/null 2>&1; then
    usermod -aG libvirt "$target_user" || true
    usermod -aG kvm "$target_user" || true
    printf '%s\n' "$target_user" > "$STATE_DIR/desktop-user"
    python3 "$ROOT_DIR/scripts/configure-desktop-style.py" --user "$target_user" --enable-tiling || true
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
  log "The v9 visual preset defaults to purple/purple0.png and a Plasma+i3 tiling session."
  log "Reboot is recommended before regular use."
}

main "$@"
