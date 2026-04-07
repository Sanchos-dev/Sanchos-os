# Branding assets

This directory holds the visual layer for sanchos-os.

## Wallpapers

Put wallpaper sources under:

- `branding/wallpapers/default/`
- `branding/wallpapers/purple/`
- `branding/wallpapers/fox/`

Do not hand-edit `branding/wallpapers/index.json` unless you really need to. The install path rebuilds it from the files that actually exist.

Manual rebuild:

```bash
python3 scripts/rebuild-wallpaper-index.py branding/wallpapers
```

Installed target path:

```text
/usr/share/backgrounds/sanchos-os/
```
