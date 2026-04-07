# sanchos-os Vision

## What this project is

`sanchos-os` is a Debian-based operating system built for two roles at once:

- a clean, capable desktop system
- a local virtualization and service host

The target is not a stripped-down admin appliance and not a generic Linux remix. The target is a coherent operating platform that feels comfortable as a daily desktop while exposing infrastructure features in a way that makes sense on a workstation.

## Why it exists

Most desktop systems treat virtualization as an add-on. Most virtualization platforms treat desktop quality as irrelevant. `sanchos-os` is meant to sit between those extremes.

The system should let a user:

- work normally on the desktop
- spin up virtual machines and containers without friction
- manage storage and networking without hunting through unrelated tools
- plug in personal or self-hosted services through modules
- keep the overall system visually and behaviorally consistent

## Product principles

### Desktop comes first
The system must remain pleasant to use for normal everyday work.

### Virtualization is native
VMs, storage pools, network bridges and related tooling should be part of the product, not an afterthought.

### The platform stays modular
Extra capabilities belong in profiles and modules. The core should stay clear and maintainable.

### Integration must stay optional
Personal services and infrastructure hooks should be easy to add, but never hardwired into the base system.

### Defaults matter
The first impression should already feel intentional: boot flow, login, shell, desktop, settings and system tools should all belong to the same product.

## Initial product shape

The first practical release should provide:

- Debian 12 base
- KDE Plasma desktop
- KVM, QEMU and libvirt integration
- Podman and Distrobox
- `desktop-virt` profile
- `sanchosctl` command-line control plane
- the first branded desktop baseline

## What success looks like

A clean Debian install can be converted into a working `sanchos-os` prototype with one bootstrap path, and that prototype is good enough to use as a real desktop with native virtualization support.
