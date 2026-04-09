#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, threading
from pathlib import Path
import customtkinter as ctk

STATE_DIR = Path('/etc/sanchos-os/state')
WALLPAPER_DIR = Path('/usr/share/backgrounds/sanchos-os')
WALLPAPER_INDEX = WALLPAPER_DIR / 'index.json'
PALETTE = {'bg':'#120e18','panel':'#17111f','panel2':'#20172a','panel3':'#2a1f37','fg':'#f5f1ff','muted':'#cabde5','accent':'#a678ff','accent2':'#7a56d6'}

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

def query(command, fallback='Unavailable', timeout=10):
    try:
        proc = subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout)
        text = (proc.stdout or '').strip() or (proc.stderr or '').strip()
        return text or fallback
    except Exception as exc:
        return f'{fallback}\n{exc}'

def run(command, privileged=False, timeout=20):
    actual = ['pkexec', *command] if privileged and os.geteuid() != 0 and shutil.which('pkexec') else command
    proc = subprocess.run(actual, capture_output=True, text=True, check=False, timeout=timeout)
    return proc.returncode == 0, (proc.stdout.strip() or proc.stderr.strip() or 'Done')

def run_detached(command):
    try:
        subprocess.Popen(command)
        return True
    except Exception:
        return False

def load_index():
    try:
        return json.loads(WALLPAPER_INDEX.read_text())
    except Exception:
        return {'default': 'unset', 'collections': {}}

def flat_wallpapers():
    data = load_index()
    out = []
    for items in data.get('collections', {}).values():
        out.extend(items)
    return out

class SidebarButton(ctk.CTkButton):
    def __init__(self, master, text, command):
        super().__init__(master, text=text, command=command, corner_radius=18, height=46, fg_color=PALETTE['panel2'], hover_color=PALETTE['panel3'], text_color=PALETTE['fg'], anchor='w')

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Sanchos Control Center')
        self.geometry('1360x900')
        self.minsize(1180, 760)
        self.configure(fg_color=PALETTE['bg'])
        self.default_wallpaper = ctk.StringVar(value='unset')
        self.wallpaper_var = ctk.StringVar(value='')
        self._build()
        self.show_page('overview')
        self.refresh_all()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color='#0f0b15')
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        self.sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(self.sidebar, text='sanchos-os', font=ctk.CTkFont(family='Inter', size=28, weight='bold')).pack(anchor='w', padx=22, pady=(24, 4))
        ctk.CTkLabel(self.sidebar, text='warm control surface', text_color=PALETTE['muted']).pack(anchor='w', padx=22, pady=(0, 18))
        self.buttons = {}
        for key, label in [('overview', 'Overview'), ('appearance', 'Appearance'), ('launcher', 'Launcher'), ('virtualization', 'Virtualization'), ('services', 'Services')]:
            btn = SidebarButton(self.sidebar, label, lambda k=key: self.show_page(k))
            btn.pack(fill='x', padx=16, pady=7)
            self.buttons[key] = btn

        self.status = ctk.CTkLabel(self.sidebar, text='Ready', wraplength=210, justify='left', text_color=PALETTE['muted'])
        self.status.pack(side='bottom', anchor='w', padx=22, pady=22)

        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=PALETTE['bg'])
        self.content.grid(row=0, column=1, sticky='nsew', padx=18, pady=18)
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(self.content, corner_radius=28, fg_color=PALETTE['panel'])
        hero.grid(row=0, column=0, sticky='ew', pady=(0, 18))
        hero.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hero, text='Sanchos Control Center', font=ctk.CTkFont(family='Inter', size=36, weight='bold')).grid(row=0, column=0, sticky='w', padx=30, pady=(24, 4))
        ctk.CTkLabel(hero, text='Rounded Plasma styling, warm purple visuals, launcher search and host controls.', text_color=PALETTE['muted']).grid(row=1, column=0, sticky='w', padx=30, pady=(0, 22))

        self.page_container = ctk.CTkFrame(self.content, fg_color='transparent')
        self.page_container.grid(row=1, column=0, sticky='nsew')
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)
        self.pages = {
            'overview': self.build_overview(),
            'appearance': self.build_appearance(),
            'launcher': self.build_launcher(),
            'virtualization': self.build_virtualization(),
            'services': self.build_services(),
        }

    def _page(self):
        f = ctk.CTkFrame(self.page_container, fg_color='transparent')
        f.grid(row=0, column=0, sticky='nsew')
        f.grid_columnconfigure(0, weight=1)
        return f

    def show_page(self, key):
        for name, frame in self.pages.items():
            frame.grid_remove()
            self.buttons[name].configure(fg_color=PALETTE['panel2'])
        self.pages[key].grid()
        self.buttons[key].configure(fg_color=PALETTE['accent2'])

    def card(self, master, title, subtitle=None):
        c = ctk.CTkFrame(master, corner_radius=26, fg_color=PALETTE['panel'])
        ctk.CTkLabel(c, text=title, font=ctk.CTkFont(family='Inter', size=22, weight='bold')).pack(anchor='w', padx=22, pady=(18, 4))
        if subtitle:
            ctk.CTkLabel(c, text=subtitle, text_color=PALETTE['muted'], wraplength=900, justify='left').pack(anchor='w', padx=22, pady=(0, 14))
        return c

    def build_overview(self):
        f = self._page()
        f.grid_columnconfigure((0, 1), weight=1)
        host = self.card(f, 'Host', 'Core host info and doctor status.')
        host.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=(0, 14))
        self.host_box = ctk.CTkTextbox(host, height=280, corner_radius=18, fg_color=PALETTE['panel2'])
        self.host_box.pack(fill='both', expand=True, padx=18, pady=(0, 18))

        actions = self.card(f, 'Quick actions', 'Jump into the things you actually touch during iteration.')
        actions.grid(row=0, column=1, sticky='nsew', padx=(10, 0), pady=(0, 14))
        wrap = ctk.CTkFrame(actions, fg_color='transparent')
        wrap.pack(fill='both', expand=True, padx=18, pady=(0, 18))
        for label, cmd in [
            ('Run visual preset now', self.apply_visual),
            ('Rebuild top panel', self.rebuild_panel),
            ('Open wallpaper settings', lambda: self.launch(['kcmshell5', 'wallpaper'])),
            ('Open NekoBox', lambda: self.launch(['nekobox'])),
            ('Open virt-manager', lambda: self.launch(['virt-manager'])),
        ]:
            ctk.CTkButton(wrap, text=label, command=cmd, corner_radius=16, height=42, fg_color=PALETTE['accent'], hover_color=PALETTE['accent2']).pack(fill='x', pady=6)

        log_card = self.card(f, 'Action log', 'Short outputs from desktop helpers and privileged commands.')
        log_card.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.log_box = ctk.CTkTextbox(log_card, corner_radius=18, fg_color=PALETTE['panel2'], height=180)
        self.log_box.pack(fill='both', expand=True, padx=18, pady=(0, 18))
        return f

    def build_appearance(self):
        f = self._page()
        card = self.card(f, 'Appearance', 'Default wallpaper, rounded shell and the polished desktop preset.')
        card.pack(fill='both', expand=True)
        top = ctk.CTkFrame(card, fg_color='transparent')
        top.pack(fill='x', padx=18, pady=(0, 12))
        ctk.CTkLabel(top, text='Default wallpaper', text_color=PALETTE['muted']).pack(anchor='w')
        ctk.CTkLabel(top, textvariable=self.default_wallpaper, font=ctk.CTkFont(family='Inter', size=16, weight='bold')).pack(anchor='w', pady=(2, 8))
        self.wallpaper_menu = ctk.CTkOptionMenu(top, variable=self.wallpaper_var, values=['loading...'], corner_radius=14, width=480, fg_color=PALETTE['panel3'], button_color=PALETTE['accent2'], button_hover_color=PALETTE['accent'])
        self.wallpaper_menu.pack(anchor='w')

        buttons = ctk.CTkFrame(card, fg_color='transparent')
        buttons.pack(fill='x', padx=18, pady=(0, 14))
        for label, cmd in [
            ('Apply selected now', self.apply_selected_wallpaper),
            ('Set selected as default', self.set_selected_default),
            ('Rescan wallpapers', self.rescan_wallpapers),
            ('Apply polished preset', self.apply_visual),
            ('Rebuild top panel', self.rebuild_panel),
        ]:
            ctk.CTkButton(buttons, text=label, command=cmd, corner_radius=16, height=40, fg_color=PALETTE['accent'], hover_color=PALETTE['accent2']).pack(side='left', padx=(0, 10))

        self.appearance_notes = ctk.CTkTextbox(card, height=260, corner_radius=18, fg_color=PALETTE['panel2'])
        self.appearance_notes.pack(fill='both', expand=True, padx=18, pady=(0, 18))
        return f

    def build_launcher(self):
        f = self._page()
        card = self.card(f, 'Launcher', 'Meta+Space opens a centered translucent search panel built with rofi.')
        card.pack(fill='both', expand=True)
        body = ctk.CTkFrame(card, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=18, pady=(0, 18))
        self.launcher_box = ctk.CTkTextbox(body, height=220, corner_radius=18, fg_color=PALETTE['panel2'])
        self.launcher_box.pack(fill='x')
        actions = ctk.CTkFrame(body, fg_color='transparent')
        actions.pack(fill='x', pady=18)
        ctk.CTkButton(actions, text='Launch search now', command=lambda: self.launch(['sanchos-launcher']), corner_radius=16, height=42, fg_color=PALETTE['accent'], hover_color=PALETTE['accent2']).pack(side='left')
        ctk.CTkButton(actions, text='Restart hotkeys', command=self.restart_hotkeys, corner_radius=16, height=42, fg_color=PALETTE['panel3'], hover_color=PALETTE['accent2']).pack(side='left', padx=10)
        ctk.CTkButton(actions, text='Open rofi config', command=lambda: self.launch(['xdg-open', str(Path.home() / '.config/rofi')]), corner_radius=16, height=42, fg_color=PALETTE['panel3'], hover_color=PALETTE['accent2']).pack(side='left')
        return f

    def build_virtualization(self):
        f = self._page()
        card = self.card(f, 'Virtualization', 'Fast view over libvirt and VM state while the desktop gets prettier.')
        card.pack(fill='both', expand=True)
        self.vm_box = ctk.CTkTextbox(card, corner_radius=18, fg_color=PALETTE['panel2'])
        self.vm_box.pack(fill='both', expand=True, padx=18, pady=(0, 18))
        return f

    def build_services(self):
        f = self._page()
        card = self.card(f, 'Services', 'Modules, NekoBox visibility and small desktop integration checks.')
        card.pack(fill='both', expand=True)
        self.services_box = ctk.CTkTextbox(card, corner_radius=18, fg_color=PALETTE['panel2'])
        self.services_box.pack(fill='both', expand=True, padx=18, pady=(0, 18))
        return f

    def set_status(self, text):
        self.status.configure(text=(text[:180] + '…') if len(text) > 180 else text)

    def log(self, text):
        self.log_box.insert('end', text.strip() + '\n\n')
        self.log_box.see('end')

    def run_async(self, label, func):
        self.set_status(label)
        def worker():
            try:
                msg = func()
            except Exception as exc:
                msg = f'{label} failed: {exc}'
            self.after(0, lambda: (self.log(msg), self.set_status('Ready'), self.refresh_all()))
        threading.Thread(target=worker, daemon=True).start()

    def launch(self, command):
        self.set_status('Launched.' if run_detached(command) else 'Launch failed.')

    def refresh_all(self):
        self.refresh_overview()
        self.refresh_appearance()
        self.refresh_launcher()
        self.refresh_virtualization()
        self.refresh_services()

    def refresh_overview(self):
        self.host_box.delete('1.0', 'end')
        self.host_box.insert('1.0', query(['sanchosctl', 'system', 'info']) + '\n\n' + query(['sanchosctl', 'system', 'doctor']))

    def refresh_appearance(self):
        data = load_index()
        self.default_wallpaper.set(data.get('default', 'unset'))
        wallpapers = flat_wallpapers() or ['unset']
        self.wallpaper_menu.configure(values=wallpapers)
        self.wallpaper_var.set(self.default_wallpaper.get() if self.default_wallpaper.get() in wallpapers else wallpapers[0])
        self.appearance_notes.delete('1.0', 'end')
        self.appearance_notes.insert('1.0', 'Visual direction:\n- Warm dark purple shell\n- Rounded cards and launcher search\n- Floating top panel\n- Papirus-Dark icons + Kvantum window style\n\nTip: use Meta+Space to open the launcher after login.')

    def refresh_launcher(self):
        self.launcher_box.delete('1.0', 'end')
        self.launcher_box.insert('1.0', 'Launcher binding: Meta+Space\nBackend: rofi drun/run/window\nTheme file: ~/.config/rofi/sanchos-launcher.rasi\nHotkey daemon: xbindkeys\n\nIf the shortcut does not work after login, press “Restart hotkeys”.')

    def refresh_virtualization(self):
        self.vm_box.delete('1.0', 'end')
        self.vm_box.insert('1.0', query(['sanchosctl', 'vm', 'list']) + '\n\n' + query(['sanchosctl', 'vm', 'networks']))

    def refresh_services(self):
        self.services_box.delete('1.0', 'end')
        self.services_box.insert('1.0', query(['sanchosctl', 'module', 'list']) + '\n\n' + query(['which', 'nekobox']))

    def apply_visual(self):
        def work():
            helper = '/usr/local/lib/sanchos-os/configure-desktop-style.py'
            ok, text = run(['python3', helper, '--user', os.environ.get('USER', 'root'), '--apply-now', '--disable-tiling'])
            return text
        self.run_async('Applying polished preset…', work)

    def rebuild_panel(self):
        def work():
            ok, text = run(['python3', '/usr/local/lib/sanchos-os/apply-plasma-layout.py'])
            return text
        self.run_async('Rebuilding top panel…', work)

    def rescan_wallpapers(self):
        def work():
            ok, text = run(['sanchosctl', 'wallpaper', 'rescan'], privileged=True)
            return text
        self.run_async('Rescanning wallpapers…', work)

    def apply_selected_wallpaper(self):
        value = self.wallpaper_var.get()
        def work():
            ok, text = run(['sanchosctl', 'wallpaper', 'apply', value])
            return text
        self.run_async(f'Applying {value}…', work)

    def set_selected_default(self):
        value = self.wallpaper_var.get()
        def work():
            ok, text = run(['sanchosctl', 'wallpaper', 'set-default', value], privileged=True)
            return text
        self.run_async(f'Setting default to {value}…', work)

    def restart_hotkeys(self):
        def work():
            subprocess.run(['pkill', '-x', 'xbindkeys'], check=False)
            ok = run_detached(['/bin/sh', '-lc', 'xbindkeys -f "$HOME/.config/xbindkeysrc"'])
            return 'Hotkeys restarted.' if ok else 'Failed to restart hotkeys.'
        self.run_async('Restarting launcher hotkeys…', work)

def main():
    if not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        print('Sanchos Control Center must be started from a graphical desktop session.')
        raise SystemExit(1)
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()
