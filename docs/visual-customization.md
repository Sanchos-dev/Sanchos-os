# Visual customization

## v10 direction

The default desktop now aims for:
- a warm dark-purple palette
- KWin as the polished default compositor
- a floating top panel
- Kvantum-based rounded widget styling
- monochrome icon inheritance
- optional tiling instead of forced tiling

## Wallpapers

The scaffold does not ship generated placeholder wallpapers anymore. Use the real assets from your repository under `branding/wallpapers/` and rebuild the index:

```bash
python3 scripts/rebuild-wallpaper-index.py branding/wallpapers
```

## Commands

```bash
sudo sanchosctl wallpaper rescan
sudo sanchosctl wallpaper set-default purple/purple0.png --apply
sudo sanchosctl visual apply --apply-now
```
