# ISO build

The repository contains a real ISO build path based on `live-build`.

## Linux host requirements

On Debian 12 or Debian 13:

```bash
sudo bash scripts/setup-build-deps.sh
```

## Build on Linux or WSL

```bash
chmod +x scripts/build-iso.sh
sudo scripts/build-iso.sh build/live-build desktop-virt
```

The resulting image is written to:

```text
./dist/sanchos-os-desktop-virt.iso
```

## What the build does

- configures a Debian bookworm live image
- injects the repository into the chroot
- installs the desktop and virtualization packages
- runs `bootstrap/install.sh desktop-virt` inside the image build
- emits a hybrid ISO for BIOS/UEFI testing

## Windows host path

If your main machine is on Windows, use WSL and see `docs/windows-build.md`.

A PowerShell wrapper also exists:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-iso.ps1 -Distro Debian -Profile desktop-virt
```

## Notes

This is still an early build path.

It is good for:
- boot testing
- installer path experiments
- validating package selection
- checking branding and desktop defaults

It is not yet a polished installer image with a custom setup flow.
