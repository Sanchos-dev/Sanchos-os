# sanchosctl

`sanchosctl` is the local control plane for `sanchos-os`.

## Current commands

### system
- `sanchosctl system info`
- `sanchosctl system doctor`
- `sanchosctl system reset --yes`

### profile
- `sanchosctl profile list`
- `sanchosctl profile info <name>`
- `sanchosctl profile apply <name>`

### module
- `sanchosctl module list`
- `sanchosctl module info <name>`
- `sanchosctl module enable <name>`

### vm
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

## Notes

The current version is intentionally thin. It wraps the workflows the repository already defines and stays close to standard libvirt tooling.
