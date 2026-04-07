# Visual customization in v9

v9 pushes sanchos-os toward a softer Plasma+i3 hybrid desktop:

- purple-first wallpaper defaults (`purple/purple0.png` when present)
- floating top panel layout for Plasma
- i3 as the tiling window manager under Plasma on X11 sessions
- warm purple color scheme and darker translucent surfaces
- monochrome icon theme scaffold (`sanchos-mono` inherits from `breeze-dark`)
- SDDM theme tuned toward purple tones

## Important note about tiling

The tiling path in v9 uses **Plasma + i3**:

- Plasma still provides widgets, panel, tray, launchers and the desktop shell
- i3 manages window tiling and keyboard-driven placement

This keeps the system much closer to a polished desktop than replacing the whole shell with a minimal compositor.

## Commands

```bash
sudo sanchosctl visual apply
sudo sanchosctl visual panel
sudo sanchosctl visual tiling enable
sanchosctl wallpaper apply-default
```

## Windows build note

Build the ISO from **WSL Debian** rather than from PowerShell directly. Keep the repository inside the WSL filesystem for best performance.
