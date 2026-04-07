#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from tkinter import BOTH, LEFT, RIGHT, Button, Frame, Label, Tk


def query(command: list[str], fallback: str = "Unavailable") -> str:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        text = proc.stdout.strip() or proc.stderr.strip()
        return text or fallback
    except Exception:
        return fallback


def main() -> None:
    root = Tk()
    root.title("Sanchos Control Center")
    root.geometry("840x520")

    header = Frame(root, padx=18, pady=18)
    header.pack(fill=BOTH)
    Label(header, text="Sanchos Control Center", font=("Sans", 20, "bold")).pack(anchor="w")
    Label(header, text="Early host management shell", font=("Sans", 11)).pack(anchor="w")

    body = Frame(root, padx=18, pady=8)
    body.pack(fill=BOTH, expand=True)

    left = Frame(body)
    left.pack(side=LEFT, fill=BOTH, expand=True)

    right = Frame(body)
    right.pack(side=RIGHT, fill=BOTH, expand=True)

    Label(left, text="System", font=("Sans", 14, "bold")).pack(anchor="w", pady=(0, 6))
    Label(left, text=query(["uname", "-srmo"]), justify="left", wraplength=340).pack(anchor="w")
    Label(left, text="\nVirtualization", font=("Sans", 14, "bold")).pack(anchor="w", pady=(12, 6))

    if shutil.which("virsh"):
        vm_data = query(["virsh", "list", "--all"], fallback="No VMs found.")
    else:
        vm_data = "virsh is not installed."
    Label(left, text=vm_data, justify="left", font=("Courier", 10), wraplength=360).pack(anchor="w")

    Label(right, text="Quick actions", font=("Sans", 14, "bold")).pack(anchor="w", pady=(0, 10))
    Button(right, text="Open virt-manager", width=24, command=lambda: subprocess.Popen(["virt-manager"])).pack(anchor="w", pady=4)
    Button(right, text="Open NekoBox", width=24, command=lambda: subprocess.Popen(["nekobox"])).pack(anchor="w", pady=4)
    Button(right, text="Run system doctor", width=24, command=lambda: subprocess.Popen(["x-terminal-emulator", "-e", "sanchosctl", "system", "doctor"])).pack(anchor="w", pady=4)

    root.mainloop()


if __name__ == "__main__":
    main()
