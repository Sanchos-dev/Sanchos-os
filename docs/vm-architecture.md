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
- OVMF

## Host model

The host stays a regular desktop system. Virtualization is treated as a native subsystem, not as a separate appliance mode.

## Network modes

### Default NAT
Works out of the box and is the default path for early installs.

### Bridge mode
Available for desktop-virt systems where guests need to be visible on the local network.

The first repository version includes baseline bridge configuration templates under `configs/network/` and `configs/libvirt/`.

## CLI model

` sanchosctl vm ... ` wraps a small subset of `virsh` so routine actions do not require raw command memorization.

Supported initial actions:
- `sanchosctl vm list`
- `sanchosctl vm start <name>`
- `sanchosctl vm stop <name>`
- `sanchosctl vm info <name>`

## Later work

Later milestones can add:
- templates
- image library handling
- snapshot wrappers
- storage pool management
- a graphical virtualization panel
