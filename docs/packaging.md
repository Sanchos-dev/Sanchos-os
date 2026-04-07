# Packaging

The packaging model for early `sanchos-os` is based on standard Debian packages and meta-packages.

## Principles

- stay close to Debian tooling
- avoid inventing a new packaging layer
- use meta-packages for profile composition
- keep project-owned packages small and clear

## Package families

- `sanchos-core`
- `sanchosctl`
- `sanchos-desktop`
- `sanchos-desktop-virt`
- `sanchos-theme`
- `sanchos-branding`

## NekoBox packaging note

NekoBox is not assumed to come from Debian main repositories. The repository currently treats it as a managed desktop artifact installed through `scripts/install-nekobox.sh` and the bootstrap flow. The long-term options are either shipping a project package that stages the AppImage cleanly or maintaining a dedicated external repository entry. The first milestone keeps this simple and reproducible. 
