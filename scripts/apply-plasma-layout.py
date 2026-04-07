#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def resolve_layout_script() -> Path:
    system_script = Path('/etc/sanchos-os/configs/plasma/panel-layout.js')
    repo_script = Path(__file__).resolve().parent.parent / 'configs' / 'plasma' / 'panel-layout.js'
    if system_script.exists():
        return system_script
    return repo_script


def run(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    return proc.returncode, ((proc.stdout or '') + (proc.stderr or '')).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply the default Plasma top panel layout for sanchos-os.')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        if not args.quiet:
            print('No graphical session detected. Run this inside Plasma.', file=sys.stderr)
        return 1

    layout_script = resolve_layout_script()
    if not layout_script.exists():
        if not args.quiet:
            print(f'Layout script not found: {layout_script}', file=sys.stderr)
        return 1
    js = layout_script.read_text()
    last = 'No Plasma D-Bus helper was available.'

    if shutil.which('dbus-send'):
        rc, out = run([
            'dbus-send', '--session', '--dest=org.kde.plasmashell', '--type=method_call',
            '/PlasmaShell', 'org.kde.PlasmaShell.evaluateScript', f'string:{js}'
        ])
        if rc == 0:
            if not args.quiet:
                print('Applied Plasma top panel layout.')
            return 0
        last = out or last

    if shutil.which('qdbus'):
        rc, out = run(['qdbus', 'org.kde.plasmashell', '/PlasmaShell', 'org.kde.PlasmaShell.evaluateScript', js])
        if rc == 0:
            if not args.quiet:
                print('Applied Plasma top panel layout.')
            return 0
        last = out or last

    if not args.quiet:
        print(last, file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
