# Profiles

Profiles define installable system roles.

## `desktop`
A normal workstation profile with Plasma, desktop conveniences and NekoBox as the default GUI VPN client.

## `desktop-virt`
The main project profile. Extends the desktop path with libvirt, KVM, bridge helpers and the local VM toolchain.

## `dev`
Focused on development workflows and container-friendly tooling.

## `server-lite`
Minimal base for remote-first systems.

## Design note

Profiles should stay readable and boring. A profile is not a giant orchestration engine. It is a clean declaration of package sets, modules and expected settings.
