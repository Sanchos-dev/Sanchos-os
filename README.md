# sanchos-os

Debian-based desktop platform with native virtualization and modular service integration.

`sanchos-os` is designed as a polished daily-driver desktop that can also act as a local virtualization host. The project is built around a simple idea: a Linux system should feel visually coherent, stay comfortable for normal desktop work, and expose infrastructure features without turning into a pile of unrelated tools.

## Direction

- Debian 12 as the initial base, with Debian 13 as the next target
- KDE Plasma as the primary desktop environment
- KVM, QEMU and libvirt as the virtualization foundation
- Podman and Distrobox for container and development workflows
- `sanchosctl` as the system control CLI
- Optional service modules for VPN, mail, backup and monitoring

## Project status

Early scaffold. The current focus is on architecture, profiles, bootstrap flow and the first working control tool.

## Planned milestones

- `v0.1` prototype on top of a clean Debian 12 install
- `desktop-virt` profile with working VM stack
- first usable `sanchosctl`
- branded desktop baseline
- initial control-center shell

## Repository layout

- `roadmap/` — product and architecture documents
- `bootstrap/` — conversion of base Debian into a sanchos-os prototype
- `profiles/` — installable role definitions
- `modules/` — optional feature blocks
- `packages/` — system packages maintained by the project
- `configs/` — managed configuration templates
- `branding/` — visual assets
- `ui/` — graphical management layer
- `docs/` — implementation notes

## Working rule

Do not try to outgrow the architecture too early. The first job is to make a clean, usable workstation with native virtualization. Clustering, HA and bigger orchestration features can come later.
