# Visual customization

v12 focuses on a saner Plasma-first visual direction:

- Papirus-Dark icons instead of a fake mono placeholder theme
- warm purple color scheme
- Kvantum-backed rounded widgets
- floating centered top panel
- CustomTkinter control tools
- Rofi launcher on Meta+Space

## Notes

- The Control Center now runs desktop actions asynchronously to avoid UI freezes.
- The launcher uses an explicit dark theme file instead of inheriting rofi defaults.
- SDDM is pointed at the bundled `sanchos-os` theme through `/etc/sddm.conf.d/sanchos-os.conf`.
