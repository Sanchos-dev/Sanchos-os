# Windows build path

The supported Windows workflow is:

1. install WSL2
2. install a Debian WSL distro
3. clone the repository inside the WSL filesystem
4. run the ISO build from WSL, or call the PowerShell wrapper that dispatches the build into WSL

## Recommended setup

Open an elevated PowerShell window and install WSL:

```powershell
wsl --install
```

If you want to install Debian explicitly:

```powershell
wsl --install -d Debian
```

After Windows restarts, open the Debian WSL terminal once and finish the user setup.

## Clone the repository inside WSL

Inside Debian WSL:

```bash
git clone https://github.com/Sanchos-dev/Sanchos-os.git
cd Sanchos-os
chmod +x scripts/*.sh bootstrap/*.sh
```

## Install build dependencies inside WSL

```bash
sudo bash scripts/setup-build-deps.sh
```

## Build the ISO inside WSL

```bash
sudo bash scripts/build-iso.sh build/live-build desktop-virt
```

The resulting image is written to:

```text
./dist/sanchos-os-desktop-virt.iso
```

## Optional PowerShell wrapper

From Windows PowerShell in the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-iso.ps1 -Distro Debian -Profile desktop-virt
```

This wrapper resolves the repository path into WSL and runs the same Debian build path there.

## Notes

- The fastest and least painful workflow is to keep the repository in the WSL filesystem, not under `/mnt/c/...`.
- The ISO build still happens in Linux through `live-build`; the PowerShell script is only a launcher.
