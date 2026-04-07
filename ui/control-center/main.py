#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, Button, Entry, Frame, Label, StringVar, Tk, Toplevel
from tkinter import ttk

STATE_DIR = Path('/etc/sanchos-os/state')
WALLPAPER_DIR = Path('/usr/share/backgrounds/sanchos-os')
PALETTE = {
    'bg': '#120f18',
    'panel': '#1d1727',
    'panel2': '#2a2136',
    'fg': '#f5f2ff',
    'muted': '#cabee1',
    'accent': '#9f6fff',
    'accent_soft': '#744ed9',
    'border': '#433056',
}


def query(command: list[str], fallback: str = 'Unavailable') -> str:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        text = proc.stdout.strip() or proc.stderr.strip()
        return text or fallback
    except Exception:
        return fallback


def run_detached(command: list[str]) -> bool:
    try:
        subprocess.Popen(command)
        return True
    except Exception:
        return False


def read_text(path: Path, fallback: str = 'Unavailable') -> str:
    try:
        return path.read_text().strip() or fallback
    except Exception:
        return fallback



def read_visual_summary() -> str:
    path = Path.home() / '.config' / 'sanchos-os' / 'visual-preset.json'
    try:
        import json
        data = json.loads(path.read_text())
        tiling = 'on' if data.get('tiling_enabled') else 'off'
        return f"Preset: {data.get('color_scheme', 'SanchosPurple')} / panel {data.get('panel_layout', 'top-floating')} / tiling {tiling} / wallpaper {data.get('wallpaper', 'unset')}"
    except Exception:
        return 'Preset: warm-purple / top-floating / tiling pending next login'


class ControlCenter:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title('Sanchos Control Center')
        self.root.geometry('1240x820')
        self.root.configure(bg=PALETTE['bg'])
        self.status = StringVar(value='Ready')
        self.wallpaper_default = StringVar(value='Default: unset')
        self.visual_state = StringVar(value='Preset: loading')
        self._configure_styles()
        self._build()
        self.refresh_all()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TNotebook', background=PALETTE['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=PALETTE['panel2'], foreground=PALETTE['fg'], padding=(12, 8))
        style.map('TNotebook.Tab', background=[('selected', PALETTE['accent_soft'])])
        style.configure('Treeview', background=PALETTE['panel'], fieldbackground=PALETTE['panel'], foreground=PALETTE['fg'], bordercolor=PALETTE['border'])
        style.configure('Treeview.Heading', background=PALETTE['panel2'], foreground=PALETTE['fg'])

    def _button(self, parent: Frame, text: str, command, width: int = 22) -> Button:
        return Button(parent, text=text, command=command, width=width, bg=PALETTE['accent'], fg=PALETTE['fg'], activebackground=PALETTE['accent_soft'], activeforeground=PALETTE['fg'], relief='flat', bd=0, padx=10, pady=8)

    def _build(self) -> None:
        header = Frame(self.root, bg=PALETTE['bg'], padx=24, pady=18)
        header.pack(fill=BOTH)
        Label(header, text='Sanchos Control Center', font=('Sans', 28, 'bold'), bg=PALETTE['bg'], fg=PALETTE['fg']).pack(anchor='w')
        Label(header, text='Warm desktop styling, host controls and virtualization from one place', font=('Sans', 11), bg=PALETTE['bg'], fg=PALETTE['muted']).pack(anchor='w')

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=16, pady=(0, 12))
        self.tab_overview = Frame(notebook, bg=PALETTE['panel'], padx=18, pady=18)
        self.tab_vms = Frame(notebook, bg=PALETTE['panel'], padx=18, pady=18)
        self.tab_network = Frame(notebook, bg=PALETTE['panel'], padx=18, pady=18)
        self.tab_services = Frame(notebook, bg=PALETTE['panel'], padx=18, pady=18)
        self.tab_appearance = Frame(notebook, bg=PALETTE['panel'], padx=18, pady=18)
        notebook.add(self.tab_overview, text='Overview')
        notebook.add(self.tab_vms, text='VMs')
        notebook.add(self.tab_network, text='Network')
        notebook.add(self.tab_services, text='Services')
        notebook.add(self.tab_appearance, text='Appearance')

        self._build_overview()
        self._build_vms()
        self._build_network()
        self._build_services()
        self._build_appearance()

        footer = Frame(self.root, bg=PALETTE['bg'], padx=16, pady=12)
        footer.pack(fill=BOTH)
        Label(footer, textvariable=self.status, bg=PALETTE['bg'], fg=PALETTE['muted']).pack(side=LEFT)
        self._button(footer, 'Refresh everything', self.refresh_all, width=20).pack(side=RIGHT)

    def _build_overview(self) -> None:
        left = Frame(self.tab_overview, bg=PALETTE['panel'])
        left.pack(side=LEFT, fill=BOTH, expand=True)
        right = Frame(self.tab_overview, bg=PALETTE['panel'])
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(24, 0))
        Label(left, text='Host summary', font=('Sans', 15, 'bold'), bg=PALETTE['panel'], fg=PALETTE['fg']).pack(anchor='w', pady=(0, 8))
        self.host_summary = Label(left, justify='left', anchor='w', wraplength=480, bg=PALETTE['panel'], fg=PALETTE['fg'])
        self.host_summary.pack(anchor='w')
        Label(left, text='Doctor', font=('Sans', 15, 'bold'), bg=PALETTE['panel'], fg=PALETTE['fg']).pack(anchor='w', pady=(20, 8))
        self.doctor_summary = Label(left, justify='left', anchor='w', wraplength=480, bg=PALETTE['panel'], fg=PALETTE['fg'])
        self.doctor_summary.pack(anchor='w')
        Label(right, text='Quick actions', font=('Sans', 15, 'bold'), bg=PALETTE['panel'], fg=PALETTE['fg']).pack(anchor='w', pady=(0, 8))
        for label, cmd in [
            ('Open virt-manager', lambda: self.launch(['virt-manager'])),
            ('Open NekoBox', lambda: self.launch(['nekobox'])),
            ('Open Plasma wallpaper settings', lambda: self.launch(['kcmshell5', 'wallpaper'])),
            ('Run visual preset now', self.apply_visual_preset),
            ('Rebuild top panel', self.apply_panel_layout),
        ]:
            self._button(right, label, cmd, width=28).pack(anchor='w', pady=4)

    def _build_vms(self) -> None:
        toolbar = Frame(self.tab_vms, bg=PALETTE['panel'])
        toolbar.pack(fill=BOTH, pady=(0, 10))
        for label, cmd in [('Refresh', self.refresh_vms), ('Start', lambda: self.vm_action('start')), ('Stop', lambda: self.vm_action('stop')), ('Console', lambda: self.vm_action('console', detached=True)), ('Delete', self.vm_delete_action), ('Snapshots', self.show_snapshot_window)]:
            self._button(toolbar, label, cmd, width=16).pack(side=LEFT, padx=(0, 8))
        create_row = Frame(self.tab_vms, bg=PALETTE['panel'])
        create_row.pack(fill=BOTH, pady=(0, 10))
        Label(create_row, text='Name', bg=PALETTE['panel'], fg=PALETTE['fg']).pack(side=LEFT)
        self.vm_name = Entry(create_row, width=18, bg=PALETTE['panel2'], fg=PALETTE['fg'], insertbackground=PALETTE['fg'])
        self.vm_name.pack(side=LEFT, padx=(6, 10))
        Label(create_row, text='ISO', bg=PALETTE['panel'], fg=PALETTE['fg']).pack(side=LEFT)
        self.vm_iso = Entry(create_row, width=42, bg=PALETTE['panel2'], fg=PALETTE['fg'], insertbackground=PALETTE['fg'])
        self.vm_iso.pack(side=LEFT, padx=(6, 10))
        self._button(create_row, 'Create VM', self.create_vm, width=14).pack(side=LEFT)
        self.vm_list = ttk.Treeview(self.tab_vms, columns=('id', 'name', 'state'), show='headings', height=18)
        for col, width in [('id', 90), ('name', 280), ('state', 220)]:
            self.vm_list.heading(col, text=col.capitalize())
            self.vm_list.column(col, width=width)
        self.vm_list.pack(fill=BOTH, expand=True)

    def _build_network(self) -> None:
        toolbar = Frame(self.tab_network, bg=PALETTE['panel'])
        toolbar.pack(fill=BOTH, pady=(0, 10))
        self._button(toolbar, 'Refresh', self.refresh_network, width=16).pack(side=LEFT)
        self._button(toolbar, 'Show interfaces', lambda: self.show_text_window('Interfaces', query(['ip', '-brief', 'address'])), width=18).pack(side=LEFT, padx=(10, 0))
        self.network_list = ttk.Treeview(self.tab_network, columns=('item', 'value'), show='headings', height=16)
        self.network_list.heading('item', text='Item')
        self.network_list.heading('value', text='Value')
        self.network_list.column('item', width=220)
        self.network_list.column('value', width=760)
        self.network_list.pack(fill=BOTH, expand=True)

    def _build_services(self) -> None:
        toolbar = Frame(self.tab_services, bg=PALETTE['panel'])
        toolbar.pack(fill=BOTH, pady=(0, 10))
        self._button(toolbar, 'Refresh', self.refresh_services, width=16).pack(side=LEFT, padx=(0, 8))
        self._button(toolbar, 'Enable selected module', self.enable_selected_module, width=22).pack(side=LEFT)
        self.module_list = ttk.Treeview(self.tab_services, columns=('module', 'status'), show='headings', height=16)
        self.module_list.heading('module', text='Module')
        self.module_list.heading('status', text='Status')
        self.module_list.column('module', width=280)
        self.module_list.column('status', width=180)
        self.module_list.pack(fill=BOTH, expand=True)

    def _build_appearance(self) -> None:
        Label(self.tab_appearance, text='Visual preset', font=('Sans', 15, 'bold'), bg=PALETTE['panel'], fg=PALETTE['fg']).pack(anchor='w', pady=(0, 4))
        Label(self.tab_appearance, textvariable=self.visual_state, bg=PALETTE['panel'], fg=PALETTE['muted']).pack(anchor='w', pady=(0, 12))
        Label(self.tab_appearance, text='Wallpapers', font=('Sans', 15, 'bold'), bg=PALETTE['panel'], fg=PALETTE['fg']).pack(anchor='w', pady=(0, 8))
        Label(self.tab_appearance, text='v9 defaults to a warm purple desktop with a floating top panel, monochrome-friendly icons and Plasma+i3 tiling.', wraplength=940, justify='left', bg=PALETTE['panel'], fg=PALETTE['muted']).pack(anchor='w', pady=(0, 6))
        Label(self.tab_appearance, textvariable=self.wallpaper_default, font=('Sans', 10, 'bold'), bg=PALETTE['panel'], fg=PALETTE['fg']).pack(anchor='w', pady=(0, 8))
        self.wallpaper_list = ttk.Treeview(self.tab_appearance, columns=('path',), show='headings', height=15)
        self.wallpaper_list.heading('path', text='Installed wallpaper')
        self.wallpaper_list.column('path', width=940)
        self.wallpaper_list.pack(fill=BOTH, expand=False)
        toolbar = Frame(self.tab_appearance, bg=PALETTE['panel'])
        toolbar.pack(fill=BOTH, pady=8)
        actions = [
            ('Rescan wallpapers', self.rescan_wallpapers, 18),
            ('Apply selected now', self.apply_selected_wallpaper, 18),
            ('Set selected as default', self.set_selected_wallpaper_default, 22),
            ('Apply visual preset', self.apply_visual_preset, 18),
            ('Rebuild top panel', self.apply_panel_layout, 18),
            ('Enable tiling session', self.enable_tiling_session, 20),
            ('Disable tiling session', self.disable_tiling_session, 20),
        ]
        for text, command, width in actions:
            self._button(toolbar, text, command, width=width).pack(side=LEFT, padx=(0, 8))
        toolbar2 = Frame(self.tab_appearance, bg=PALETTE['panel'])
        toolbar2.pack(fill=BOTH, pady=8)
        self._button(toolbar2, 'Open wallpaper directory', lambda: self.launch(['xdg-open', str(WALLPAPER_DIR)]), 22).pack(side=LEFT)
        self._button(toolbar2, 'Open first-boot state', lambda: self.show_text_window('First-boot state', read_text(Path.home() / '.config/sanchos-os/firstboot.json', fallback='No first-boot state found.')), 22).pack(side=LEFT, padx=(8, 0))

    def launch(self, command: list[str]) -> None:
        ok = run_detached(command)
        self.status.set('Launched' if ok else 'Launch failed')

    def privileged_query(self, command: list[str], fallback: str = 'Unavailable') -> str:
        if os.geteuid() == 0:
            return query(command, fallback=fallback)
        if shutil.which('pkexec'):
            return query(['pkexec', *command], fallback=fallback)
        return 'pkexec is not available for privileged actions.'

    def refresh_all(self) -> None:
        self.refresh_overview(); self.refresh_vms(); self.refresh_network(); self.refresh_services(); self.refresh_appearance(); self.status.set('Refreshed')

    def refresh_overview(self) -> None:
        summary = [
            f"Hostname: {query(['hostname'])}",
            f"Kernel: {query(['uname', '-srmo'])}",
            f"OS: {query(['bash', '-lc', '. /etc/os-release && echo ${PRETTY_NAME:-Debian}'])}",
            f"Installed profile: {read_text(STATE_DIR / 'installed-profile', 'unknown')}",
            f"Desktop user: {read_text(STATE_DIR / 'desktop-user', 'not recorded')}",
        ]
        self.host_summary.config(text='\n'.join(summary))
        self.doctor_summary.config(text=query(['sanchosctl', 'system', 'doctor'], fallback='Doctor unavailable'))

    def refresh_vms(self) -> None:
        for item in self.vm_list.get_children():
            self.vm_list.delete(item)
        table = query(['virsh', 'list', '--all'], fallback='')
        for line in table.splitlines()[2:]:
            if not line.strip():
                continue
            parts = line.split(None, 2)
            if len(parts) >= 3:
                self.vm_list.insert('', END, values=(parts[0], parts[1], parts[2]))

    def refresh_network(self) -> None:
        for item in self.network_list.get_children():
            self.network_list.delete(item)
        entries = [
            ('NetworkManager', query(['systemctl', 'is-active', 'NetworkManager'])),
            ('libvirtd', query(['systemctl', 'is-active', 'libvirtd'])),
            ('Default route', query(['bash', '-lc', 'ip route show default | head -n1'])),
            ('Primary address', query(['bash', '-lc', "hostname -I | awk '{print $1}'"])),
            ('NekoBox', shutil.which('nekobox') or 'not installed'),
        ]
        for key, value in entries:
            self.network_list.insert('', END, values=(key, value))

    def refresh_services(self) -> None:
        for item in self.module_list.get_children():
            self.module_list.delete(item)
        enabled = set(read_text(STATE_DIR / 'enabled-modules', '').splitlines())
        modules_dir = Path('/etc/sanchos-os/modules')
        if not modules_dir.exists():
            return
        for item in sorted(modules_dir.iterdir()):
            if item.is_dir():
                status = 'enabled' if item.name in enabled else 'available'
                self.module_list.insert('', END, values=(item.name, status))

    def refresh_appearance(self) -> None:
        for item in self.wallpaper_list.get_children():
            self.wallpaper_list.delete(item)
        output = query(['sanchosctl', 'wallpaper', 'list'], fallback='')
        default = 'unset'
        for line in output.splitlines():
            if line.startswith('Default: '):
                default = line.removeprefix('Default: ').strip()
                break
        self.wallpaper_default.set(f'Default: {default}')
        self.visual_state.set(read_visual_summary())
        if not WALLPAPER_DIR.exists():
            return
        for path in sorted(WALLPAPER_DIR.rglob('*')):
            if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.svg'} and path.name != 'index.json':
                self.wallpaper_list.insert('', END, values=(str(path.relative_to(WALLPAPER_DIR)),))

    def selected_wallpaper(self) -> str | None:
        selection = self.wallpaper_list.selection()
        if not selection:
            self.status.set('Select a wallpaper first')
            return None
        return self.wallpaper_list.item(selection[0], 'values')[0]

    def rescan_wallpapers(self) -> None:
        result = self.privileged_query(['sanchosctl', 'wallpaper', 'rescan'])
        self.status.set(result.splitlines()[0] if result else 'Wallpaper rescan finished')
        self.refresh_appearance()

    def apply_selected_wallpaper(self) -> None:
        value = self.selected_wallpaper()
        if not value:
            return
        result = query(['sanchosctl', 'wallpaper', 'apply', value])
        self.status.set(result.splitlines()[0] if result else 'Wallpaper applied')

    def set_selected_wallpaper_default(self) -> None:
        value = self.selected_wallpaper()
        if not value:
            return
        result = self.privileged_query(['sanchosctl', 'wallpaper', 'set-default', value, '--apply'])
        self.status.set(result.splitlines()[0] if result else 'Default wallpaper updated')
        self.refresh_appearance()

    def apply_visual_preset(self) -> None:
        result = self.privileged_query(['sanchosctl', 'visual', 'apply', '--apply-now'])
        self.status.set(result.splitlines()[0] if result else 'Visual preset applied')
        self.refresh_appearance()

    def apply_panel_layout(self) -> None:
        result = query(['sanchosctl', 'visual', 'panel'])
        self.status.set(result.splitlines()[0] if result else 'Panel layout applied')

    def enable_tiling_session(self) -> None:
        result = self.privileged_query(['sanchosctl', 'visual', 'tiling', 'enable'])
        self.status.set(result.splitlines()[0] if result else 'Tiling enabled for next login')

    def disable_tiling_session(self) -> None:
        result = self.privileged_query(['sanchosctl', 'visual', 'tiling', 'disable'])
        self.status.set(result.splitlines()[0] if result else 'Tiling disabled for next login')

    def enable_selected_module(self) -> None:
        selection = self.module_list.selection()
        if not selection:
            self.status.set('Select a module first')
            return
        name = self.module_list.item(selection[0], 'values')[0]
        result = self.privileged_query(['sanchosctl', 'module', 'enable', name])
        self.status.set(result.splitlines()[0] if result else f'Enabled module: {name}')
        self.refresh_services()

    def vm_action(self, action: str, detached: bool = False) -> None:
        selection = self.vm_list.selection()
        if not selection:
            self.status.set('Select a VM first')
            return
        name = self.vm_list.item(selection[0], 'values')[1]
        if detached and action == 'console':
            ok = run_detached(['sanchosctl', 'vm', 'console', name])
            self.status.set('Launched VM console' if ok else 'Failed to launch console')
            return
        result = query(['sanchosctl', 'vm', action, name])
        self.status.set(result.splitlines()[0] if result else f'VM action finished: {action}')
        self.refresh_vms()

    def vm_delete_action(self) -> None:
        selection = self.vm_list.selection()
        if not selection:
            self.status.set('Select a VM first')
            return
        name = self.vm_list.item(selection[0], 'values')[1]
        result = self.privileged_query(['sanchosctl', 'vm', 'delete', name, '--yes'])
        self.status.set(result.splitlines()[0] if result else f'Deleted VM: {name}')
        self.refresh_vms()

    def show_snapshot_window(self) -> None:
        selection = self.vm_list.selection()
        if not selection:
            self.status.set('Select a VM first')
            return
        name = self.vm_list.item(selection[0], 'values')[1]
        win = Toplevel(self.root)
        win.title(f'Snapshots: {name}')
        win.configure(bg=PALETTE['panel'])
        text = query(['sanchosctl', 'vm', 'snapshot', 'list', name], fallback='No snapshots')
        body = ttk.Treeview(win, columns=('text',), show='headings', height=12)
        body.heading('text', text='Snapshot list')
        body.column('text', width=600)
        body.pack(fill=BOTH, expand=True, padx=12, pady=12)
        for line in text.splitlines():
            if line.strip():
                body.insert('', END, values=(line,))

    def create_vm(self) -> None:
        name = self.vm_name.get().strip()
        iso = self.vm_iso.get().strip()
        if not name or not iso:
            self.status.set('Enter a VM name and ISO path first')
            return
        result = self.privileged_query(['sanchosctl', 'vm', 'create', name, iso, '20', '4096', '2'])
        self.status.set(result.splitlines()[0] if result else f'VM create requested: {name}')
        self.refresh_vms()

    def show_text_window(self, title: str, text: str) -> None:
        win = Toplevel(self.root)
        win.title(title)
        win.configure(bg=PALETTE['panel'])
        widget = ttk.Treeview(win, columns=('text',), show='headings', height=18)
        widget.heading('text', text=title)
        widget.column('text', width=820)
        widget.pack(fill=BOTH, expand=True, padx=12, pady=12)
        for line in text.splitlines() or ['']:
            widget.insert('', END, values=(line,))


def main() -> None:
    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        print('Sanchos Control Center requires a graphical session. Start it from Plasma, not from a TTY or SSH shell.')
        raise SystemExit(1)
    app = ControlCenter()
    app.root.mainloop()


if __name__ == '__main__':
    main()
