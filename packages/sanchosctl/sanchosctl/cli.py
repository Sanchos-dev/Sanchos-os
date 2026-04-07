#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

STATE_DIR = Path('/etc/sanchos-os/state')
ENABLED_MODULES_FILE = STATE_DIR / 'enabled-modules'
WALLPAPER_DIR = Path('/usr/share/backgrounds/sanchos-os')
WALLPAPER_INDEX = WALLPAPER_DIR / 'index.json'
PLASMA_WALLPAPER_ROOT = Path('/usr/share/wallpapers')
DEFAULT_VM_STORAGE = Path('/var/lib/libvirt/images')
LIBVIRT_DEFAULT_NETWORK = 'default'
VALID_WALLPAPER_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.svg'}


def scan_wallpapers() -> dict:
    collections: dict[str, list[str]] = {}
    if not WALLPAPER_DIR.exists():
        return {'default': 'purple/purple0.png', 'collections': {'purple': [], 'default': [], 'fox': []}}
    for path in sorted(WALLPAPER_DIR.rglob('*')):
        if not path.is_file() or path.name == 'index.json':
            continue
        if path.suffix.lower() not in VALID_WALLPAPER_EXTS:
            continue
        rel = path.relative_to(WALLPAPER_DIR).as_posix()
        parts = rel.split('/')
        collection = parts[0] if len(parts) > 1 else 'default'
        collections.setdefault(collection, []).append(rel)
    ordered = {name: collections.pop(name, []) for name in ['purple', 'default', 'fox']}
    for name in sorted(collections):
        ordered[name] = collections[name]
    preferred_defaults = ['purple/purple0.png', 'default/wp0.png']
    available = {item for values in ordered.values() for item in values}
    default_path = 'unset'
    for candidate in preferred_defaults:
        if candidate in available:
            default_path = candidate
            break
    if default_path == 'unset':
        for items in ordered.values():
            if items:
                default_path = items[0]
                break
    return {'default': default_path, 'collections': ordered}


def load_wallpaper_index() -> dict:
    try:
        if WALLPAPER_INDEX.exists():
            return json.loads(WALLPAPER_INDEX.read_text())
    except Exception:
        pass
    return scan_wallpapers()


def save_wallpaper_index(data: dict) -> None:
    WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
    WALLPAPER_INDEX.write_text(json.dumps(data, indent=2) + '\n')


def resolve_wallpaper_path(value: str) -> tuple[str, Path]:
    path = Path(value).expanduser()
    if path.is_absolute():
        resolved = path.resolve()
        if WALLPAPER_DIR in resolved.parents or resolved == WALLPAPER_DIR:
            rel = resolved.relative_to(WALLPAPER_DIR).as_posix()
        else:
            rel = resolved.name
        return rel, resolved
    resolved = (WALLPAPER_DIR / value).resolve()
    return value, resolved


def find_root() -> Path:
    cwd = Path.cwd()
    for base in [cwd, *cwd.parents]:
        if (base / 'profiles').is_dir() and (base / 'modules').is_dir():
            return base
    if Path('/etc/sanchos-os/profiles').is_dir() and Path('/etc/sanchos-os/modules').is_dir():
        return Path('/etc/sanchos-os')
    return cwd


ROOT = find_root()
PROFILES_DIR = ROOT / 'profiles'
MODULES_DIR = ROOT / 'modules'


def run(command: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(command, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def stream(command: list[str]) -> int:
    return subprocess.run(command, check=False).returncode


def print_header(title: str) -> None:
    print(title)
    print('-' * len(title))


def load_yaml(path: Path) -> dict:
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


def require_root_for_mutation() -> None:
    if os.geteuid() != 0:
        raise SystemExit('This action requires root.')


def read_enabled_modules() -> list[str]:
    if not ENABLED_MODULES_FILE.exists():
        return []
    return [line.strip() for line in ENABLED_MODULES_FILE.read_text().splitlines() if line.strip()]


def write_enabled_modules(names: list[str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ENABLED_MODULES_FILE.write_text('\n'.join(sorted(set(names))) + '\n')


def read_state_value(name: str, default: str = '') -> str:
    path = STATE_DIR / name
    if not path.exists():
        return default
    return path.read_text().strip() or default


def apt_install(packages: list[str]) -> int:
    if not packages:
        return 0
    rc, _, stderr = run(['apt-get', 'update'])
    if rc != 0:
        print(stderr)
        return rc
    rc, _, stderr = run(['apt-get', 'install', '-y', *packages])
    if rc != 0:
        print(stderr)
    return rc


def ensure_vm_exists(name: str) -> bool:
    if not require_virsh():
        return False
    rc, _, _ = run(['virsh', 'dominfo', name])
    if rc != 0:
        print(f'VM not found: {name}')
        return False
    return True


def find_helper(name: str) -> Path | None:
    candidates = [
        ROOT / 'scripts' / name,
        Path('/usr/local/lib/sanchos-os') / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def sync_plasma_wallpaper_packages() -> int:
    helper = find_helper('install-plasma-wallpaper-packages.py')
    if helper is None:
        print('Wallpaper package sync helper not found.')
        return 1
    rc, stdout, stderr = run(['python3', str(helper), str(WALLPAPER_DIR), str(PLASMA_WALLPAPER_ROOT)])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def apply_wallpaper(value: str, quiet: bool = False) -> int:
    _, path = resolve_wallpaper_path(value)
    if not path.exists():
        if not quiet:
            print(f'Wallpaper not found: {value}')
        return 1
    helper = find_helper('apply-plasma-wallpaper.py')
    if helper is None:
        if not quiet:
            print('Wallpaper apply helper not found.')
        return 1
    command = ['python3', str(helper), str(path)]
    if quiet:
        command.append('--quiet')
    rc, stdout, stderr = run(command)
    if not quiet:
        if stdout:
            print(stdout)
        if rc != 0 and stderr:
            print(stderr)
    return rc


def apply_panel_layout(quiet: bool = False) -> int:
    helper = find_helper('apply-plasma-layout.py')
    if helper is None:
        if not quiet:
            print('Plasma layout helper not found.')
        return 1
    command = ['python3', str(helper)]
    if quiet:
        command.append('--quiet')
    rc, stdout, stderr = run(command)
    if not quiet:
        if stdout:
            print(stdout)
        if rc != 0 and stderr:
            print(stderr)
    return rc


def preferred_visual_user() -> str:
    user = read_state_value('desktop-user')
    if user:
        return user
    return os.environ.get('SUDO_USER') or os.environ.get('USER') or 'root'


def apply_visual_preset(user: str | None = None, apply_now: bool = False, tiling_enabled: bool = False) -> int:
    helper = find_helper('configure-desktop-style.py')
    if helper is None:
        print('Visual preset helper not found.')
        return 1
    actual_user = user or preferred_visual_user()
    command = ['python3', str(helper), '--user', actual_user]
    command.append('--enable-tiling' if tiling_enabled else '--disable-tiling')
    if apply_now:
        command.append('--apply-now')
    rc, stdout, stderr = run(command)
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


# system commands

def cmd_system_info(_: argparse.Namespace) -> int:
    print_header('System information')
    print(f'Hostname: {platform.node()}')
    print(f'Kernel:   {platform.release()}')
    print(f'Machine:  {platform.machine()}')
    print(f'Python:   {platform.python_version()}')
    print(f'Root dir: {ROOT}')
    print(f'Profile:  {read_state_value("installed-profile", "unknown")}')
    os_release = Path('/etc/os-release')
    if os_release.exists():
        values = {}
        for line in os_release.read_text().splitlines():
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            values[key] = value.strip().strip('"')
        pretty = values.get('PRETTY_NAME')
        if pretty:
            print(f'OS:       {pretty}')
    return 0


def cmd_system_doctor(_: argparse.Namespace) -> int:
    print_header('System doctor')
    checks = [
        ('kvm device', Path('/dev/kvm').exists()),
        ('qemu-system-x86_64', shutil.which('qemu-system-x86_64') is not None),
        ('virsh', shutil.which('virsh') is not None),
        ('virt-install', shutil.which('virt-install') is not None),
        ('podman', shutil.which('podman') is not None),
        ('i3', shutil.which('i3') is not None),
        ('nekobox', shutil.which('nekobox') is not None or Path('/opt/nekobox/nekobox.AppImage').exists()),
        ('control center', Path('/usr/local/bin/sanchos-control-center').exists()),
        ('wallpaper index', WALLPAPER_INDEX.exists()),
        ('wallpaper apply helper', find_helper('apply-plasma-wallpaper.py') is not None),
        ('visual preset helper', find_helper('configure-desktop-style.py') is not None),
    ]
    rc, stdout, _ = run(['systemctl', 'is-active', 'libvirtd'])
    checks.append(('libvirtd active', rc == 0 and stdout == 'active'))
    for name, status in checks:
        print(f"[{'ok' if status else 'missing'}] {name}")
    missing = [name for name, status in checks if not status]
    if missing:
        print('\nSome components are missing or inactive.')
        return 1
    print('\nEverything required by the current doctor checks looks ready.')
    return 0


def cmd_system_reset(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    uninstall = ROOT / 'bootstrap' / 'uninstall.sh'
    if not uninstall.exists():
        uninstall = Path('/usr/local/share/sanchos-os/uninstall.sh')
    if not uninstall.exists():
        print('No uninstall helper found.')
        return 1
    if not args.yes:
        print('This will remove files and packages installed by the bootstrap path.')
        print('Run again with --yes to continue.')
        return 1
    return stream(['bash', str(uninstall)])


# profile/module commands

def cmd_profile_list(_: argparse.Namespace) -> int:
    print_header('Profiles')
    if not PROFILES_DIR.exists():
        print('profiles directory not found')
        return 1
    for item in sorted(PROFILES_DIR.glob('*.yaml')):
        print(item.stem)
    return 0


def cmd_profile_info(args: argparse.Namespace) -> int:
    path = PROFILES_DIR / f'{args.name}.yaml'
    if not path.exists():
        print(f'profile not found: {args.name}')
        return 1
    data = load_yaml(path)
    print_header(f'Profile: {args.name}')
    print(data.get('description') or data.get('summary') or '')
    print('\nPackages:')
    for item in data.get('packages', []):
        print(f'- {item}')
    print('\nModules:')
    for item in data.get('modules', []):
        print(f'- {item}')
    return 0


def cmd_profile_apply(args: argparse.Namespace) -> int:
    path = PROFILES_DIR / f'{args.name}.yaml'
    if not path.exists():
        print(f'profile not found: {args.name}')
        return 1
    require_root_for_mutation()
    data = load_yaml(path)
    packages = data.get('packages', [])
    modules = data.get('modules', [])
    if apt_install(packages) != 0:
        return 1
    current_modules = read_enabled_modules()
    write_enabled_modules(current_modules + modules)
    print(f'Applied profile: {args.name}')
    return 0


def cmd_module_list(_: argparse.Namespace) -> int:
    print_header('Modules')
    if not MODULES_DIR.exists():
        print('modules directory not found')
        return 1
    enabled = set(read_enabled_modules())
    for item in sorted(MODULES_DIR.iterdir()):
        if item.is_dir():
            suffix = ' (enabled)' if item.name in enabled else ''
            print(f'{item.name}{suffix}')
    return 0


def cmd_module_info(args: argparse.Namespace) -> int:
    path = MODULES_DIR / args.name / 'module.yaml'
    if not path.exists():
        print(f'module not found: {args.name}')
        return 1
    data = load_yaml(path)
    print_header(f'Module: {args.name}')
    print(data.get('description') or data.get('summary') or '')
    print('\nPackages:')
    for item in data.get('packages', []):
        print(f'- {item}')
    print('\nServices:')
    for item in data.get('services', []):
        print(f'- {item}')
    return 0


def cmd_module_enable(args: argparse.Namespace) -> int:
    path = MODULES_DIR / args.name / 'module.yaml'
    if not path.exists():
        print(f'module not found: {args.name}')
        return 1
    require_root_for_mutation()
    data = load_yaml(path)
    packages = data.get('packages', [])
    services = data.get('services', [])
    if apt_install(packages) != 0:
        return 1
    for service in services:
        run(['systemctl', 'enable', service])
        run(['systemctl', 'start', service])
    enabled = read_enabled_modules()
    write_enabled_modules(enabled + [args.name])
    print(f'Enabled module: {args.name}')
    return 0


# VM commands

def require_virsh() -> bool:
    if shutil.which('virsh') is None:
        print('virsh is not installed or not in PATH')
        return False
    return True


def require_virt_install() -> bool:
    if shutil.which('virt-install') is None:
        print('virt-install is not installed or not in PATH')
        return False
    return True


def cmd_vm_list(_: argparse.Namespace) -> int:
    if not require_virsh():
        return 1
    rc, stdout, stderr = run(['virsh', 'list', '--all'])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_info(args: argparse.Namespace) -> int:
    if not ensure_vm_exists(args.name):
        return 1
    rc, stdout, stderr = run(['virsh', 'dominfo', args.name])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_start(args: argparse.Namespace) -> int:
    if not ensure_vm_exists(args.name):
        return 1
    rc, stdout, stderr = run(['virsh', 'start', args.name])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_stop(args: argparse.Namespace) -> int:
    if not ensure_vm_exists(args.name):
        return 1
    rc, stdout, stderr = run(['virsh', 'shutdown', args.name])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_delete(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    if not ensure_vm_exists(args.name):
        return 1
    if not args.yes:
        print('Refusing to delete without --yes.')
        return 1
    run(['virsh', 'destroy', args.name])
    command = ['virsh', 'undefine', args.name]
    if args.remove_storage:
        command.append('--remove-all-storage')
    rc, stdout, stderr = run(command)
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_console(args: argparse.Namespace) -> int:
    if not ensure_vm_exists(args.name):
        return 1
    if shutil.which('virt-viewer'):
        return stream(['virt-viewer', '--connect', 'qemu:///system', args.name])
    print('virt-viewer is not installed. Falling back to virsh console.')
    print('Use Ctrl+] to leave the console.')
    return stream(['virsh', 'console', args.name])


def cmd_vm_create(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    if not require_virt_install():
        return 1
    iso_value = args.iso or args.iso_positional
    if not iso_value:
        print('An ISO path is required. Use --iso <path> or provide it as the second positional argument.')
        return 1
    iso = Path(iso_value).expanduser().resolve()
    if not iso.exists():
        print(f'ISO not found: {iso}')
        return 1
    memory = args.memory if args.memory is not None else (args.memory_positional or 4096)
    vcpus = args.vcpus if args.vcpus is not None else (args.vcpus_positional or 4)
    disk_size = args.disk_size if args.disk_size is not None else (args.disk_size_positional or 64)
    disk_dir = Path(args.disk_dir).expanduser() if args.disk_dir else DEFAULT_VM_STORAGE
    disk_dir.mkdir(parents=True, exist_ok=True)
    disk_path = disk_dir / f'{args.name}.qcow2'
    command = [
        'virt-install',
        '--name', args.name,
        '--memory', str(memory),
        '--vcpus', str(vcpus),
        '--disk', f'path={disk_path},size={disk_size},format=qcow2,bus=virtio',
        '--cdrom', str(iso),
        '--network', f'network={args.network},model=virtio',
        '--graphics', args.graphics,
        '--video', args.video,
        '--os-variant', args.os_variant,
        '--boot', 'uefi',
        '--noautoconsole',
    ]
    print('Running:')
    print(' '.join(shlex.quote(part) for part in command))
    rc, stdout, stderr = run(command)
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_snapshot_list(args: argparse.Namespace) -> int:
    if not ensure_vm_exists(args.name):
        return 1
    rc, stdout, stderr = run(['virsh', 'snapshot-list', args.name])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_snapshot_create(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    if not ensure_vm_exists(args.name):
        return 1
    command = ['virsh', 'snapshot-create-as', args.name, args.snapshot]
    if args.description:
        command.extend(['--description', args.description])
    if args.disk_only:
        command.append('--disk-only')
    rc, stdout, stderr = run(command)
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_snapshot_revert(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    if not ensure_vm_exists(args.name):
        return 1
    rc, stdout, stderr = run(['virsh', 'snapshot-revert', args.name, args.snapshot])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_networks(_: argparse.Namespace) -> int:
    if not require_virsh():
        return 1
    rc, stdout, stderr = run(['virsh', 'net-list', '--all'])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


# wallpaper commands

def cmd_wallpaper_list(_: argparse.Namespace) -> int:
    print_header('Wallpapers')
    data = load_wallpaper_index()
    print(f"Default: {data.get('default', 'unset')}")
    for name, items in data.get('collections', {}).items():
        print(f'\n{name}:')
        for item in items:
            print(f'- {item}')
    return 0


def cmd_wallpaper_rescan(_: argparse.Namespace) -> int:
    require_root_for_mutation()
    data = scan_wallpapers()
    save_wallpaper_index(data)
    total = sum(len(items) for items in data.get('collections', {}).values())
    print(f'Rebuilt wallpaper index with {total} wallpaper(s).')
    sync_plasma_wallpaper_packages()
    return 0


def cmd_wallpaper_set_default(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    data = load_wallpaper_index()
    all_items = {item for items in data.get('collections', {}).values() for item in items}
    if args.path not in all_items:
        _, resolved = resolve_wallpaper_path(args.path)
        if resolved.exists() and WALLPAPER_DIR in resolved.parents:
            args.path = resolved.relative_to(WALLPAPER_DIR).as_posix()
        else:
            print(f'Wallpaper not found in index: {args.path}')
            return 1
    data['default'] = args.path
    save_wallpaper_index(data)
    print(f'Set default wallpaper: {args.path}')
    if args.apply:
        return apply_wallpaper(args.path, quiet=False)
    return 0


def cmd_wallpaper_apply(args: argparse.Namespace) -> int:
    return apply_wallpaper(args.path, quiet=args.quiet)


def cmd_wallpaper_apply_default(args: argparse.Namespace) -> int:
    data = load_wallpaper_index()
    target = data.get('default')
    if not target or target == 'unset':
        if not args.quiet:
            print('No default wallpaper is configured.')
        return 1
    return apply_wallpaper(target, quiet=args.quiet)


def cmd_visual_apply(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    return apply_visual_preset(user=args.user, apply_now=args.apply_now, tiling_enabled=not args.no_tiling)


def cmd_visual_panel(args: argparse.Namespace) -> int:
    return apply_panel_layout(quiet=args.quiet)


def cmd_visual_tiling_enable(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    return apply_visual_preset(user=args.user, apply_now=False, tiling_enabled=True)


def cmd_visual_tiling_disable(args: argparse.Namespace) -> int:
    require_root_for_mutation()
    return apply_visual_preset(user=args.user, apply_now=False, tiling_enabled=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='sanchosctl')
    subparsers = parser.add_subparsers(dest='group', required=True)

    system = subparsers.add_parser('system')
    system_sub = system.add_subparsers(dest='action', required=True)
    system_sub.add_parser('info').set_defaults(func=cmd_system_info)
    system_sub.add_parser('doctor').set_defaults(func=cmd_system_doctor)
    system_reset = system_sub.add_parser('reset')
    system_reset.add_argument('--yes', action='store_true')
    system_reset.set_defaults(func=cmd_system_reset)

    profile = subparsers.add_parser('profile')
    profile_sub = profile.add_subparsers(dest='action', required=True)
    profile_sub.add_parser('list').set_defaults(func=cmd_profile_list)
    profile_info = profile_sub.add_parser('info')
    profile_info.add_argument('name')
    profile_info.set_defaults(func=cmd_profile_info)
    profile_apply = profile_sub.add_parser('apply')
    profile_apply.add_argument('name')
    profile_apply.set_defaults(func=cmd_profile_apply)

    module = subparsers.add_parser('module')
    module_sub = module.add_subparsers(dest='action', required=True)
    module_sub.add_parser('list').set_defaults(func=cmd_module_list)
    module_info = module_sub.add_parser('info')
    module_info.add_argument('name')
    module_info.set_defaults(func=cmd_module_info)
    module_enable = module_sub.add_parser('enable')
    module_enable.add_argument('name')
    module_enable.set_defaults(func=cmd_module_enable)

    vm = subparsers.add_parser('vm')
    vm_sub = vm.add_subparsers(dest='action', required=True)
    vm_sub.add_parser('list').set_defaults(func=cmd_vm_list)
    vm_sub.add_parser('networks').set_defaults(func=cmd_vm_networks)
    vm_info = vm_sub.add_parser('info')
    vm_info.add_argument('name')
    vm_info.set_defaults(func=cmd_vm_info)
    vm_start = vm_sub.add_parser('start')
    vm_start.add_argument('name')
    vm_start.set_defaults(func=cmd_vm_start)
    vm_stop = vm_sub.add_parser('stop')
    vm_stop.add_argument('name')
    vm_stop.set_defaults(func=cmd_vm_stop)
    vm_delete = vm_sub.add_parser('delete')
    vm_delete.add_argument('name')
    vm_delete.add_argument('--remove-storage', action='store_true')
    vm_delete.add_argument('--yes', action='store_true')
    vm_delete.set_defaults(func=cmd_vm_delete)
    vm_console = vm_sub.add_parser('console')
    vm_console.add_argument('name')
    vm_console.set_defaults(func=cmd_vm_console)
    vm_create = vm_sub.add_parser('create')
    vm_create.add_argument('name')
    vm_create.add_argument('iso_positional', nargs='?')
    vm_create.add_argument('disk_size_positional', nargs='?', type=int)
    vm_create.add_argument('memory_positional', nargs='?', type=int)
    vm_create.add_argument('vcpus_positional', nargs='?', type=int)
    vm_create.add_argument('--iso', help='Path to installation ISO')
    vm_create.add_argument('--memory', type=int)
    vm_create.add_argument('--vcpus', type=int)
    vm_create.add_argument('--disk-size', type=int, help='Disk size in GiB')
    vm_create.add_argument('--disk-dir', default=str(DEFAULT_VM_STORAGE))
    vm_create.add_argument('--network', default=LIBVIRT_DEFAULT_NETWORK)
    vm_create.add_argument('--graphics', default='spice')
    vm_create.add_argument('--video', default='qxl')
    vm_create.add_argument('--os-variant', default='debian12')
    vm_create.set_defaults(func=cmd_vm_create)
    vm_snapshot = vm_sub.add_parser('snapshot')
    vm_snapshot_sub = vm_snapshot.add_subparsers(dest='snapshot_action', required=True)
    vm_snapshot_list = vm_snapshot_sub.add_parser('list')
    vm_snapshot_list.add_argument('name')
    vm_snapshot_list.set_defaults(func=cmd_vm_snapshot_list)
    vm_snapshot_create = vm_snapshot_sub.add_parser('create')
    vm_snapshot_create.add_argument('name')
    vm_snapshot_create.add_argument('snapshot')
    vm_snapshot_create.add_argument('--description')
    vm_snapshot_create.add_argument('--disk-only', action='store_true')
    vm_snapshot_create.set_defaults(func=cmd_vm_snapshot_create)
    vm_snapshot_revert = vm_snapshot_sub.add_parser('revert')
    vm_snapshot_revert.add_argument('name')
    vm_snapshot_revert.add_argument('snapshot')
    vm_snapshot_revert.set_defaults(func=cmd_vm_snapshot_revert)

    wallpaper = subparsers.add_parser('wallpaper')
    wallpaper_sub = wallpaper.add_subparsers(dest='action', required=True)
    wallpaper_sub.add_parser('list').set_defaults(func=cmd_wallpaper_list)
    wallpaper_rescan = wallpaper_sub.add_parser('rescan')
    wallpaper_rescan.set_defaults(func=cmd_wallpaper_rescan)
    wallpaper_set_default = wallpaper_sub.add_parser('set-default')
    wallpaper_set_default.add_argument('path')
    wallpaper_set_default.add_argument('--apply', action='store_true')
    wallpaper_set_default.set_defaults(func=cmd_wallpaper_set_default)
    wallpaper_apply = wallpaper_sub.add_parser('apply')
    wallpaper_apply.add_argument('path')
    wallpaper_apply.add_argument('--quiet', action='store_true')
    wallpaper_apply.set_defaults(func=cmd_wallpaper_apply)
    wallpaper_apply_default = wallpaper_sub.add_parser('apply-default')
    wallpaper_apply_default.add_argument('--quiet', action='store_true')
    wallpaper_apply_default.set_defaults(func=cmd_wallpaper_apply_default)
    visual = subparsers.add_parser('visual')
    visual_sub = visual.add_subparsers(dest='action', required=True)
    visual_apply = visual_sub.add_parser('apply')
    visual_apply.add_argument('--user')
    visual_apply.add_argument('--apply-now', action='store_true')
    visual_apply.add_argument('--no-tiling', action='store_true')
    visual_apply.set_defaults(func=cmd_visual_apply)
    visual_panel = visual_sub.add_parser('panel')
    visual_panel.add_argument('--quiet', action='store_true')
    visual_panel.set_defaults(func=cmd_visual_panel)
    visual_tiling = visual_sub.add_parser('tiling')
    visual_tiling_sub = visual_tiling.add_subparsers(dest='tiling_action', required=True)
    visual_tiling_enable = visual_tiling_sub.add_parser('enable')
    visual_tiling_enable.add_argument('--user')
    visual_tiling_enable.set_defaults(func=cmd_visual_tiling_enable)
    visual_tiling_disable = visual_tiling_sub.add_parser('disable')
    visual_tiling_disable.add_argument('--user')
    visual_tiling_disable.set_defaults(func=cmd_visual_tiling_disable)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
