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
- `ui/control-center/` local control center

## Current state

The repository has moved past pure documentation and now includes:

- a reproducible bootstrap path
- an uninstall/reset path for test machines
- `sanchosctl` with profile, module and VM workflows
- a first-pass control center
- a first-pass first-boot flow
- branding and desktop defaults

## Quick start

Use a clean Debian 12 VM for initial testing.

```bash
bash ./bootstrap/install.sh desktop-virt
sanchosctl system doctor
sanchosctl vm list
```

To remove the bootstrap content again on a test VM:

```bash
bash ./bootstrap/uninstall.sh
```

## Profiles

- `desktop`
- `desktop-virt`
- `dev`
- `server-lite`

## Notes

The project intentionally starts with standard Debian tooling instead of inventing custom plumbing too early.


## ISO builds

A first live ISO build path now exists through `scripts/build-iso.sh`. See `docs/iso-build.md`.

## Wallpaper workflow

Place wallpapers under `branding/wallpapers/<collection>/` and let the install path rebuild `index.json` automatically.

Useful commands:

```bash
sudo sanchosctl wallpaper rescan
sanchosctl wallpaper list
sudo sanchosctl wallpaper set-default purple/purple0.png
```

## Notes

- `nekobox` and `sanchos-control-center` must be launched inside a graphical KDE session, not from a plain SSH shell.
- The wallpaper index is rebuilt during install so the control center and first-boot flow stay in sync with the files that are actually present.
