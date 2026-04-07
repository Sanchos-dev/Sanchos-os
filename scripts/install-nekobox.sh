#!/usr/bin/env bash
set -euo pipefail

NEKOBOX_VERSION="${NEKOBOX_VERSION:-5.10.32}"
NEKOBOX_ARCH="${NEKOBOX_ARCH:-x86_64}"
INSTALL_DIR="/opt/nekobox"
APPIMAGE_NAME="nekobox-${NEKOBOX_VERSION}-${NEKOBOX_ARCH}-linux.AppImage"
DOWNLOAD_URL="https://github.com/qr243vbi/nekobox/releases/download/${NEKOBOX_VERSION}/${APPIMAGE_NAME}"

log() {
  echo "[nekobox] $*"
}

require_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run this script as root." >&2
    exit 1
  fi
}

main() {
  require_root
  apt-get update
  apt-get install -y curl ca-certificates libfuse2 || apt-get install -y curl ca-certificates

  install -d "$INSTALL_DIR"
  curl -L "$DOWNLOAD_URL" -o "$INSTALL_DIR/nekobox.AppImage"
  chmod 0755 "$INSTALL_DIR/nekobox.AppImage"

  cat > /usr/local/bin/nekobox <<'SH'
#!/usr/bin/env sh
exec /opt/nekobox/nekobox.AppImage "$@"
SH
  chmod 0755 /usr/local/bin/nekobox

  cat > /usr/share/applications/nekobox.desktop <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=NekoBox
Comment=Proxy and VPN client
Exec=/usr/local/bin/nekobox
Icon=network-vpn
Terminal=false
Categories=Network;
StartupNotify=true
DESKTOP

  log "Installed NekoBox ${NEKOBOX_VERSION}"
}

main "$@"
