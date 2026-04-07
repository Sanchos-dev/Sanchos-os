# reset and test cleanup

The current test workflow assumes disposable Debian VMs.

## Recommended method

Use Proxmox snapshots instead of trying to fully scrub a machine by hand.

Suggested checkpoints:

- `clean-debian`
- `after-bootstrap`
- `after-vm-tests`

## In-guest reset path

For bootstrap-installed systems, the current reset path is:

```bash
sudo sanchosctl system reset --yes
```

or directly:

```bash
sudo bash ./bootstrap/uninstall.sh
```

The uninstall helper removes:

- `sanchosctl`
- control center and first-boot files
- branding assets placed by bootstrap
- NekoBox artifacts installed by the project helper
- package sets recorded in the bootstrap state directory

## Caveat

This is still a test-oriented cleanup path. Proxmox snapshots remain the preferred reset mechanism while the package model is being hardened.
