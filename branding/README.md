# Branding assets

This directory holds the visual layer for sanchos-os.

## Wallpapers

Put wallpaper sources under:

- `branding/wallpapers/default/`
- `branding/wallpapers/purple/`
- `branding/wallpapers/fox/`

Do not hand-edit `branding/wallpapers/index.json` unless you really need to. The install path rebuilds it from the files that actually exist.

In v9 the preferred default is `purple/purple0.png` when that file exists.

Manual rebuild in the repository:

```bash
python3 scripts/rebuild-wallpaper-index.py branding/wallpapers
```

Installed target paths:

```text
/usr/share/backgrounds/sanchos-os/
/usr/share/wallpapers/SanchosOs-*/
/usr/share/icons/sanchos-mono/
```

Useful runtime commands:

```bash
sudo sanchosctl wallpaper rescan
sanchosctl wallpaper list
sudo sanchosctl wallpaper set-default purple/purple0.png --apply
sudo sanchosctl visual apply
sudo sanchosctl visual tiling enable
```
