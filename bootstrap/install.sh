#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${1:-desktop-virt}"
PROFILE_FILE="$ROOT_DIR/profiles/${PROFILE}.yaml"
STATE_DIR="/etc/sanchos-os/state"
UI_VENV="/opt/sanchos-os/venv"
log(){ echo "[sanchos-os] $*"; }
require_root(){ [[ "$(id -u)" -eq 0 ]] || { echo "Run this script as root." >&2; exit 1; }; }
read_profile_value(){ local key="$1"; python3 - "$PROFILE_FILE" "$key" <<'PY'
import sys, yaml
from pathlib import Path
path = Path(sys.argv[1]); key = sys.argv[2]
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
install_base_packages(){ apt-get update; apt-get install -y python3 python3-yaml python3-tk python3-venv sudo curl wget git ca-certificates rsync; }
install_profile_packages(){ mapfile -t packages < <(read_profile_value packages); if [[ ${#packages[@]} -gt 0 ]]; then apt-get install -y "${packages[@]}"; printf '%s
' "${packages[@]}" > "$STATE_DIR/profile-packages"; else : > "$STATE_DIR/profile-packages"; fi; }
install_python_ui_runtime(){ log "Preparing CustomTkinter runtime"; mkdir -p /opt/sanchos-os; python3 -m venv "$UI_VENV"; "$UI_VENV/bin/pip" install --upgrade pip >/dev/null; "$UI_VENV/bin/pip" install --upgrade customtkinter pillow >/dev/null; printf '%s
' "$UI_VENV" > "$STATE_DIR/ui-venv"; }
install_manifests(){ install -d "$STATE_DIR"; rm -rf /etc/sanchos-os/profiles /etc/sanchos-os/modules /etc/sanchos-os/configs /etc/sanchos-os/branding; cp -r "$ROOT_DIR/profiles" /etc/sanchos-os/; cp -r "$ROOT_DIR/modules" /etc/sanchos-os/; cp -r "$ROOT_DIR/configs" /etc/sanchos-os/; cp -r "$ROOT_DIR/branding" /etc/sanchos-os/; printf '%s
' "$PROFILE" > "$STATE_DIR/installed-profile"; }
install_wallpapers(){ install -d /usr/share/backgrounds/sanchos-os /usr/share/wallpapers; if [[ -d "$ROOT_DIR/branding/wallpapers" ]]; then rsync -a --delete --exclude 'index.json' "$ROOT_DIR/branding/wallpapers/" /usr/share/backgrounds/sanchos-os/; fi; if [[ -x "$ROOT_DIR/scripts/rebuild-wallpaper-index.py" ]]; then python3 "$ROOT_DIR/scripts/rebuild-wallpaper-index.py" /usr/share/backgrounds/sanchos-os >/dev/null; fi; if [[ -x "$ROOT_DIR/scripts/install-plasma-wallpaper-packages.py" ]]; then python3 "$ROOT_DIR/scripts/install-plasma-wallpaper-packages.py" /usr/share/backgrounds/sanchos-os /usr/share/wallpapers >/dev/null || true; fi; }
install_icon_theme(){ install -d /usr/share/icons/sanchos-mono; [[ -f "$ROOT_DIR/branding/icons/sanchos-mono/index.theme" ]] && install -m0644 "$ROOT_DIR/branding/icons/sanchos-mono/index.theme" /usr/share/icons/sanchos-mono/index.theme; }
install_configs(){
  install -d /etc/libvirt/libvirtd.conf.d /etc/qemu /etc/sddm.conf.d /usr/share/sddm/themes/sanchos-os /usr/local/share/sanchos-os
  install -d /etc/skel/.config /etc/skel/.local/share/color-schemes /etc/skel/.config/plasma-workspace/env /etc/skel/.config/Kvantum /etc/skel/.config/gtk-3.0 /etc/skel/.local/share/konsole /etc/skel/.config/rofi
  [[ -f "$ROOT_DIR/configs/libvirt/10-sanchos.conf" ]] && install -m0644 "$ROOT_DIR/configs/libvirt/10-sanchos.conf" /etc/libvirt/libvirtd.conf.d/10-sanchos.conf
  [[ -f "$ROOT_DIR/configs/network/qemu-bridge.conf" ]] && install -m0644 "$ROOT_DIR/configs/network/qemu-bridge.conf" /etc/qemu/bridge.conf
  for name in kdeglobals kwinrc plasmarc kscreenlockerrc; do [[ -f "$ROOT_DIR/configs/plasma/${name}" ]] && install -m0644 "$ROOT_DIR/configs/plasma/${name}" "/etc/skel/.config/${name}"; done
  for color in SanchosPurple.colors SanchosWarm.colors; do [[ -f "$ROOT_DIR/configs/plasma/${color}" ]] && install -m0644 "$ROOT_DIR/configs/plasma/${color}" "/etc/skel/.local/share/color-schemes/${color}"; done
  [[ -f "$ROOT_DIR/configs/plasma/konsolerc" ]] && install -m0644 "$ROOT_DIR/configs/plasma/konsolerc" /etc/skel/.config/konsolerc
  [[ -f "$ROOT_DIR/configs/plasma/SanchosDark.profile" ]] && install -m0644 "$ROOT_DIR/configs/plasma/SanchosDark.profile" /etc/skel/.local/share/konsole/SanchosDark.profile
  [[ -f "$ROOT_DIR/configs/plasma/gtk-settings.ini" ]] && install -m0644 "$ROOT_DIR/configs/plasma/gtk-settings.ini" /etc/skel/.config/gtk-3.0/settings.ini
  [[ -f "$ROOT_DIR/configs/plasma/kvantum.kvconfig" ]] && install -m0644 "$ROOT_DIR/configs/plasma/kvantum.kvconfig" /etc/skel/.config/Kvantum/kvantum.kvconfig
  for name in config.rasi sanchos-launcher.rasi; do [[ -f "$ROOT_DIR/configs/rofi/${name}" ]] && install -m0644 "$ROOT_DIR/configs/rofi/${name}" "/etc/skel/.config/rofi/${name}"; done
  [[ -f "$ROOT_DIR/configs/system/xbindkeysrc" ]] && install -m0644 "$ROOT_DIR/configs/system/xbindkeysrc" /etc/skel/.config/xbindkeysrc
  install_wallpapers
  install_icon_theme
  if [[ -d "$ROOT_DIR/themes/kvantum/SanchosRounded" ]]; then install -d /usr/share/Kvantum/SanchosRounded; cp -r "$ROOT_DIR/themes/kvantum/SanchosRounded/." /usr/share/Kvantum/SanchosRounded/; fi
  [[ -f "$ROOT_DIR/branding/sddm/Main.qml" ]] && install -m0644 "$ROOT_DIR/branding/sddm/Main.qml" /usr/share/sddm/themes/sanchos-os/Main.qml
  [[ -f "$ROOT_DIR/branding/sddm/metadata.desktop" ]] && install -m0644 "$ROOT_DIR/branding/sddm/metadata.desktop" /usr/share/sddm/themes/sanchos-os/metadata.desktop
  [[ -f "$ROOT_DIR/branding/sddm/theme.conf" ]] && install -m0644 "$ROOT_DIR/branding/sddm/theme.conf" /usr/share/sddm/themes/sanchos-os/theme.conf
  [[ -f "$ROOT_DIR/configs/system/sddm-sanchos.conf" ]] && install -m0644 "$ROOT_DIR/configs/system/sddm-sanchos.conf" /etc/sddm.conf.d/sanchos-os.conf
  printf 'profile=%s
installed_at=%s
' "$PROFILE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /usr/local/share/sanchos-os/install.env
}
install_sanchosctl(){ install -Dm755 "$ROOT_DIR/packages/sanchosctl/sanchosctl/cli.py" /usr/local/bin/sanchosctl; }
install_ui_bits(){
  install -d /usr/local/lib/sanchos-os
  install -Dm755 "$ROOT_DIR/firstboot/firstboot.py" /usr/local/lib/sanchos-os/firstboot.py
  install -Dm755 "$ROOT_DIR/ui/control-center/main.py" /usr/local/lib/sanchos-os/control-center.py
  install -Dm755 "$ROOT_DIR/scripts/launch-control-center.sh" /usr/local/bin/sanchos-control-center
  install -Dm755 "$ROOT_DIR/scripts/launch-firstboot.sh" /usr/local/bin/sanchos-firstboot
  install -Dm755 "$ROOT_DIR/bootstrap/uninstall.sh" /usr/local/share/sanchos-os/uninstall.sh
  install -Dm755 "$ROOT_DIR/scripts/apply-plasma-wallpaper.py" /usr/local/lib/sanchos-os/apply-plasma-wallpaper.py
  install -Dm755 "$ROOT_DIR/scripts/install-plasma-wallpaper-packages.py" /usr/local/lib/sanchos-os/install-plasma-wallpaper-packages.py
  install -Dm755 "$ROOT_DIR/scripts/apply-default-wallpaper.sh" /usr/local/lib/sanchos-os/apply-default-wallpaper.sh
  install -Dm755 "$ROOT_DIR/scripts/apply-plasma-layout.py" /usr/local/lib/sanchos-os/apply-plasma-layout.py
  install -Dm755 "$ROOT_DIR/scripts/configure-desktop-style.py" /usr/local/lib/sanchos-os/configure-desktop-style.py
  install -Dm755 "$ROOT_DIR/scripts/apply-visual-preset.sh" /usr/local/lib/sanchos-os/apply-visual-preset.sh
  install -Dm755 "$ROOT_DIR/scripts/sanchos-launcher" /usr/local/bin/sanchos-launcher
  install -Dm644 "$ROOT_DIR/configs/system/firstboot.desktop" /etc/xdg/autostart/sanchos-firstboot.desktop
  install -Dm644 "$ROOT_DIR/configs/system/apply-default-wallpaper.desktop" /etc/xdg/autostart/sanchos-apply-default-wallpaper.desktop
  install -Dm644 "$ROOT_DIR/configs/system/apply-visual-preset.desktop" /etc/xdg/autostart/sanchos-apply-visual-preset.desktop
  install -Dm644 "$ROOT_DIR/configs/system/xbindkeys.desktop" /etc/xdg/autostart/sanchos-xbindkeys.desktop
  install -Dm644 "$ROOT_DIR/configs/system/control-center.desktop" /usr/share/applications/sanchos-control-center.desktop
}
install_desktop_vpn_client(){ case "$PROFILE" in desktop|desktop-virt|dev) log "Installing NekoBox"; "$ROOT_DIR/scripts/install-nekobox.sh"; printf '%s
' nekobox > "$STATE_DIR/external-artifacts";; esac; }
enable_profile_services(){
  case "$PROFILE" in desktop|desktop-virt|dev) systemctl enable sddm || true; systemctl enable NetworkManager || true;; esac
  if [[ "$PROFILE" == "desktop-virt" ]]; then systemctl enable libvirtd || true; systemctl start libvirtd || true; fi
  local target_user="${SUDO_USER:-${PKEXEC_UID:-}}"
  if [[ -z "$target_user" && -n "${USER:-}" && "$USER" != "root" ]]; then target_user="$USER"; fi
  if [[ -z "$target_user" ]]; then target_user="$(awk -F: '$3 >= 1000 && $1 != "nobody" {print $1; exit}' /etc/passwd || true)"; fi
  if [[ -n "$target_user" ]] && id "$target_user" >/dev/null 2>&1; then usermod -aG libvirt "$target_user" || true; usermod -aG kvm "$target_user" || true; printf '%s
' "$target_user" > "$STATE_DIR/desktop-user"; python3 "$ROOT_DIR/scripts/configure-desktop-style.py" --user "$target_user" || true; fi
}
run_postinstall(){ "$ROOT_DIR/bootstrap/postinstall.sh" || true; }
main(){
  require_root; "$ROOT_DIR/bootstrap/check-env.sh"
  [[ -f "$PROFILE_FILE" ]] || { echo "Unknown profile: $PROFILE" >&2; exit 1; }
  install -d "$STATE_DIR"
  log "Installing bootstrap dependencies"; install_base_packages
  log "Installing profile packages: $PROFILE"; install_profile_packages
  install_python_ui_runtime
  log "Installing manifests and configs"; install_manifests; install_configs
  log "Installing control tooling"; install_sanchosctl; install_ui_bits
  install_desktop_vpn_client
  log "Enabling profile services"; enable_profile_services
  log "Running post-install hooks"; run_postinstall
  log "Bootstrap finished for profile: $PROFILE"
  log "The v12 visual preset focuses on polished Plasma, Papirus icons, a translucent top panel, a warm SDDM theme and a repaired launcher/control center flow."
  log "Reboot is recommended before regular use."
}
main "$@"
