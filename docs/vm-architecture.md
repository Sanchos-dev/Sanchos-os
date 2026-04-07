# VM architecture

## Purpose

The first virtualization layer in `sanchos-os` is intentionally conservative. The goal is to expose a reliable local VM host on top of Debian without inventing another management stack too early.

## Stack

- KVM
- QEMU
- libvirt
- virsh
- virt-install
- virt-manager
- virt-viewer
- OVMF

## Host model

The host stays a regular desktop system. Virtualization is treated as a native subsystem, not as a separate appliance mode.

## Network modes

### Default NAT
Works out of the box and is the default path for early installs.

### Bridge mode
Available for desktop-virt systems where guests need to be visible on the local network.

The current repository version includes baseline bridge configuration templates under `configs/network/` and `configs/libvirt/`.

## CLI model

`sanchosctl vm ...` wraps a small subset of libvirt tools so routine actions do not require raw command memorization.

Current actions:
- `sanchosctl vm list`
- `sanchosctl vm networks`
- `sanchosctl vm info <name>`
- `sanchosctl vm create <name> --iso <path>`
- `sanchosctl vm start <name>`
- `sanchosctl vm stop <name>`
- `sanchosctl vm console <name>`
- `sanchosctl vm delete <name> --remove-storage --yes`
- `sanchosctl vm snapshot list <name>`
- `sanchosctl vm snapshot create <name> <snapshot>`
- `sanchosctl vm snapshot revert <name> <snapshot>`

## UI model

The control center now exposes:
- VM listing
- basic start and stop actions
- console launch
- snapshot visibility

This is still a local workstation model, not a cluster appliance model.

## Later work

Later milestones can add:
- templates
- image library handling
- storage pool management
- import/export flows
- a more complete graphical virtualization panel
