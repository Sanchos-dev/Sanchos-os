# VM Architecture

The first virtualization baseline is built on:
- KVM
- QEMU
- libvirt
- OVMF

## Early user model
- workstation host runs normal desktop session
- guest systems run through libvirt
- NAT works out of the box
- bridge networking becomes a managed option

This is intentionally a workstation-first model, not a datacenter cluster design.
