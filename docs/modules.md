# Module model

## Purpose

Modules provide optional system capabilities without forcing them into the core product.

A module can install packages, enable services and expose a stable name for higher-level tooling.

## Rules

- every module must have a `module.yaml`
- modules must be understandable without reading shell scripts
- personal infrastructure must never be hardcoded into the core modules
- modules should be composable with profiles

## Current layout

Each module currently defines:
- `name`
- `description`
- `packages`
- `services`
- `notes`

## Planned additions

Later revisions can add:
- dependency relationships
- post-install hooks
- rollback actions
- UI metadata for the control center
