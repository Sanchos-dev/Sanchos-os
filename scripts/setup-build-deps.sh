#!/usr/bin/env bash
set -euo pipefail

apt-get update
apt-get install -y \
  live-build \
  rsync \
  debootstrap \
  xorriso \
  squashfs-tools
