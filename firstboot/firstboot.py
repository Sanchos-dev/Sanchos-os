#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, threading
from pathlib import Path
import customtkinter as ctk

STATE_DIR = Path.home() / '.config' / 'sanchos-os'
STATE_FILE = STATE_DIR / 'firstboot.json'
WALLPAPER_INDEX = Path('/usr/share/backgrounds/sanchos-os/index.json')
PALETTE = {'bg':'#120e18','panel':'#17111f','panel2':'#20172a','fg':'#f5f1ff','muted':'#cbbfe5','accent':'#9d72ff','accent2':'#7a56d6'}

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

def run(cmd, timeout=20):
    try:
        subprocess.run(cmd, check=False, timeout=timeout)
    except Exception:
        pass

def load_wallpapers():
    try:
        data = json.loads(WALLPAPER_INDEX.read_text())
        items = []
        for values in data.get('collections', {}).values():
            items.extend(values)
        return items or [data.get('default', 'purple/purple0.png')]
    except Exception:
        return ['purple/purple0.png']

def preferred(items):
    for candidate in ['purple/purple0.png', 'purple/purple1.png', 'default/wp0.png']:
        if candidate in items:
            return candidate
    return items[0]

def save_state(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2) + '\n')

class FirstBoot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('sanchos-os first boot')
        self.geometry('1040x760')
        self.minsize(960, 720)
        self.configure(fg_color=PALETTE['bg'])
        self.wallpapers = load_wallpapers()
        self.wallpaper_var = ctk.StringVar(value=preferred(self.wallpapers))
        self.launch_cc = ctk.BooleanVar(value=True)
        self.apply_panel = ctk.BooleanVar(value=True)
        self.status = ctk.StringVar(value='Ready')
        self.build()

    def build(self):
        shell = ctk.CTkFrame(self, fg_color='transparent')
        shell.pack(fill='both', expand=True, padx=28, pady=28)
        hero = ctk.CTkFrame(shell, corner_radius=30, fg_color=PALETTE['panel'])
        hero.pack(fill='both', expand=True)
        ctk.CTkLabel(hero, text='Welcome to sanchos-os', font=ctk.CTkFont(family='Inter', size=36, weight='bold')).pack(anchor='w', padx=30, pady=(28, 6))
        ctk.CTkLabel(hero, text='Set the wallpaper, warm shell and launcher defaults before you settle in.', text_color=PALETTE['muted']).pack(anchor='w', padx=30, pady=(0, 18))

        grid = ctk.CTkFrame(hero, fg_color='transparent')
        grid.pack(fill='both', expand=True, padx=26, pady=(0, 22))
        grid.grid_columnconfigure((0, 1), weight=1)

        left = ctk.CTkFrame(grid, corner_radius=24, fg_color=PALETTE['panel2'])
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=(0, 12))
        ctk.CTkLabel(left, text='Wallpaper', font=ctk.CTkFont(family='Inter', size=22, weight='bold')).pack(anchor='w', padx=20, pady=(18, 10))
        ctk.CTkOptionMenu(left, variable=self.wallpaper_var, values=self.wallpapers, corner_radius=14, width=380, fg_color='#302443', button_color=PALETTE['accent2'], button_hover_color=PALETTE['accent']).pack(anchor='w', padx=20)
        ctk.CTkLabel(left, text='purple0 is the intended default for the warm visual preset.', text_color=PALETTE['muted']).pack(anchor='w', padx=20, pady=(12, 0))

        right = ctk.CTkFrame(grid, corner_radius=24, fg_color=PALETTE['panel2'])
        right.grid(row=0, column=1, sticky='nsew', padx=(10, 0), pady=(0, 12))
        ctk.CTkLabel(right, text='Session polish', font=ctk.CTkFont(family='Inter', size=22, weight='bold')).pack(anchor='w', padx=20, pady=(18, 10))
        ctk.CTkCheckBox(right, text='Apply rounded top panel now', variable=self.apply_panel, fg_color=PALETTE['accent'], hover_color=PALETTE['accent2']).pack(anchor='w', padx=20, pady=8)
        ctk.CTkCheckBox(right, text='Open control center after finishing', variable=self.launch_cc, fg_color=PALETTE['accent'], hover_color=PALETTE['accent2']).pack(anchor='w', padx=20, pady=8)
        ctk.CTkLabel(right, text='Meta+Space launches the centered search after the desktop finishes starting.', text_color=PALETTE['muted'], wraplength=360, justify='left').pack(anchor='w', padx=20, pady=(10, 0))

        notes = ctk.CTkFrame(hero, corner_radius=24, fg_color=PALETTE['panel2'])
        notes.pack(fill='x', padx=26, pady=(0, 18))
        ctk.CTkLabel(notes, text='What happens next', font=ctk.CTkFont(family='Inter', size=22, weight='bold')).pack(anchor='w', padx=20, pady=(18, 10))
        body = ctk.CTkTextbox(notes, height=150, corner_radius=18, fg_color='#1a1423')
        body.pack(fill='x', padx=20, pady=(0, 18))
        body.insert('1.0', '- The selected wallpaper becomes the system default.\n- The warm rounded Plasma preset is applied.\n- The floating top panel is rebuilt if requested.\n- CustomTkinter tools take over instead of plain Tk windows.')
        body.configure(state='disabled')

        footer = ctk.CTkFrame(hero, fg_color='transparent')
        footer.pack(fill='x', padx=30, pady=(0, 24))
        ctk.CTkButton(footer, text='Finish setup', command=self.finish, corner_radius=18, height=46, fg_color=PALETTE['accent'], hover_color=PALETTE['accent2']).pack(side='left')
        ctk.CTkLabel(footer, textvariable=self.status, text_color=PALETTE['muted']).pack(side='left', padx=16)

    def finish(self):
        selected = self.wallpaper_var.get()
        save_state({'wallpaper': selected, 'launch_control_center': bool(self.launch_cc.get()), 'panel_enabled': bool(self.apply_panel.get())})
        self.status.set('Applying desktop polish…')

        def worker():
            run(['pkexec', 'sanchosctl', 'wallpaper', 'set-default', selected])
            run(['sanchosctl', 'wallpaper', 'apply', selected])
            run(['python3', '/usr/local/lib/sanchos-os/configure-desktop-style.py', '--user', os.environ.get('SANCHOS_DESKTOP_USER') or os.environ.get('USER', 'root'), '--apply-now', '--disable-tiling'])
            if self.apply_panel.get():
                run(['python3', '/usr/local/lib/sanchos-os/apply-plasma-layout.py'])
            if self.launch_cc.get():
                subprocess.Popen(['sanchos-control-center'])
            self.after(0, self.destroy)

        threading.Thread(target=worker, daemon=True).start()

def main():
    if STATE_FILE.exists() or not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        return
    app = FirstBoot()
    app.mainloop()

if __name__ == '__main__':
    main()
