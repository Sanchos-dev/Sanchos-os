#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

WALLPAPER_BASE = Path('/usr/share/backgrounds/sanchos-os')


def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    candidate = (WALLPAPER_BASE / value).resolve()
    if candidate.exists():
        return candidate
    return path.resolve()


def build_js(file_uri: str) -> str:
    image = json.dumps(file_uri)
    return (
        "var allDesktops = desktops();"
        "for (var i = 0; i < allDesktops.length; ++i) {"
        "var d = allDesktops[i];"
        "d.wallpaperPlugin = 'org.kde.image';"
        "d.currentConfigGroup = ['Wallpaper','org.kde.image','General'];"
        f"d.writeConfig('Image', {image});"
        f"d.writeConfig('PreviewImage', {image});"
        "d.writeConfig('FillMode', '2');"
        "}"
    )


def try_run(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    output = (proc.stdout or '') + (proc.stderr or '')
    return proc.returncode, output.strip()


def apply_once(path: Path) -> tuple[bool, str]:
    last_output = ''

    if shutil.which('plasma-apply-wallpaperimage'):
        rc, out = try_run(['plasma-apply-wallpaperimage', str(path)])
        if rc == 0:
            return True, 'Applied wallpaper with plasma-apply-wallpaperimage.'
        last_output = out

    if shutil.which('dbus-send'):
        js = build_js(path.resolve().as_uri())
        rc, out = try_run([
            'dbus-send',
            '--session',
            '--dest=org.kde.plasmashell',
            '--type=method_call',
            '/PlasmaShell',
            'org.kde.PlasmaShell.evaluateScript',
            f'string:{js}',
        ])
        if rc == 0:
            return True, 'Applied wallpaper through Plasma D-Bus.'
        last_output = out or last_output

    if shutil.which('qdbus'):
        js = build_js(path.resolve().as_uri())
        rc, out = try_run([
            'qdbus',
            'org.kde.plasmashell',
            '/PlasmaShell',
            'org.kde.PlasmaShell.evaluateScript',
            js,
        ])
        if rc == 0:
            return True, 'Applied wallpaper through qdbus.'
        last_output = out or last_output

    if not last_output:
        last_output = 'No supported wallpaper apply backend was available.'
    return False, last_output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply a wallpaper to the current Plasma session.')
    parser.add_argument('path', help='absolute path or path relative to /usr/share/backgrounds/sanchos-os')
    parser.add_argument('--wait-seconds', type=int, default=8)
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        if not args.quiet:
            print('No graphical session detected. Run inside KDE/Wayland/X11.', file=sys.stderr)
        return 1

    path = resolve_path(args.path)
    if not path.exists():
        if not args.quiet:
            print(f'Wallpaper not found: {path}', file=sys.stderr)
        return 1

    deadline = time.time() + max(args.wait_seconds, 0)
    last_message = 'Failed to apply wallpaper.'
    while True:
        ok, message = apply_once(path)
        last_message = message
        if ok:
            if not args.quiet:
                print(message)
            return 0
        if time.time() >= deadline:
            break
        time.sleep(1)

    if not args.quiet:
        print(last_message, file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
