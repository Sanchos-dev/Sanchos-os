# sanchos-os

Debian-based desktop platform with native virtualization and modular service integration.

`sanchos-os` is built as a daily-driver Linux system that also acts as a local virtualization host. The project aims to keep the desktop polished, the infra stack usable, and the repository maintainable.

## Current direction

- Debian 12 as the first base, with Debian 13 as the next target
- KDE Plasma as the main desktop
- KVM, QEMU and libvirt as the virtualization baseline
- Podman and Distrobox for container and development workflows
- `sanchosctl` as the system control CLI
- NekoBox as the default desktop VPN client
- optional service modules for VPN, mail, backup and monitoring

## Project status

Early scaffold. Current work is focused on repository structure, bootstrap flow, profile manifests, first packaging, and the initial control tooling.

## Working rule

The first release should solve one job well: turn a clean Debian installation into a coherent workstation with native virtualization and a stable desktop. Anything bigger can wait until the basics stop moving.
