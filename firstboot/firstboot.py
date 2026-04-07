#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tkinter import Button, Checkbutton, IntVar, Label, StringVar, Tk, OptionMenu

STATE_DIR = Path.home() / ".config" / "sanchos-os"
STATE_FILE = STATE_DIR / "firstboot.json"


def run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=False)
    except Exception:
        pass


def save_state(data: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2) + "\n")


def main() -> None:
    if STATE_FILE.exists():
        return

    root = Tk()
    root.title("sanchos-os setup")
    root.geometry("520x320")
    root.resizable(False, False)

    Label(root, text="Welcome to sanchos-os", font=("Sans", 18, "bold")).pack(pady=(18, 6))
    Label(root, text="Choose a few defaults for this session.", font=("Sans", 11)).pack(pady=(0, 16))

    theme_var = StringVar(value="dark")
    Label(root, text="Theme mode").pack()
    OptionMenu(root, theme_var, "dark", "light").pack(pady=(0, 12))

    enable_virt = IntVar(value=1)
    Checkbutton(root, text="Keep desktop virtualization tools enabled", variable=enable_virt).pack(anchor="w", padx=40)

    enable_nekobox = IntVar(value=1)
    Checkbutton(root, text="Show NekoBox in the desktop app set", variable=enable_nekobox).pack(anchor="w", padx=40)

    Label(root, text="This is an early setup flow. More options will move into the control center.", wraplength=440, justify="left").pack(pady=(18, 16))

    def finish() -> None:
        data = {
            "theme": theme_var.get(),
            "virtualization": bool(enable_virt.get()),
            "nekobox_visible": bool(enable_nekobox.get()),
        }
        save_state(data)
        if theme_var.get() == "dark":
            run(["lookandfeeltool", "-a", "org.kde.breezedark.desktop"])
        else:
            run(["lookandfeeltool", "-a", "org.kde.breeze.desktop"])
        root.destroy()

    Button(root, text="Finish", command=finish, width=18).pack()
    root.mainloop()


if __name__ == "__main__":
    main()
