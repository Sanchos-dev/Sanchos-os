#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, pwd, shutil, subprocess
from pathlib import Path

WALLPAPER_INDEX = Path('/usr/share/backgrounds/sanchos-os/index.json')

def resolve_config_root():
    local_root = Path(__file__).resolve().parent.parent / 'configs'
    etc_root = Path('/etc/sanchos-os/configs')
    return etc_root if etc_root.exists() else local_root

def resolve_script_path(name):
    system_path = Path('/usr/local/lib/sanchos-os') / name
    repo_path = Path(__file__).resolve().parent / name
    return system_path if system_path.exists() else repo_path

def preferred_wallpaper():
    try:
        data = json.loads(WALLPAPER_INDEX.read_text())
        default = data.get('default')
        if default:
            return default
    except Exception:
        pass
    return 'purple/purple0.png'

def run(command, env=None, timeout=18):
    return subprocess.run(command, check=False, env=env, timeout=timeout).returncode

def copy_if_exists(src, dst):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def chown_tree(path, user_name, group_name):
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

def write_config(file_name, key, groups, value, env):
    tool = shutil.which('kwriteconfig5') or shutil.which('kwriteconfig6')
    if not tool:
        return
    cmd = [tool, '--file', file_name]
    for g in groups:
        cmd.extend(['--group', g])
    cmd.extend(['--key', key, value])
    run(cmd, env=env)

def restart_hotkeys(env):
    if shutil.which('pkill'):
        run(['pkill', '-x', 'xbindkeys'], env=env)
    if shutil.which('xbindkeys'):
        subprocess.Popen(['/bin/sh', '-lc', 'xbindkeys -f "$HOME/.config/xbindkeysrc" >/dev/null 2>&1'], env=env)

def refresh_lookandfeel(env):
    for cmd in [
        ['plasma-apply-colorscheme', 'SanchosWarm'],
        ['plasma-apply-desktoptheme', 'breeze-dark'],
    ]:
        if shutil.which(cmd[0]):
            run(cmd, env=env, timeout=20)
    for cmd in [['kbuildsycoca5'], ['kbuildsycoca6']]:
        if shutil.which(cmd[0]):
            run(cmd, env=env, timeout=20)

def reconfigure_live_session(env):
    if shutil.which('qdbus'):
        run(['qdbus', 'org.kde.KWin', '/KWin', 'reconfigure'], env=env)
        run(['qdbus', 'org.kde.plasmashell', '/PlasmaShell', 'org.kde.PlasmaShell.reloadConfig'], env=env)

def main(argv=None):
    parser = argparse.ArgumentParser(description='Apply the v13 desktop preset to a user home.')
    default_user = os.environ.get('SANCHOS_DESKTOP_USER') or os.environ.get('SUDO_USER') or os.environ.get('USER') or 'root'
    parser.add_argument('--user', default=default_user)
    parser.add_argument('--enable-tiling', action='store_true')
    parser.add_argument('--disable-tiling', action='store_true')
    parser.add_argument('--apply-now', action='store_true')
    parser.add_argument('--skip-layout', action='store_true')
    parser.add_argument('--wallpaper', default='')
    args = parser.parse_args(argv)

    config_root = resolve_config_root()
    user = pwd.getpwnam(args.user)
    home = Path(os.environ.get('HOME', user.pw_dir))
    config = home / '.config'
    local_share = home / '.local' / 'share'

    for name in ['kdeglobals', 'kwinrc', 'plasmarc', 'konsolerc', 'kscreenlockerrc']:
        copy_if_exists(config_root / 'plasma' / name, config / name)
    for name in ['SanchosPurple.colors', 'SanchosWarm.colors']:
        copy_if_exists(config_root / 'plasma' / name, local_share / 'color-schemes' / name)
    copy_if_exists(config_root / 'plasma' / 'SanchosDark.profile', local_share / 'konsole' / 'SanchosDark.profile')
    copy_if_exists(config_root / 'plasma' / 'gtk-settings.ini', config / 'gtk-3.0' / 'settings.ini')
    copy_if_exists(config_root / 'plasma' / 'kvantum.kvconfig', config / 'Kvantum' / 'kvantum.kvconfig')
    copy_if_exists(config_root / 'system' / 'xbindkeysrc', config / 'xbindkeysrc')
    for name in ['config.rasi', 'sanchos-launcher.rasi']:
        copy_if_exists(config_root / 'rofi' / name, config / 'rofi' / name)

    runtime_env = os.environ.copy()
    runtime_env.update({'HOME': str(home), 'USER': args.user, 'LOGNAME': args.user, 'SANCHOS_DESKTOP_USER': args.user})

    tiling_enabled = args.enable_tiling and not args.disable_tiling
    env_dir = config / 'plasma-workspace' / 'env'
    env_dir.mkdir(parents=True, exist_ok=True)
    wm_script = env_dir / '90-sanchos-wm.sh'
    if tiling_enabled:
        wm_script.write_text('''#!/usr/bin/env sh
export KDEWM=/usr/bin/i3
''')
        wm_script.chmod(0o755)
    else:
        wm_script.unlink(missing_ok=True)

    wallpaper = args.wallpaper or preferred_wallpaper()
    write_config('kdeglobals', 'ColorScheme', ['General'], 'SanchosWarm', runtime_env)
    write_config('kdeglobals', 'font', ['General'], 'Inter,11,-1,5,50,0,0,0,0,0', runtime_env)
    write_config('kdeglobals', 'smallestReadableFont', ['General'], 'Inter,10,-1,5,50,0,0,0,0,0', runtime_env)
    write_config('kdeglobals', 'menuFont', ['General'], 'Inter,11,-1,5,50,0,0,0,0,0', runtime_env)
    write_config('kdeglobals', 'toolBarFont', ['General'], 'Inter,10,-1,5,50,0,0,0,0,0', runtime_env)
    write_config('kdeglobals', 'widgetStyle', ['KDE'], 'Breeze', runtime_env)
    write_config('kdeglobals', 'Theme', ['Icons'], 'Papirus-Dark', runtime_env)
    write_config('kwinrc', 'theme', ['org.kde.kdecoration2'], 'Breeze', runtime_env)
    write_config('konsolerc', 'DefaultProfile', ['Desktop Entry'], 'SanchosDark.profile', runtime_env)
    write_config('gtk-3.0/settings.ini', 'gtk-icon-theme-name', ['Settings'], 'Papirus-Dark', runtime_env)
    write_config('gtk-3.0/settings.ini', 'gtk-theme-name', ['Settings'], 'Breeze-Dark', runtime_env)

    refresh_lookandfeel(runtime_env)
    if args.apply_now and (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        run(['python3', str(resolve_script_path('apply-plasma-wallpaper.py')), wallpaper], env=runtime_env, timeout=20)
        if not args.skip_layout:
            run(['python3', str(resolve_script_path('apply-plasma-layout.py'))], env=runtime_env, timeout=24)
        restart_hotkeys(runtime_env)
        reconfigure_live_session(runtime_env)

    state_dir = config / 'sanchos-os'
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        'tiling_enabled': tiling_enabled,
        'wallpaper': wallpaper,
        'panel_layout': 'top-floating',
        'color_scheme': 'SanchosWarm',
        'icon_theme': 'Papirus-Dark',
        'window_style': 'Breeze',
        'launcher': 'rofi',
    }
    (state_dir / 'visual-preset.json').write_text(json.dumps(state, indent=2) + '\n')

    for path in [config / 'kdeglobals', config / 'kwinrc', config / 'plasmarc', config / 'konsolerc', config / 'rofi', config / 'xbindkeysrc', env_dir, state_dir, local_share / 'color-schemes', local_share / 'konsole', config / 'gtk-3.0', config / 'Kvantum']:
        if path.exists():
            chown_tree(path, args.user, args.user)
    print(f'Applied visual preset for user: {args.user}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
