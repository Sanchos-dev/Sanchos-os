#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pwd
import shutil
import subprocess
from pathlib import Path

WALLPAPER_INDEX = Path('/usr/share/backgrounds/sanchos-os/index.json')


def resolve_config_root() -> Path:
    local_root = Path(__file__).resolve().parent.parent / 'configs'
    etc_root = Path('/etc/sanchos-os/configs')
    return etc_root if etc_root.exists() else local_root


def resolve_script_path(name: str) -> Path:
    system_path = Path('/usr/local/lib/sanchos-os') / name
    repo_path = Path(__file__).resolve().parent / name
    return system_path if system_path.exists() else repo_path


def preferred_wallpaper() -> str:
    try:
        data = json.loads(WALLPAPER_INDEX.read_text())
        default = data.get('default')
        if default:
            return default
    except Exception:
        pass
    return 'purple/purple0.png'


def run(command: list[str], env: dict[str, str] | None = None) -> int:
    return subprocess.run(command, check=False, env=env).returncode


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def chown_tree(path: Path, user_name: str, group_name: str) -> None:
    try:
        shutil.chown(path, user=user_name, group=group_name)
    except Exception:
        return
    if path.is_dir():
        for child in path.rglob('*'):
            try:
                shutil.chown(child, user=user_name, group=group_name)
            except Exception:
                pass


def write_config(key: str, group: list[str], value: str, env: dict[str, str]) -> None:
    tool = shutil.which('kwriteconfig5') or shutil.which('kwriteconfig6')
    if not tool:
        return
    command = [tool, '--file', 'kdeglobals']
    for item in group:
        command.extend(['--group', item])
    command.extend(['--key', key, value])
    run(command, env=env)


def reconfigure_live_session(env: dict[str, str]) -> None:
    if shutil.which('qdbus'):
        run(['qdbus', 'org.kde.KWin', '/KWin', 'reconfigure'], env=env)
        run(['qdbus', 'org.kde.plasmashell', '/PlasmaShell', 'org.kde.PlasmaShell.reloadConfig'], env=env)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply the v10 desktop visual preset to a user home.')
    parser.add_argument('--user', default=os.environ.get('SUDO_USER') or os.environ.get('USER') or 'root')
    parser.add_argument('--enable-tiling', action='store_true')
    parser.add_argument('--disable-tiling', action='store_true')
    parser.add_argument('--apply-now', action='store_true')
    parser.add_argument('--skip-layout', action='store_true')
    parser.add_argument('--wallpaper', default='')
    args = parser.parse_args(argv)

    config_root = resolve_config_root()
    user = pwd.getpwnam(args.user)
    home = Path(user.pw_dir)
    config = home / '.config'
    local_share = home / '.local' / 'share'

    for name in ['kdeglobals', 'kwinrc', 'plasmarc', 'konsolerc']:
        copy_if_exists(config_root / 'plasma' / name, config / name)
    for name in ['SanchosPurple.colors', 'SanchosWarm.colors']:
        copy_if_exists(config_root / 'plasma' / name, local_share / 'color-schemes' / name)
    copy_if_exists(config_root / 'plasma' / 'SanchosDark.profile', local_share / 'konsole' / 'SanchosDark.profile')
    copy_if_exists(config_root / 'plasma' / 'gtk-settings.ini', config / 'gtk-3.0' / 'settings.ini')
    copy_if_exists(config_root / 'plasma' / 'kvantum.kvconfig', config / 'Kvantum' / 'kvantum.kvconfig')
    copy_if_exists(config_root / 'i3' / 'config', config / 'i3' / 'config')

    env_dir = config / 'plasma-workspace' / 'env'
    env_dir.mkdir(parents=True, exist_ok=True)
    wm_script = env_dir / '90-sanchos-wm.sh'
    tiling_enabled = args.enable_tiling and not args.disable_tiling
    if tiling_enabled:
        wm_script.write_text('#!/usr/bin/env sh\nexport KDEWM=/usr/bin/i3\n')
        wm_script.chmod(0o755)
    else:
        wm_script.unlink(missing_ok=True)

    runtime_env = os.environ.copy()
    runtime_env.update({'HOME': str(home), 'USER': args.user})

    wallpaper = args.wallpaper or preferred_wallpaper()
    write_config('ColorScheme', ['General'], 'SanchosWarm', runtime_env)
    write_config('widgetStyle', ['KDE'], 'kvantum-dark', runtime_env)
    write_config('Theme', ['Icons'], 'sanchos-mono', runtime_env)

    if args.apply_now and (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        wallpaper_helper = resolve_script_path('apply-plasma-wallpaper.py')
        layout_helper = resolve_script_path('apply-plasma-layout.py')
        run(['python3', str(wallpaper_helper), wallpaper], env=runtime_env)
        if not args.skip_layout:
            run(['python3', str(layout_helper)], env=runtime_env)
        reconfigure_live_session(runtime_env)

    state_dir = config / 'sanchos-os'
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        'tiling_enabled': tiling_enabled,
        'wallpaper': wallpaper,
        'panel_layout': 'top-floating',
        'color_scheme': 'SanchosWarm',
        'icon_theme': 'sanchos-mono',
        'window_style': 'kvantum-dark',
    }
    (state_dir / 'visual-preset.json').write_text(json.dumps(state, indent=2) + '\n')

    for path in [config / 'kdeglobals', config / 'kwinrc', config / 'plasmarc', config / 'konsolerc', config / 'i3', env_dir, state_dir, local_share / 'color-schemes', local_share / 'konsole', config / 'gtk-3.0', config / 'Kvantum']:
        if path.exists():
            chown_tree(path, args.user, args.user)

    print(f'Applied visual preset for user: {args.user}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
