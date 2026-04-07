#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${1:-$ROOT_DIR/build/live-build}"
PROFILE="${2:-desktop-virt}"
OUTPUT_DIR="$ROOT_DIR/dist"
IMAGE_NAME="sanchos-os-${PROFILE}"

log() {
  echo "[sanchos-os][iso] $*"
}

require_tool() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required tool: $1" >&2
    exit 1
  }
}

main() {
  require_tool lb
  require_tool rsync
  require_tool awk

  rm -rf "$WORK_DIR"
  mkdir -p "$WORK_DIR" "$OUTPUT_DIR"
  cd "$WORK_DIR"

  log "Configuring live-build for $PROFILE"
  lb config \
    --ignore-system-defaults \
    --distribution bookworm \
    --debian-installer live \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --bootappend-live "boot=live components quiet splash" \
    --linux-flavours amd64 \
    --iso-application "sanchos-os" \
    --iso-publisher "Sanchos" \
    --iso-volume "SANCHOS_OS"

  mkdir -p config/package-lists config/includes.chroot/etc/skel/.config config/includes.chroot/usr/local/src/sanchos-os config/hooks/live
  cp "$ROOT_DIR/configs/plasma/kdeglobals" config/includes.chroot/etc/skel/.config/kdeglobals
  rsync -a "$ROOT_DIR/" config/includes.chroot/usr/local/src/sanchos-os/ --exclude .git --exclude build --exclude dist

  cat > config/package-lists/sanchos.list.chroot <<EOF
sudo
curl
wget
git
python3
python3-yaml
python3-tk
network-manager
plasma-desktop
sddm
dolphin
konsole
kate
firefox-esr
plasma-nm
pipewire
pipewire-pulse
wireplumber
qemu-kvm
qemu-system-x86
libvirt-daemon-system
libvirt-clients
virtinst
virt-manager
virt-viewer
ovmf
bridge-utils
podman
EOF

  cat > config/hooks/live/9999-bootstrap.chroot <<EOF
#!/bin/sh
set -e
cd /usr/local/src/sanchos-os
chmod +x bootstrap/*.sh scripts/*.sh || true
bash bootstrap/install.sh ${PROFILE}
EOF
  chmod +x config/hooks/live/9999-bootstrap.chroot

  log "Building ISO (this can take a while)"
  lb build

  mv live-image-amd64.hybrid.iso "$OUTPUT_DIR/${IMAGE_NAME}.iso"
  log "ISO ready: $OUTPUT_DIR/${IMAGE_NAME}.iso"
}

main "$@"
