# sanchos-os Architecture

## 1. Overview

`sanchos-os` is a Debian-based operating platform built around a dual-role design: a polished desktop environment on one side and a virtualization-capable local infrastructure node on the other.

The system should feel natural as a daily workstation while exposing first-class support for virtual machines, containers, storage layout and network management. The architecture is intentionally layered so the project can grow without turning monolithic.

## 2. Goals

### Product goals
- provide a strong desktop experience
- make virtualization a native feature
- support modular service integration
- keep the system maintainable
- allow future packaging and branding growth

### Non-goals for early milestones
- custom kernel work
- custom package manager
- replacing systemd
- full Proxmox-level datacenter features in `v0.x`
- writing a desktop environment from scratch

## 3. Base platform

### Distribution base
- Debian 12 for the first practical target
- Debian 13 as the next platform target

### Core platform choices
- systemd
- apt and dpkg
- AppArmor
- PipeWire
- Wayland-first desktop direction with X11 compatibility where required

## 4. System layers

### Layer 1 — Base OS
Standard Debian userspace and system components.

### Layer 2 — Sanchos Core
Project identity, defaults, shell environment, profile and module logic, and base project packages.

### Layer 3 — Desktop Layer
Graphical session, theming, login manager, file manager, terminal, desktop utilities and visual integration.

### Layer 4 — Virtualization Layer
KVM, QEMU, libvirt, firmware support, storage pools, snapshot handling and network modes for guest systems.

### Layer 5 — Containers and Dev Layer
Podman, optional Docker compatibility and Distrobox for development-oriented user environments.

### Layer 6 — Services Layer
Optional infrastructure integration such as VPN, mail, backup, monitoring and SSH bootstrap.

### Layer 7 — Control Layer
`sanchosctl`, future graphical control center, diagnostics, onboarding and profile management.

## 5. Desktop architecture

### Initial desktop stack
- KDE Plasma
- SDDM
- Dolphin
- Konsole
- Kate

### Rationale
KDE Plasma is mature, flexible and capable of supporting both power-user workflows and a more polished mainstream presentation.

## 6. Virtualization architecture

### Initial stack
- KVM
- QEMU
- libvirt
- OVMF
- virt-install
- virt-manager as a companion tool

### Design target
Virtualization should be available as part of the workstation model. The user should not need to assemble unrelated admin tools by hand just to manage guest systems.

### Early boundary
The system is not trying to replicate clustering, HA or multi-node orchestration in the first milestones.

## 7. Container architecture

### Initial stack
- Podman
- Distrobox
- optional Docker compatibility later

### Role in the product
Containers complement the desktop and VM workflows. They are not a replacement for proper VM isolation.

## 8. Storage architecture

### Default direction
- btrfs for desktop-focused installations

### Practical layout
- `/`
- `/home`
- `/var/lib/libvirt/images`
- `/var/lib/containers`
- `/srv/sanchos`
- `/var/backups`

### Notes
ZFS can be explored later as an optional path, not as a hard requirement in the first release.

## 9. Network architecture

The system must support both normal desktop networking and virtualization-aware networking.

### Supported modes
- standard desktop mode
- NAT-backed VM mode
- bridge mode for LAN-visible guests
- service publishing mode for local tools and containers

## 10. Security model

### Baseline
- least privilege by default
- AppArmor enabled
- explicit elevation for sensitive actions
- avoid hidden service coupling in the base install

## 11. Profiles

### `desktop`
General desktop system.

### `desktop-virt`
Desktop plus full local virtualization baseline.

### `dev`
Development-oriented tooling.

### `server-lite`
Reduced footprint for service-oriented machines.

## 12. Modules

Modules extend the base system without bloating the core.

Initial module families:
- virtualization
- containers
- vpn
- mail
- backup
- monitoring

Each module should eventually have:
- manifest
- packages list
- config templates
- enable and disable logic

## 13. Control plane

### CLI
`sanchosctl` is the main management entry point in early milestones.

### Planned CLI roles
- system info
- diagnostics
- profile listing
- module listing
- virtualization checks

### GUI
A graphical control center is planned as a later layer, but the project should not block on it.

## 14. Packaging

### Package model
- standard Debian packages
- project APT repository later
- meta-packages for roles and profiles

Planned package families:
- `sanchos-core`
- `sanchos-branding`
- `sanchos-theme`
- `sanchosctl`
- `sanchos-control-center`
- `sanchos-desktop`
- `sanchos-desktop-virt`

## 15. Build path

The first build path is bootstrap-first, not ISO-first.

### Sequence
1. install clean Debian 12
2. run bootstrap scripts
3. apply profile and module baseline
4. validate desktop and virtualization features
5. iterate on packaging
6. introduce branded install media later

## 16. Summary

The first successful version of `sanchos-os` should be small but coherent: a strong Debian desktop with native virtualization, modular service hooks and a clean foundation for future growth.
