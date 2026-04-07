# Modules

Modules are optional feature blocks that can be enabled on top of a profile.

## Rules

- a module owns a focused concern
- a module may depend on packages, services and config templates
- a module should be reversible where practical
- personal infrastructure is modeled as modules or overlays, not as hardcoded core behavior

## Current modules

### `virtualization`
Host-side VM stack based on libvirt.

### `containers`
Podman and Distrobox workflows.

### `vpn`
Base VPN tooling plus the project default desktop client path via NekoBox.

### `backup`
Reserved for backup integration.

### `monitoring`
Reserved for host and service monitoring.

### `mail`
Reserved for mail-related tooling or user workflow integration.
