# sanchos-os Architecture

## 1. Vision

**sanchos-os** is a Debian-based operating system that combines a polished desktop experience with native virtualization and modular service integration.

The goal is to build a system that feels like a premium desktop Linux distribution while also acting as a local infrastructure node: a machine that can run virtual machines, containers, development environments, and self-hosted services without turning into a fragmented mess.

This project is **not** intended to reinvent Linux from scratch. It is intended to provide a coherent operating platform built from proven components with a unified user experience, opinionated defaults, and modular extensibility.

## 2. Product goals

### Primary goals

* Provide a clean, modern, visually strong desktop experience.
* Make virtualization a first-class system feature rather than an afterthought.
* Support both regular desktop use and advanced infrastructure workflows.
* Allow deep customization without sacrificing maintainability.
* Integrate optional personal/self-hosted services in a modular way.

### Non-goals for early versions

* Building a custom kernel.
* Building a custom package manager.
* Replacing systemd.
* Reimplementing a full Proxmox-like clustered platform in v0.x.
* Creating a new desktop environment from scratch.

## 3. Core principles

### Desktop-first

The system must be pleasant and usable as a daily driver.

### Virtualization-native

VMs, containers, networking, storage, and host management should be integrated into the product architecture.

### Modular

Features should be installable and removable as modules or profiles.

### Service-aware

The system should support optional integration with external infrastructure, domains, VPNs, mail systems, and self-hosted services.

### Sane defaults

The out-of-box experience should already feel polished.

### User-facing quality

Branding, theming, settings, boot flow, control center, and system tools should feel like one coherent product.

## 4. Base platform

### Base distribution

* Debian 12 as the first practical base.
* Debian 13 support planned as the next platform target.

### System foundations

* Linux kernel from Debian base.
* systemd as init and service manager.
* apt/dpkg for package management.
* AppArmor for baseline application confinement.
* PipeWire for audio stack.
* Wayland-first, with X11 compatibility when needed.

## 5. System layers

### Layer 1: Base OS

Provides the standard operating system foundation:

* kernel
* bootloader
* userspace
* package manager
* networking stack
* display stack
* service manager

### Layer 2: Sanchos Core

Defines the system identity and behavior:

* `sanchos-core` package
* branding assets
* defaults and policies
* shell environment
* baseline system configuration
* profile and module logic
* core CLI integration

### Layer 3: Desktop Layer

Defines the user-facing graphical environment:

* desktop environment
* theming
* file manager
* terminal
* login manager
* settings integration
* notifications and visual consistency

### Layer 4: Virtualization Layer

Provides local infrastructure capabilities:

* KVM/QEMU
* libvirt
* storage pools
* VM templates
* snapshots
* bridge/NAT network options
* desktop management integration

### Layer 5: Containers and Dev Layer

Provides application and development isolation:

* Podman
* optional Docker compatibility
* Distrobox for dev workflows
* container networking integration

### Layer 6: Services Layer

Provides optional integration with external infrastructure:

* VPN profiles
* SSH bootstrap
* backup integration
* monitoring agents
* mail tools
* service bookmarks or dashboards

### Layer 7: UX Control Layer

Provides a unified management experience:

* `sanchosctl`
* graphical control center
* first-boot wizard
* health checks
* diagnostics
* profile and module management

## 6. Editions and profiles

The system should avoid a monolithic installation model.

### Initial profiles

#### `desktop`

For regular daily desktop usage:

* polished GUI
* browser and standard desktop tools
* multimedia support
* minimal complexity

#### `desktop-virt`

Flagship profile for workstation + virtualization use:

* everything in `desktop`
* KVM/QEMU/libvirt stack
* VM management tools
* storage and networking helpers
* container stack

#### `dev`

For development-heavy workflows:

* compilers
* git
* editors
* containers
* development presets

#### `server-lite`

For minimal or semi-headless systems:

* reduced desktop footprint or optional no GUI
* remote-first workflows
* compatible with `sanchosctl`

## 7. Desktop architecture

### Recommended starting desktop stack

* KDE Plasma
* SDDM
* Dolphin
* Konsole
* Kate

### Why KDE Plasma

* visually flexible
* mature and stable
* highly customizable
* suitable for both power users and regular users
* strong base for a premium-feeling product

### Design direction

The desktop should feel:

* clean
* modern
* dark-theme friendly
* responsive
* modular
* visually distinct from stock Debian

## 8. Virtualization architecture

### Target model

The system should function as a desktop OS with built-in local virtualization management.

### Initial virtualization stack

* KVM
* QEMU
* libvirt
* OVMF/UEFI firmware support
* virt-install
* virt-manager as fallback or companion tool

### UX goals

The user should be able to:

* create VMs from a graphical wizard
* import ISO files
* assign CPU, memory, disks, and firmware options
* choose NAT or bridge networking
* create and restore snapshots
* view host and guest resource usage

### Scope boundaries for v0.x

Not in the first milestone:

* clustering
* HA
* live migration
* distributed storage
* full Proxmox-equivalent datacenter model

## 9. Container architecture

### Primary container stack

* Podman as default container runtime
* optional Docker compatibility layer
* Distrobox for desktop/dev environments

### Rationale

* Podman fits system integration and rootless flows well
* Distrobox improves developer usability on desktop systems
* containers should complement VMs rather than replace them

## 10. Storage architecture

### Recommended default

* btrfs for desktop-focused installations

### Benefits

* snapshots
* rollback support
* subvolumes
* practical layout separation
* useful for host and VM workflows

### Planned storage areas

* `/`
* `/home`
* `/var/lib/libvirt/images`
* `/var/lib/containers`
* `/srv/sanchos`
* `/var/backups`

### Future exploration

* optional ZFS support
* UI-driven snapshot management
* storage profiles for VM-heavy systems

## 11. Network architecture

The platform should support both standard desktop networking and virtualization-aware networking.

### Network modes

* normal desktop mode
* NAT-backed virtualization mode
* bridge mode for LAN-visible VMs
* service publishing mode for containers and tools

### User-facing needs

The control center should eventually expose:

* interface overview
* active DNS and gateway info
* bridge creation
* NAT/bridge selection per VM
* VPN profile management
* firewall overview

## 12. Security architecture

### Baseline approach

* least privilege by default
* AppArmor enabled
* firewall enabled by default where practical
* explicit privilege escalation for sensitive operations
* avoid hidden service integration

### Administrative model

Advanced features such as virtualization management should rely on controlled permissions rather than unrestricted root access.

## 13. Personal and external service integration

Personal infrastructure integration must be optional.

### Rule

No hardcoded dependency on one specific domain or service provider should exist inside the system core.

### Correct model

External services should be provided as modules or profile extensions.

### Example modules

* `vpn`
* `mail`
* `ssh-bootstrap`
* `backup`
* `monitoring`
* `cloud-links`

### Personal profile concept

A future `personal` or `infrastructure-profile` can connect the OS to a known service ecosystem without forcing that behavior for all users.

## 14. Command-line control plane

### `sanchosctl`

This is the main CLI entry point for operating system-level workflows.

### Initial responsibilities

* system info
* diagnostics
* profile management
* module management
* virtualization helpers
* service connection helpers
* update orchestration

### Example commands

```bash
sanchosctl system info
sanchosctl system doctor
sanchosctl profile list
sanchosctl profile apply desktop-virt
sanchosctl module list
sanchosctl module enable virtualization
sanchosctl vm list
sanchosctl vm create
sanchosctl vm start <name>
sanchosctl config export
```

### Initial implementation language

* Python

## 15. Graphical control center

### Purpose

The graphical control center should become the signature UX layer of sanchos-os.

### Sections for early design

* System
* Appearance
* Virtualization
* Containers
* Storage
* Network
* Services
* Backups
* Diagnostics
* Updates

### Early implementation direction

* Qt/QML preferred for deep desktop integration
* Tauri/Electron acceptable for rapid prototyping if necessary

## 16. Boot and onboarding flow

### First boot experience

The system should guide new users through:

* user setup
* theme selection
* update status
* profile confirmation
* optional virtualization enablement
* optional service integration
* basic backup recommendations

### Product experience goal

The system should feel intentionally designed from boot splash to desktop session.

## 17. Packaging and distribution model

### Packaging approach

* standard Debian packages
* custom APT repository
* meta-packages for profiles

### Planned package families

* `sanchos-core`
* `sanchos-branding`
* `sanchos-theme`
* `sanchosctl`
* `sanchos-control-center`
* `sanchos-desktop`
* `sanchos-desktop-virt`
* `sanchos-service-profiles`

## 18. Development workflow

### Recommended build path

Start with bootstrap and package composition, not a custom ISO.

### Phases

1. Clean Debian install
2. Bootstrap script converts base system into sanchos-os prototype
3. Profiles and modules become installable units
4. CLI management matures
5. GUI control center matures
6. Branded install image comes later

## 19. Repository structure

```text
sanchos-os/
├── README.md
├── roadmap/
│   ├── vision.md
│   ├── architecture.md
│   └── v0.1.md
├── bootstrap/
│   ├── install.sh
│   ├── postinstall.sh
│   └── check-env.sh
├── profiles/
│   ├── desktop.yaml
│   ├── desktop-virt.yaml
│   ├── dev.yaml
│   └── server-lite.yaml
├── modules/
│   ├── virtualization/
│   ├── containers/
│   ├── vpn/
│   ├── mail/
│   ├── backup/
│   └── monitoring/
├── packages/
│   ├── sanchos-core/
│   ├── sanchosctl/
│   ├── sanchos-theme/
│   ├── sanchos-branding/
│   └── sanchos-control-center/
├── configs/
│   ├── system/
│   ├── plasma/
│   ├── libvirt/
│   ├── podman/
│   └── network/
├── branding/
│   ├── icons/
│   ├── wallpapers/
│   ├── plymouth/
│   └── sddm/
├── ui/
│   └── control-center/
├── scripts/
│   ├── build-package.sh
│   ├── build-iso.sh
│   └── lint-configs.sh
└── docs/
    ├── packaging.md
    ├── modules.md
    ├── profiles.md
    └── vm-architecture.md
```

## 20. MVP target

### `v0.1`

A practical first milestone should include:

* Debian 12 base
* KDE Plasma desktop
* SDDM branding
* `sanchos-core`
* `sanchosctl` initial version
* `desktop-virt` profile
* KVM/QEMU/libvirt integration
* Podman integration
* btrfs recommended installation path
* first boot wizard concept or simple implementation
* basic control center shell

## 21. Immediate next steps

1. Create `roadmap/architecture.md` from this document.
2. Create `roadmap/vision.md` with a shorter product summary.
3. Define profile manifests in `profiles/`.
4. Create initial module manifests.
5. Build a bootstrap script for clean Debian 12.
6. Implement `sanchosctl` v0 in Python.
7. Validate the `desktop-virt` profile in a VM.

## 22. Summary

sanchos-os should be built as a Debian-based operating platform that unifies desktop quality, local virtualization, modular extensibility, and service-aware workflows.

The first successful version does not need to be massive. It needs to be coherent, usable, visually strong, and architecturally clean.
