# Packaging notes

## Package strategy

sanchos-os should stay aligned with standard Debian packaging.

The project-owned parts should be shipped as normal `.deb` packages through an APT repository rather than custom installers or opaque bundles.

## Early package set

- `sanchos-core`
- `sanchos-branding`
- `sanchos-theme`
- `sanchosctl`
- `sanchos-control-center`
- `sanchos-desktop`
- `sanchos-desktop-virt`

## Meta-packages vs owned packages

Profiles such as `desktop-virt` can start as manifests and later become meta-packages.

The project should keep its own code in dedicated packages and treat upstream software as dependencies rather than vendored payloads.

## Initial packaging priority

The first package worth maintaining is `sanchosctl`, because it acts as the control plane entry point and is already useful independently of the full UI.
