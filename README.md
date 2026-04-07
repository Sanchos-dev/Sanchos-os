# sanchos-os

sanchos-os is a Debian-based desktop operating system built around two goals:

- a warm, polished workstation experience
- local virtualization and self-hosted workflows without a split-brain UX

The project is built around a desktop-first model with native KVM/libvirt integration, modular features, and a small control plane for common host tasks.

## Current direction

- Debian 12 as the initial base
- Debian 13 as the next platform target
- KDE Plasma as the primary shell
- Plasma + i3 as the tiling-first desktop session in v9
- libvirt/KVM/QEMU for virtualization
- Podman and Distrobox for containers and dev environments
- NekoBox as the default desktop VPN client
- warm purple visuals, floating top panel, monochrome-friendly icon theme scaffold

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
- `sanchosctl` with profile, module, VM, wallpaper and visual workflows
- a control center that can apply wallpapers, visual presets and host tasks
- a first-boot flow that writes and applies the selected wallpaper and visual style
- branding, desktop defaults, Plasma wallpaper package sync and a monochrome icon theme scaffold
- a live ISO build path through Debian `live-build`

## Quick start

Use a clean Debian 12 VM for initial testing.

```bash
bash ./bootstrap/install.sh desktop-virt
sanchosctl system doctor
sanchosctl visual apply --apply-now
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

## Wallpaper and visual workflow

Place wallpapers under `branding/wallpapers/<collection>/` and let the install path rebuild `index.json` automatically.

Useful commands:

```bash
sudo sanchosctl wallpaper rescan
sanchosctl wallpaper list
sudo sanchosctl wallpaper set-default purple/purple0.png --apply
sudo sanchosctl visual apply --apply-now
sudo sanchosctl visual panel
sudo sanchosctl visual tiling enable
```

The install path mirrors the indexed wallpapers into `/usr/share/wallpapers/SanchosOs-*` so they show up as Plasma wallpaper packages.

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

See `docs/iso-build.md`, `docs/windows-build.md` and `docs/visual-customization.md`.

## Notes

- `nekobox` and `sanchos-control-center` must be launched inside a graphical KDE session, not from a plain SSH shell.
- v9 defaults to `purple/purple0.png` when that wallpaper exists.
- the tiling path in v9 uses **Plasma + i3**, not a minimal standalone window manager session.


## v10 visual direction

The default visual direction now prioritizes a polished KWin session with a floating top panel, warm purple colors, Kvantum-based rounded styling, monochrome icons and optional tiling. The scaffold no longer includes generated placeholder wallpapers; it expects the real wallpaper assets from your repository.
