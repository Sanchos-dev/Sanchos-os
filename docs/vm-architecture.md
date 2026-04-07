# VM architecture notes

## Goal

Virtualization is a first-class part of sanchos-os, but the first milestone should stay focused on local single-node workflows.

## Stack

- KVM
- QEMU
- libvirt
- OVMF
- virt-install
- virt-manager as a companion tool

## Initial use cases

- run Linux guests locally
- keep separate dev and test environments
- build disposable lab machines
- use bridged or NAT networking from a desktop host

## Product direction

The long-term objective is a desktop-oriented virtualization experience with system-integrated networking, storage and resource management.

The short-term objective is reliability, not feature count.
