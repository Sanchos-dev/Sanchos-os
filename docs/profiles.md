# Profile model

## Purpose

Profiles define install roles.

A profile groups packages, modules and defaults that make sense together for a specific system role.

## Current profiles

- `desktop`
- `desktop-virt`
- `dev`
- `server-lite`

## Design rules

- profiles should describe intent clearly
- profiles should stay readable as plain manifests
- profiles should be installable through `sanchosctl`
- profiles should avoid hidden side effects

## Relationship to modules

Profiles describe a complete role.
Modules describe optional or reusable capabilities.

A profile can pull in several modules, but the module boundary should remain clean.
