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
WALLPAPER_INDEX = Path('/usr/share/backgrounds/sanchos-os/index.json')


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


class ControlCenter:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title('Sanchos Control Center')
        self.root.geometry('1024x680')
        self.status = StringVar(value='Ready')
        self.vm_list = None
        self.module_list = None
        self.network_list = None
        self.wallpaper_list = None
        self.wallpaper_default = StringVar(value='Default: unset')
        self._build()
        self.refresh_all()

    def _build(self) -> None:
        header = Frame(self.root, padx=20, pady=18)
        header.pack(fill=BOTH)
        Label(header, text='Sanchos Control Center', font=('Sans', 22, 'bold')).pack(anchor='w')
        Label(header, text='Host, desktop and virtualization controls', font=('Sans', 11)).pack(anchor='w')

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=16, pady=(0, 12))

        self.tab_overview = Frame(notebook, padx=16, pady=16)
        self.tab_vms = Frame(notebook, padx=16, pady=16)
        self.tab_network = Frame(notebook, padx=16, pady=16)
        self.tab_services = Frame(notebook, padx=16, pady=16)
        self.tab_appearance = Frame(notebook, padx=16, pady=16)

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

        footer = Frame(self.root, padx=16, pady=10)
        footer.pack(fill=BOTH)
        Label(footer, textvariable=self.status).pack(side=LEFT)
        Button(footer, text='Refresh', command=self.refresh_all).pack(side=RIGHT)

    def _build_overview(self) -> None:
        left = Frame(self.tab_overview)
        left.pack(side=LEFT, fill=BOTH, expand=True)
        right = Frame(self.tab_overview)
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        Label(left, text='Host summary', font=('Sans', 14, 'bold')).pack(anchor='w', pady=(0, 8))
        self.host_summary = Label(left, justify='left', anchor='w', wraplength=400)
        self.host_summary.pack(anchor='w')

        Label(left, text='Doctor', font=('Sans', 14, 'bold')).pack(anchor='w', pady=(20, 8))
        self.doctor_summary = Label(left, justify='left', anchor='w', wraplength=400)
        self.doctor_summary.pack(anchor='w')

        Label(right, text='Quick actions', font=('Sans', 14, 'bold')).pack(anchor='w', pady=(0, 8))
        Button(right, text='Open virt-manager', width=26, command=lambda: self.launch(['virt-manager'])).pack(anchor='w', pady=4)
        Button(right, text='Open NekoBox', width=26, command=lambda: self.launch(['nekobox'])).pack(anchor='w', pady=4)
        Button(right, text='Open VM networks', width=26, command=lambda: self.show_text_window('VM networks', query(['sanchosctl', 'vm', 'networks']))).pack(anchor='w', pady=4)
        Button(right, text='Run doctor in terminal', width=26, command=lambda: self.launch(['x-terminal-emulator', '-e', 'sanchosctl', 'system', 'doctor'])).pack(anchor='w', pady=4)

    def _build_vms(self) -> None:
        toolbar = Frame(self.tab_vms)
        toolbar.pack(fill=BOTH, pady=(0, 10))
        Button(toolbar, text='Refresh', command=self.refresh_vms).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text='Start', command=lambda: self.vm_action('start')).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text='Stop', command=lambda: self.vm_action('stop')).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text='Console', command=lambda: self.vm_action('console', detached=True)).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text='Delete', command=self.vm_delete_action).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text='Snapshots', command=self.show_snapshot_window).pack(side=LEFT, padx=(0, 8))

        create_row = Frame(self.tab_vms)
        create_row.pack(fill=BOTH, pady=(0, 10))
        Label(create_row, text='Name').pack(side=LEFT)
        self.vm_name = Entry(create_row, width=18)
        self.vm_name.pack(side=LEFT, padx=(6, 10))
        Label(create_row, text='ISO').pack(side=LEFT)
        self.vm_iso = Entry(create_row, width=38)
        self.vm_iso.pack(side=LEFT, padx=(6, 10))
        Button(create_row, text='Create VM', command=self.create_vm).pack(side=LEFT)

        self.vm_list = ttk.Treeview(self.tab_vms, columns=('id', 'name', 'state'), show='headings', height=18)
        for col, width in [('id', 80), ('name', 260), ('state', 220)]:
            self.vm_list.heading(col, text=col.capitalize())
            self.vm_list.column(col, width=width)
        self.vm_list.pack(fill=BOTH, expand=True)

    def _build_network(self) -> None:
        toolbar = Frame(self.tab_network)
        toolbar.pack(fill=BOTH, pady=(0, 10))
        Button(toolbar, text='Refresh', command=self.refresh_network).pack(side=LEFT)
        Button(toolbar, text='Show interfaces', command=lambda: self.show_text_window('Interfaces', query(['ip', '-brief', 'address']))).pack(side=LEFT, padx=(10, 0))

        self.network_list = ttk.Treeview(self.tab_network, columns=('item', 'value'), show='headings', height=16)
        self.network_list.heading('item', text='Item')
        self.network_list.heading('value', text='Value')
        self.network_list.column('item', width=220)
        self.network_list.column('value', width=720)
        self.network_list.pack(fill=BOTH, expand=True)

    def _build_services(self) -> None:
        toolbar = Frame(self.tab_services)
        toolbar.pack(fill=BOTH, pady=(0, 10))
        Button(toolbar, text='Refresh', command=self.refresh_services).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text='Enable selected module', command=self.enable_selected_module).pack(side=LEFT)

        self.module_list = ttk.Treeview(self.tab_services, columns=('module', 'status'), show='headings', height=16)
        self.module_list.heading('module', text='Module')
        self.module_list.heading('status', text='Status')
        self.module_list.column('module', width=280)
        self.module_list.column('status', width=180)
        self.module_list.pack(fill=BOTH, expand=True)

    def _build_appearance(self) -> None:
        Label(self.tab_appearance, text='Wallpapers', font=('Sans', 14, 'bold')).pack(anchor='w', pady=(0, 8))
        Label(self.tab_appearance, text='Wallpapers are installed into /usr/share/backgrounds/sanchos-os and indexed for first boot and the control center.', wraplength=760, justify='left').pack(anchor='w', pady=(0, 4))
        Label(self.tab_appearance, textvariable=self.wallpaper_default, font=('Sans', 10, 'bold')).pack(anchor='w', pady=(0, 8))
        self.wallpaper_list = ttk.Treeview(self.tab_appearance, columns=('path',), show='headings', height=14)
        self.wallpaper_list.heading('path', text='Installed wallpaper')
        self.wallpaper_list.column('path', width=760)
        self.wallpaper_list.pack(fill=BOTH, expand=False)
        toolbar = Frame(self.tab_appearance)
        toolbar.pack(fill=BOTH, pady=8)
        Button(toolbar, text='Rescan wallpapers', command=self.rescan_wallpapers).pack(side=LEFT)
        Button(toolbar, text='Set selected as default', command=self.set_selected_wallpaper_default).pack(side=LEFT, padx=(8, 0))
        Button(toolbar, text='Open wallpaper directory', command=lambda: self.launch(['xdg-open', '/usr/share/backgrounds/sanchos-os'])).pack(side=LEFT, padx=(8, 0))
        Button(self.tab_appearance, text='Open first-boot state', command=lambda: self.show_text_window('First-boot state', read_text(Path.home() / '.config/sanchos-os/firstboot.json', fallback='No first-boot state found.'))).pack(anchor='w', pady=4)

    def launch(self, command: list[str]) -> None:
        ok = run_detached(command)
        self.status.set('Launched' if ok else 'Launch failed')

    def refresh_all(self) -> None:
        self.refresh_overview()
        self.refresh_vms()
        self.refresh_network()
        self.refresh_services()
        self.refresh_appearance()
        self.status.set('Refreshed')

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
            if len(parts) < 3:
                continue
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
        base = Path('/usr/share/backgrounds/sanchos-os')
        if not base.exists():
            return
        for path in sorted(base.rglob('*')):
            if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.svg'} and path.name != 'index.json':
                self.wallpaper_list.insert('', END, values=(str(path.relative_to(base)),))

    def selected_wallpaper(self) -> str | None:
        selected = self.wallpaper_list.selection()
        if not selected:
            self.status.set('No wallpaper selected')
            return None
        values = self.wallpaper_list.item(selected[0], 'values')
        return values[0] if values else None

    def rescan_wallpapers(self) -> None:
        if os.geteuid() != 0:
            self.status.set('Open control center as root to rebuild the index')
            return
        output = query(['sanchosctl', 'wallpaper', 'rescan'], fallback='Rescan failed')
        self.status.set(output.splitlines()[0] if output else 'Rescanned wallpapers')
        self.refresh_appearance()

    def set_selected_wallpaper_default(self) -> None:
        path = self.selected_wallpaper()
        if not path:
            return
        if os.geteuid() != 0:
            self.status.set('Open control center as root to change the default wallpaper')
            return
        output = query(['sanchosctl', 'wallpaper', 'set-default', path], fallback='Set default failed')
        self.status.set(output.splitlines()[0] if output else f'Set default wallpaper: {path}')
        self.refresh_appearance()

    def selected_vm_name(self) -> str | None:
        selected = self.vm_list.selection()
        if not selected:
            self.status.set('No VM selected')
            return None
        values = self.vm_list.item(selected[0], 'values')
        return values[1] if len(values) >= 2 else None

    def selected_module_name(self) -> str | None:
        selected = self.module_list.selection()
        if not selected:
            self.status.set('No module selected')
            return None
        values = self.module_list.item(selected[0], 'values')
        return values[0] if values else None

    def vm_action(self, action: str, detached: bool = False) -> None:
        name = self.selected_vm_name()
        if not name:
            return
        command = ['sanchosctl', 'vm', action, name]
        if detached:
            if not run_detached(['x-terminal-emulator', '-e', *command]):
                self.status.set('Console launch failed')
            return
        output = query(command, fallback='Action failed')
        self.status.set(output.splitlines()[0] if output else f'Ran {action} for {name}')
        self.refresh_vms()

    def vm_delete_action(self) -> None:
        name = self.selected_vm_name()
        if not name:
            return
        output = query(['sanchosctl', 'vm', 'delete', name, '--yes'], fallback='Delete failed')
        self.status.set(output.splitlines()[0] if output else f'Deleted {name}')
        self.refresh_vms()

    def create_vm(self) -> None:
        name = self.vm_name.get().strip()
        iso = self.vm_iso.get().strip()
        if not name or not iso:
            self.status.set('Fill VM name and ISO path first')
            return
        output = query(['sanchosctl', 'vm', 'create', name, '--iso', iso], fallback='Create failed')
        self.status.set(output.splitlines()[0] if output else f'Create launched for {name}')
        self.refresh_vms()

    def enable_selected_module(self) -> None:
        name = self.selected_module_name()
        if not name:
            return
        if os.geteuid() != 0:
            self.status.set('Open control center as root to enable modules')
            return
        output = query(['sanchosctl', 'module', 'enable', name], fallback='Enable failed')
        self.status.set(output.splitlines()[0] if output else f'Enabled {name}')
        self.refresh_services()

    def show_snapshot_window(self) -> None:
        name = self.selected_vm_name()
        if not name:
            return
        self.show_text_window(f'Snapshots: {name}', query(['sanchosctl', 'vm', 'snapshot', 'list', name], fallback='No snapshots found.'))

    def show_text_window(self, title: str, text: str) -> None:
        window = Toplevel(self.root)
        window.title(title)
        window.geometry('760x480')
        box = ttk.Treeview(window, columns=('text',), show='headings')
        box.heading('text', text=title)
        box.column('text', width=720)
        box.pack(fill=BOTH, expand=True)
        for line in text.splitlines() or [text]:
            box.insert('', END, values=(line,))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        print('sanchos-control-center needs a graphical session. Run it inside KDE/Wayland/X11, not from a plain TTY or SSH shell.')
        raise SystemExit(1)
    app = ControlCenter()
    app.run()


if __name__ == '__main__':
    sys.exit(main())
