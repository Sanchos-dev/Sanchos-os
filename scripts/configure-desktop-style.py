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
    if etc_root.exists():
        return etc_root
    return local_root


def resolve_script_path(name: str) -> Path:
    system_path = Path('/usr/local/lib/sanchos-os') / name
    repo_path = Path(__file__).resolve().parent / name
    if system_path.exists():
        return system_path
    return repo_path


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
    if not src.exists():
        return
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply the v9 desktop visual preset to a user home.')
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

    copy_if_exists(config_root / 'plasma' / 'kdeglobals', config / 'kdeglobals')
    copy_if_exists(config_root / 'plasma' / 'kwinrc', config / 'kwinrc')
    copy_if_exists(config_root / 'plasma' / 'plasmarc', config / 'plasmarc')
    copy_if_exists(config_root / 'plasma' / 'SanchosPurple.colors', local_share / 'color-schemes' / 'SanchosPurple.colors')
    copy_if_exists(config_root / 'i3' / 'config', config / 'i3' / 'config')

    env_dir = config / 'plasma-workspace' / 'env'
    env_dir.mkdir(parents=True, exist_ok=True)
    wm_script = env_dir / '90-sanchos-wm.sh'
    tiling_enabled = args.enable_tiling or not args.disable_tiling
    if tiling_enabled:
        wm_script.write_text('#!/usr/bin/env sh\nexport KDEWM=/usr/bin/i3\n')
        wm_script.chmod(0o755)
    else:
        wm_script.unlink(missing_ok=True)

    runtime_env = os.environ.copy()
    runtime_env.setdefault('HOME', str(home))
    runtime_env.setdefault('USER', args.user)

    wallpaper = args.wallpaper or preferred_wallpaper()
    if args.apply_now and (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        wallpaper_helper = resolve_script_path('apply-plasma-wallpaper.py')
        layout_helper = resolve_script_path('apply-plasma-layout.py')
        run(['python3', str(wallpaper_helper), wallpaper], env=runtime_env)
        if not args.skip_layout:
            run(['python3', str(layout_helper)], env=runtime_env)

    state_dir = config / 'sanchos-os'
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        'tiling_enabled': tiling_enabled,
        'wallpaper': wallpaper,
        'panel_layout': 'top-floating',
        'color_scheme': 'SanchosPurple',
        'icon_theme': 'sanchos-mono',
    }
    (state_dir / 'visual-preset.json').write_text(json.dumps(state, indent=2) + '\n')

    for path in [config / 'kdeglobals', config / 'kwinrc', config / 'plasmarc', config / 'i3', env_dir, state_dir, local_share / 'color-schemes']:
        if path.exists():
            chown_tree(path, args.user, args.user)

    print(f'Applied visual preset for user: {args.user}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
