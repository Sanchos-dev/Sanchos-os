# ISO build

The repository now contains a first real ISO build path based on `live-build`.

## Host requirements

Build on a Debian 12 or Debian 13 machine with:

```bash
sudo apt update
sudo apt install -y live-build rsync debootstrap xorriso squashfs-tools
```

## Build

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

## Notes

This is still an early build path.

It is good for:
- boot testing
- installer path experiments
- validating package selection
- checking branding and desktop defaults

It is not yet a polished installer image with a custom setup flow.
