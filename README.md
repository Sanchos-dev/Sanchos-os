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

The repository now includes:

- a reproducible bootstrap path
- an uninstall/reset path for test machines
- `sanchosctl` with profile, module, VM and wallpaper workflows
- a first-pass control center that can apply wallpapers and drive host tasks
- a first-pass first-boot flow that writes and applies the selected wallpaper
- branding, desktop defaults and Plasma wallpaper package sync
- a live ISO build path through Debian `live-build`

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

## Wallpaper workflow

Place wallpapers under `branding/wallpapers/<collection>/` and let the install path rebuild `index.json` automatically.

Useful commands:

```bash
sudo sanchosctl wallpaper rescan
sanchosctl wallpaper list
sudo sanchosctl wallpaper set-default purple/purple0.png
sanchosctl wallpaper apply purple/purple0.png
sanchosctl wallpaper apply-default
```

The install path also mirrors the indexed wallpapers into `/usr/share/wallpapers/SanchosOs-*` so they show up as Plasma wallpaper packages.

## ISO builds

Linux and WSL build paths exist.

Linux:

```bash
sudo bash scripts/setup-build-deps.sh
sudo bash scripts/build-iso.sh build/live-build desktop-virt
```

Windows host via WSL wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-iso.ps1 -Distro Debian -Profile desktop-virt
```

See `docs/iso-build.md` and `docs/windows-build.md`.

## Notes

- `nekobox` and `sanchos-control-center` must be launched inside a graphical KDE session, not from a plain SSH shell.
- The wallpaper index is rebuilt during install so the control center, first-boot flow and Plasma packages stay in sync with the files that are actually present.
