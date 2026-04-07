#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, Button, Frame, Label, StringVar, Tk, Toplevel
from tkinter import ttk

STATE_DIR = Path("/etc/sanchos-os/state")


def query(command: list[str], fallback: str = "Unavailable") -> str:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        text = proc.stdout.strip() or proc.stderr.strip()
        return text or fallback
    except Exception:
        return fallback


def run_detached(command: list[str]) -> None:
    try:
        subprocess.Popen(command)
    except Exception:
        pass


def read_text(path: Path, fallback: str = "Unavailable") -> str:
    try:
        return path.read_text().strip() or fallback
    except Exception:
        return fallback


class ControlCenter:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Sanchos Control Center")
        self.root.geometry("980x640")
        self.status = StringVar(value="Ready")
        self.vm_list = None
        self.module_list = None
        self.network_text = None
        self._build()
        self.refresh_all()

    def _build(self) -> None:
        header = Frame(self.root, padx=20, pady=18)
        header.pack(fill=BOTH)
        Label(header, text="Sanchos Control Center", font=("Sans", 22, "bold")).pack(anchor="w")
        Label(header, text="Host, desktop and virtualization controls", font=("Sans", 11)).pack(anchor="w")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=16, pady=(0, 12))

        self.tab_overview = Frame(notebook, padx=16, pady=16)
        self.tab_vms = Frame(notebook, padx=16, pady=16)
        self.tab_network = Frame(notebook, padx=16, pady=16)
        self.tab_services = Frame(notebook, padx=16, pady=16)
        self.tab_appearance = Frame(notebook, padx=16, pady=16)

        notebook.add(self.tab_overview, text="Overview")
        notebook.add(self.tab_vms, text="VMs")
        notebook.add(self.tab_network, text="Network")
        notebook.add(self.tab_services, text="Services")
        notebook.add(self.tab_appearance, text="Appearance")

        self._build_overview()
        self._build_vms()
        self._build_network()
        self._build_services()
        self._build_appearance()

        footer = Frame(self.root, padx=16, pady=10)
        footer.pack(fill=BOTH)
        Label(footer, textvariable=self.status).pack(side=LEFT)
        Button(footer, text="Refresh", command=self.refresh_all).pack(side=RIGHT)

    def _build_overview(self) -> None:
        left = Frame(self.tab_overview)
        left.pack(side=LEFT, fill=BOTH, expand=True)
        right = Frame(self.tab_overview)
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        Label(left, text="Host summary", font=("Sans", 14, "bold")).pack(anchor="w", pady=(0, 8))
        self.host_summary = Label(left, justify="left", anchor="w", wraplength=380)
        self.host_summary.pack(anchor="w")

        Label(left, text="Doctor", font=("Sans", 14, "bold")).pack(anchor="w", pady=(20, 8))
        self.doctor_summary = Label(left, justify="left", anchor="w", wraplength=380)
        self.doctor_summary.pack(anchor="w")

        Label(right, text="Quick actions", font=("Sans", 14, "bold")).pack(anchor="w", pady=(0, 8))
        Button(right, text="Open virt-manager", width=24, command=lambda: run_detached(["virt-manager"])).pack(anchor="w", pady=4)
        Button(right, text="Open NekoBox", width=24, command=lambda: run_detached(["nekobox"])).pack(anchor="w", pady=4)
        Button(right, text="Run doctor in terminal", width=24, command=lambda: run_detached(["x-terminal-emulator", "-e", "sanchosctl", "system", "doctor"])).pack(anchor="w", pady=4)
        Button(right, text="Open VM networks", width=24, command=lambda: self.show_text_window("VM networks", query(["sanchosctl", "vm", "networks"]))).pack(anchor="w", pady=4)

    def _build_vms(self) -> None:
        toolbar = Frame(self.tab_vms)
        toolbar.pack(fill=BOTH, pady=(0, 10))
        Button(toolbar, text="Refresh", command=self.refresh_vms).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text="Start", command=lambda: self.vm_action("start")).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text="Stop", command=lambda: self.vm_action("stop")).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text="Console", command=lambda: self.vm_action("console", detached=True)).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text="Snapshots", command=self.show_snapshot_window).pack(side=LEFT, padx=(0, 8))

        self.vm_list = ttk.Treeview(self.tab_vms, columns=("id", "name", "state"), show="headings", height=20)
        self.vm_list.heading("id", text="Id")
        self.vm_list.heading("name", text="Name")
        self.vm_list.heading("state", text="State")
        self.vm_list.column("id", width=80)
        self.vm_list.column("name", width=240)
        self.vm_list.column("state", width=180)
        self.vm_list.pack(fill=BOTH, expand=True)

    def _build_network(self) -> None:
        Label(self.tab_network, text="Network summary", font=("Sans", 14, "bold")).pack(anchor="w", pady=(0, 8))
        self.network_text = ttk.Treeview(self.tab_network, columns=("key", "value"), show="headings", height=10)
        self.network_text.heading("key", text="Item")
        self.network_text.heading("value", text="Value")
        self.network_text.column("key", width=220)
        self.network_text.column("value", width=640)
        self.network_text.pack(fill=BOTH, expand=False)

        Button(self.tab_network, text="Show interfaces", command=lambda: self.show_text_window("Interfaces", query(["ip", "-brief", "address"]))).pack(anchor="w", pady=(14, 4))
        Button(self.tab_network, text="Show libvirt networks", command=lambda: self.show_text_window("Libvirt networks", query(["virsh", "net-list", "--all"]))).pack(anchor="w", pady=4)

    def _build_services(self) -> None:
        toolbar = Frame(self.tab_services)
        toolbar.pack(fill=BOTH, pady=(0, 10))
        Button(toolbar, text="Refresh", command=self.refresh_services).pack(side=LEFT, padx=(0, 8))
        Button(toolbar, text="Enable selected module", command=self.enable_selected_module).pack(side=LEFT)

        self.module_list = ttk.Treeview(self.tab_services, columns=("module", "status"), show="headings", height=16)
        self.module_list.heading("module", text="Module")
        self.module_list.heading("status", text="Status")
        self.module_list.column("module", width=280)
        self.module_list.column("status", width=180)
        self.module_list.pack(fill=BOTH, expand=True)

    def _build_appearance(self) -> None:
        Label(self.tab_appearance, text="Session defaults", font=("Sans", 14, "bold")).pack(anchor="w", pady=(0, 8))
        profile = read_text(STATE_DIR / "installed-profile", fallback="unknown")
        Label(self.tab_appearance, text=f"Installed profile: {profile}", justify="left").pack(anchor="w")
        Label(self.tab_appearance, text="The first pass keeps appearance control simple: wallpaper, Plasma defaults and the SDDM theme are installed by bootstrap.", wraplength=760, justify="left").pack(anchor="w", pady=(8, 12))
        Button(self.tab_appearance, text="Open wallpaper directory", command=lambda: run_detached(["xdg-open", "/usr/share/backgrounds/sanchos-os"])).pack(anchor="w", pady=4)
        Button(self.tab_appearance, text="Open first-boot state", command=lambda: self.show_text_window("First-boot state", read_text(Path.home() / ".config/sanchos-os/firstboot.json", fallback="No first-boot state found."))).pack(anchor="w", pady=4)

    def refresh_all(self) -> None:
        self.refresh_overview()
        self.refresh_vms()
        self.refresh_network()
        self.refresh_services()
        self.status.set("Refreshed")

    def refresh_overview(self) -> None:
        summary = [
            f"Hostname: {query(['hostname'])}",
            f"Kernel: {query(['uname', '-srmo'])}",
            f"OS: {query(['bash', '-lc', '. /etc/os-release && echo ${PRETTY_NAME:-Debian}'])}",
            f"Installed profile: {read_text(STATE_DIR / 'installed-profile', 'unknown')}",
            f"Desktop user: {read_text(STATE_DIR / 'desktop-user', 'not recorded')}",
        ]
        self.host_summary.config(text="\n".join(summary))
        self.doctor_summary.config(text=query(["sanchosctl", "system", "doctor"], fallback="Doctor unavailable"))

    def refresh_vms(self) -> None:
        for item in self.vm_list.get_children():
            self.vm_list.delete(item)
        table = query(["virsh", "list", "--all"], fallback="")
        for line in table.splitlines()[2:]:
            if not line.strip():
                continue
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            self.vm_list.insert("", END, values=(parts[0], parts[1], parts[2]))

    def refresh_network(self) -> None:
        for item in self.network_text.get_children():
            self.network_text.delete(item)
        entries = [
            ("NetworkManager", query(["systemctl", "is-active", "NetworkManager"])),
            ("libvirtd", query(["systemctl", "is-active", "libvirtd"])),
            ("Default route", query(["bash", "-lc", "ip route show default | head -n1"])),
            ("Primary address", query(["bash", "-lc", "hostname -I | awk '{print $1}'"])),
            ("NekoBox", shutil.which("nekobox") or "not installed"),
        ]
        for key, value in entries:
            self.network_text.insert("", END, values=(key, value))

    def refresh_services(self) -> None:
        for item in self.module_list.get_children():
            self.module_list.delete(item)
        enabled = set(read_text(STATE_DIR / "enabled-modules", "").splitlines())
        modules_dir = Path("/etc/sanchos-os/modules")
        if not modules_dir.exists():
            return
        for item in sorted(modules_dir.iterdir()):
            if not item.is_dir():
                continue
            status = "enabled" if item.name in enabled else "available"
            self.module_list.insert("", END, values=(item.name, status))

    def selected_vm_name(self) -> str | None:
        selected = self.vm_list.selection()
        if not selected:
            self.status.set("No VM selected")
            return None
        values = self.vm_list.item(selected[0], "values")
        return values[1] if len(values) >= 2 else None

    def selected_module_name(self) -> str | None:
        selected = self.module_list.selection()
        if not selected:
            self.status.set("No module selected")
            return None
        values = self.module_list.item(selected[0], "values")
        return values[0] if values else None

    def vm_action(self, action: str, detached: bool = False) -> None:
        name = self.selected_vm_name()
        if not name:
            return
        command = ["sanchosctl", "vm", action, name]
        if detached:
            run_detached(["x-terminal-emulator", "-e", *command])
        else:
            output = query(command, fallback="Action failed")
            self.status.set(output.splitlines()[0] if output else f"Ran {action} for {name}")
            self.refresh_vms()

    def enable_selected_module(self) -> None:
        name = self.selected_module_name()
        if not name:
            return
        if os.geteuid() != 0:
            self.status.set("Open control center as root to enable modules")
            return
        output = query(["sanchosctl", "module", "enable", name], fallback="Enable failed")
        self.status.set(output.splitlines()[0] if output else f"Enabled {name}")
        self.refresh_services()

    def show_snapshot_window(self) -> None:
        name = self.selected_vm_name()
        if not name:
            return
        self.show_text_window(f"Snapshots: {name}", query(["sanchosctl", "vm", "snapshot", "list", name], fallback="No snapshots found."))

    def show_text_window(self, title: str, text: str) -> None:
        window = Toplevel(self.root)
        window.title(title)
        window.geometry("760x480")
        box = ttk.Treeview(window, columns=("text",), show="headings")
        box.heading("text", text=title)
        box.column("text", width=720)
        box.pack(fill=BOTH, expand=True)
        for line in text.splitlines() or [text]:
            box.insert("", END, values=(line,))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = ControlCenter()
    app.run()


if __name__ == "__main__":
    main()
