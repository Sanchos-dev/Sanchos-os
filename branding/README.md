# Branding assets

This directory holds the visual layer for sanchos-os.

## Wallpapers

Put wallpaper sources under:

- `branding/wallpapers/default/`
- `branding/wallpapers/purple/`
- `branding/wallpapers/fox/`

Do not hand-edit `branding/wallpapers/index.json` unless you really need to. The install path rebuilds it from the files that actually exist.

Manual rebuild in the repository:

```bash
python3 scripts/rebuild-wallpaper-index.py branding/wallpapers
```

Installed target paths:

```text
/usr/share/backgrounds/sanchos-os/
/usr/share/wallpapers/SanchosOs-*/
```

The first path holds the raw wallpaper assets used by first boot and the control center.
The second path holds generated Plasma wallpaper packages so the images also show up in the native KDE wallpaper picker.

Useful runtime commands:

```bash
sudo sanchosctl wallpaper rescan
sanchosctl wallpaper list
sudo sanchosctl wallpaper set-default default/wp0.png
sanchosctl wallpaper apply default/wp0.png
sanchosctl wallpaper apply-default
```
