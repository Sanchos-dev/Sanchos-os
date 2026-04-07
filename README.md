# sanchos-os

sanchos-os is a Debian-based desktop operating system with native virtualization and modular service integration.

The project aims to combine a clean desktop environment with a local infrastructure workflow: a machine that works as a daily driver, a virtualization host, a container workstation and a control point for optional self-hosted services.

## Current focus

The repository currently contains the first project scaffold:
- roadmap documents
- profile manifests
- module manifests
- bootstrap scripts
- the first `sanchosctl` CLI skeleton

## Short-term priorities

1. make bootstrap repeatable on clean Debian 12 systems
2. mature `desktop-virt` into the main workstation profile
3. turn `sanchosctl` into the control plane for profiles and modules
4. package the core pieces as proper Debian packages
5. start the first native control center prototype

## Repository layout

- `roadmap/` — product direction and milestone planning
- `profiles/` — install roles and package bundles
- `modules/` — optional features and integrations
- `bootstrap/` — conversion of base Debian into sanchos-os
- `packages/` — Debian package sources and project-owned tools
- `configs/` — configuration templates for system components
- `docs/` — design notes for packaging, modules and virtualization

## Bootstrap on a test VM

Use a clean Debian 12 virtual machine and run:

```bash
sudo ./bootstrap/install.sh desktop-virt
```

After installation:

```bash
sanchosctl system info
sanchosctl system doctor
sanchosctl profile list
sanchosctl module list
```

## Status

This is early infrastructure work. The priority is a clean architecture and a usable bootstrap path, not surface polish.
