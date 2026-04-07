#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tkinter import Button, Checkbutton, IntVar, Label, OptionMenu, StringVar, Tk

STATE_DIR = Path.home() / '.config' / 'sanchos-os'
STATE_FILE = STATE_DIR / 'firstboot.json'
WALLPAPER_INDEX = Path('/usr/share/backgrounds/sanchos-os/index.json')
PROFILES = ['desktop', 'desktop-virt', 'dev', 'server-lite']


def run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=False)
    except Exception:
        pass


def save_state(data: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2) + '\n')


def load_wallpapers() -> list[str]:
    try:
        data = json.loads(WALLPAPER_INDEX.read_text())
        items: list[str] = []
        for values in data.get('collections', {}).values():
            items.extend(values)
        return items or [data.get('default', 'default/sanchos-default.svg')]
    except Exception:
        return ['default/sanchos-default.svg']


def main() -> None:
    if STATE_FILE.exists():
        return

    root = Tk()
    root.title('sanchos-os setup')
    root.geometry('720x500')
    root.resizable(False, False)

    Label(root, text='Welcome to sanchos-os', font=('Sans', 18, 'bold')).pack(pady=(18, 6))
    Label(root, text='Set the baseline for this machine.', font=('Sans', 11)).pack(pady=(0, 16))

    theme_var = StringVar(value='dark')
    profile_var = StringVar(value='desktop-virt')
    wallpaper_options = load_wallpapers()
    wallpaper_var = StringVar(value=wallpaper_options[0])

    Label(root, text='Theme mode').pack()
    OptionMenu(root, theme_var, 'dark', 'light').pack(pady=(0, 12))

    Label(root, text='Primary profile').pack()
    OptionMenu(root, profile_var, *PROFILES).pack(pady=(0, 12))

    Label(root, text='Default wallpaper').pack()
    OptionMenu(root, wallpaper_var, *wallpaper_options).pack(pady=(0, 12))

    enable_virt = IntVar(value=1)
    Checkbutton(root, text='Keep virtualization tools enabled', variable=enable_virt).pack(anchor='w', padx=44)

    enable_nekobox = IntVar(value=1)
    Checkbutton(root, text='Keep NekoBox in the default app set', variable=enable_nekobox).pack(anchor='w', padx=44)

    launch_control_center = IntVar(value=1)
    Checkbutton(root, text='Open control center after setup', variable=launch_control_center).pack(anchor='w', padx=44)

    Label(
        root,
        text='The selected wallpaper is written as the system default and then applied to the current Plasma session.',
        wraplength=580,
        justify='left',
    ).pack(pady=(18, 16))

    def finish() -> None:
        selected_wallpaper = wallpaper_var.get()
        data = {
            'theme': theme_var.get(),
            'profile': profile_var.get(),
            'wallpaper': selected_wallpaper,
            'virtualization': bool(enable_virt.get()),
            'nekobox_visible': bool(enable_nekobox.get()),
            'launch_control_center': bool(launch_control_center.get()),
        }
        save_state(data)
        run(['pkexec', 'sanchosctl', 'wallpaper', 'set-default', selected_wallpaper])
        run(['sanchosctl', 'wallpaper', 'apply', selected_wallpaper])
        if theme_var.get() == 'dark':
            run(['lookandfeeltool', '-a', 'org.kde.breezedark.desktop'])
        else:
            run(['lookandfeeltool', '-a', 'org.kde.breeze.desktop'])
        if launch_control_center.get():
            run(['sanchos-control-center'])
        root.destroy()

    Button(root, text='Finish', command=finish, width=18).pack()
    root.mainloop()


if __name__ == '__main__':
    main()
