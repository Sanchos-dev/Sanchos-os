#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tkinter import BOTH, LEFT, W, Button, Checkbutton, Frame, IntVar, Label, OptionMenu, StringVar, Tk

STATE_DIR = Path.home() / '.config' / 'sanchos-os'
STATE_FILE = STATE_DIR / 'firstboot.json'
WALLPAPER_INDEX = Path('/usr/share/backgrounds/sanchos-os/index.json')
PROFILES = ['desktop', 'desktop-virt', 'dev', 'server-lite']
PALETTE = {
    'bg': '#120f18',
    'panel': '#1f1828',
    'panel2': '#2a2036',
    'fg': '#f6f2ff',
    'muted': '#cabfdf',
    'accent': '#9f6fff',
    'accent_soft': '#6d4ac6',
}


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
        return items or [data.get('default', 'purple/purple0.png')]
    except Exception:
        return ['purple/purple0.png']


def preferred_wallpaper(items: list[str]) -> str:
    for candidate in ['purple/purple0.png', 'default/wp0.png', 'default/sanchos-default.svg']:
        if candidate in items:
            return candidate
    return items[0]


def style_option_menu(widget: OptionMenu) -> None:
    widget.config(bg=PALETTE['panel2'], fg=PALETTE['fg'], activebackground=PALETTE['accent_soft'], activeforeground=PALETTE['fg'], highlightthickness=0)
    widget['menu'].config(bg=PALETTE['panel2'], fg=PALETTE['fg'], activebackground=PALETTE['accent_soft'])


def main() -> None:
    if STATE_FILE.exists():
        return

    root = Tk()
    root.title('sanchos-os first boot')
    root.geometry('840x620')
    root.resizable(False, False)
    root.configure(bg=PALETTE['bg'])

    shell = Frame(root, bg=PALETTE['bg'])
    shell.pack(fill=BOTH, expand=True, padx=24, pady=24)

    card = Frame(shell, bg=PALETTE['panel'], bd=0, highlightthickness=1, highlightbackground='#3b2b4e')
    card.pack(fill=BOTH, expand=True)

    Label(card, text='Welcome to sanchos-os', font=('Sans', 22, 'bold'), bg=PALETTE['panel'], fg=PALETTE['fg']).pack(anchor=W, padx=28, pady=(24, 6))
    Label(card, text='Warm purple desktop, tiling-first window management, native virtualization and your service stack.', font=('Sans', 11), bg=PALETTE['panel'], fg=PALETTE['muted'], wraplength=700, justify='left').pack(anchor=W, padx=28, pady=(0, 18))

    form = Frame(card, bg=PALETTE['panel'])
    form.pack(fill=BOTH, expand=True, padx=28, pady=12)

    theme_var = StringVar(value='sanchos-purple')
    profile_var = StringVar(value='desktop-virt')
    wallpaper_options = load_wallpapers()
    wallpaper_var = StringVar(value=preferred_wallpaper(wallpaper_options))

    for label_text, var, options in [
        ('Visual preset', theme_var, ['sanchos-purple', 'sanchos-purple-soft', 'dark']),
        ('Primary profile', profile_var, PROFILES),
        ('Default wallpaper', wallpaper_var, wallpaper_options),
    ]:
        Label(form, text=label_text, bg=PALETTE['panel'], fg=PALETTE['fg'], font=('Sans', 10, 'bold')).pack(anchor=W, pady=(8, 6))
        menu = OptionMenu(form, var, *options)
        style_option_menu(menu)
        menu.pack(anchor=W)

    enable_virt = IntVar(value=1)
    enable_nekobox = IntVar(value=1)
    enable_tiling = IntVar(value=1)
    apply_panel = IntVar(value=1)
    launch_control_center = IntVar(value=1)

    checks = [
        ('Keep virtualization tools enabled', enable_virt),
        ('Keep NekoBox in the default app set', enable_nekobox),
        ('Use Plasma + i3 tiling session on next login', enable_tiling),
        ('Apply the floating top panel and widget preset', apply_panel),
        ('Open control center after setup', launch_control_center),
    ]
    for text, variable in checks:
        Checkbutton(form, text=text, variable=variable, bg=PALETTE['panel'], fg=PALETTE['fg'], activebackground=PALETTE['panel'], activeforeground=PALETTE['fg'], selectcolor=PALETTE['panel2']).pack(anchor=W, pady=3)

    Label(card, text='The selected wallpaper becomes the default system wallpaper and is applied to the current Plasma session.', bg=PALETTE['panel'], fg=PALETTE['muted'], wraplength=700, justify='left').pack(anchor=W, padx=28, pady=(12, 18))

    actions = Frame(card, bg=PALETTE['panel'])
    actions.pack(fill=BOTH, padx=28, pady=(0, 24))

    def finish() -> None:
        selected_wallpaper = wallpaper_var.get()
        data = {
            'theme': theme_var.get(),
            'profile': profile_var.get(),
            'wallpaper': selected_wallpaper,
            'virtualization': bool(enable_virt.get()),
            'nekobox_visible': bool(enable_nekobox.get()),
            'tiling_enabled': bool(enable_tiling.get()),
            'panel_enabled': bool(apply_panel.get()),
            'launch_control_center': bool(launch_control_center.get()),
        }
        save_state(data)
        run(['pkexec', 'sanchosctl', 'wallpaper', 'set-default', selected_wallpaper])
        run(['sanchosctl', 'wallpaper', 'apply', selected_wallpaper])
        visual_command = ['pkexec', 'sanchosctl', 'visual', 'apply']
        if apply_panel.get():
            visual_command.append('--apply-now')
        run(visual_command)
        if enable_tiling.get():
            run(['pkexec', 'sanchosctl', 'visual', 'tiling', 'enable'])
        else:
            run(['pkexec', 'sanchosctl', 'visual', 'tiling', 'disable'])
        if launch_control_center.get():
            run(['sanchos-control-center'])
        root.destroy()

    Button(actions, text='Finish setup', command=finish, bg=PALETTE['accent'], fg=PALETTE['fg'], activebackground=PALETTE['accent_soft'], activeforeground=PALETTE['fg'], padx=18, pady=8).pack(side=LEFT)
    root.mainloop()


if __name__ == '__main__':
    main()
