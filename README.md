# sanchos-os

sanchos-os is a Debian-based desktop operating system focused on two things:

- a clean, usable workstation experience
- local virtualization and self-hosted workflows without a split-brain UX

The project is built around a desktop-first model with native KVM/libvirt integration, modular features, and a small control plane for common host tasks.

## Current direction

- Debian 12 as the initial base
- Debian 13 as the next platform target
- KDE Plasma as the primary desktop
- libvirt/KVM/QEMU for virtualization
- Podman and Distrobox for containers and dev environments
- NekoBox as the default desktop VPN client

## Repository layout

- `roadmap/` product and platform documents
- `profiles/` install profiles
- `modules/` optional feature modules
- `bootstrap/` scripts for turning a clean Debian install into sanchos-os
- `packages/` package sources and packaging scaffolds
- `configs/` system, desktop, networking and virtualization defaults
- `firstboot/` first session setup flow
- `ui/control-center/` early control center prototype

## Current state

This repository is the early platform scaffold. The main goals right now are:

- lock down the platform architecture
- make the bootstrap path reproducible
- grow `sanchosctl` into a practical host management tool
- build the first branded desktop session

## Quick start

Use a clean Debian 12 VM for initial testing.

```bash
sudo ./bootstrap/install.sh desktop-virt
sudo sanchosctl system doctor
sudo sanchosctl vm list
```

## Profiles

- `desktop`
- `desktop-virt`
- `dev`
- `server-lite`

## Notes

The project intentionally starts with standard Debian tooling instead of inventing custom plumbing too early.
