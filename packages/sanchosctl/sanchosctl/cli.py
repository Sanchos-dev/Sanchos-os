#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


STATE_DIR = Path("/etc/sanchos-os/state")
ENABLED_MODULES_FILE = STATE_DIR / "enabled-modules"


def find_root() -> Path:
    cwd = Path.cwd()
    for base in [cwd, *cwd.parents]:
        if (base / "profiles").is_dir() and (base / "modules").is_dir():
            return base
    if Path("/etc/sanchos-os/profiles").is_dir() and Path("/etc/sanchos-os/modules").is_dir():
        return Path("/etc/sanchos-os")
    return cwd


ROOT = find_root()
PROFILES_DIR = ROOT / "profiles"
MODULES_DIR = ROOT / "modules"


def run(command: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(command, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def print_header(title: str) -> None:
    print(title)
    print("-" * len(title))


def load_yaml(path: Path) -> dict:
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


def require_root_for_mutation() -> None:
    if os.geteuid() != 0:
        raise SystemExit("This action requires root.")


def read_enabled_modules() -> list[str]:
    if not ENABLED_MODULES_FILE.exists():
        return []
    return [line.strip() for line in ENABLED_MODULES_FILE.read_text().splitlines() if line.strip()]


def write_enabled_modules(names: list[str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ENABLED_MODULES_FILE.write_text("\n".join(sorted(set(names))) + "\n")


def cmd_system_info(_: argparse.Namespace) -> int:
    print_header("System information")
    print(f"Hostname: {platform.node()}")
    print(f"Kernel:   {platform.release()}")
    print(f"Machine:  {platform.machine()}")
    print(f"Python:   {platform.python_version()}")
    print(f"Root dir: {ROOT}")

    os_release = Path("/etc/os-release")
    if os_release.exists():
        values = {}
        for line in os_release.read_text().splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
        pretty = values.get("PRETTY_NAME")
        if pretty:
            print(f"OS:       {pretty}")

    return 0


def cmd_system_doctor(_: argparse.Namespace) -> int:
    print_header("System doctor")

    checks = []
    checks.append(("kvm device", Path("/dev/kvm").exists()))
    checks.append(("qemu-system-x86_64", shutil.which("qemu-system-x86_64") is not None))
    checks.append(("virsh", shutil.which("virsh") is not None))
    checks.append(("podman", shutil.which("podman") is not None))
    checks.append(("nekobox", shutil.which("nekobox") is not None or Path("/opt/nekobox/nekobox.AppImage").exists()))

    rc, stdout, _ = run(["systemctl", "is-active", "libvirtd"])
    checks.append(("libvirtd active", rc == 0 and stdout == "active"))

    for name, status in checks:
        mark = "ok" if status else "missing"
        print(f"[{mark}] {name}")

    missing = [name for name, status in checks if not status]
    if missing:
        print("\nSome components are missing or inactive.")
        return 1

    print("\nEverything required by the current doctor checks looks ready.")
    return 0


def cmd_profile_list(_: argparse.Namespace) -> int:
    print_header("Profiles")
    if not PROFILES_DIR.exists():
        print("profiles directory not found")
        return 1
    for item in sorted(PROFILES_DIR.glob("*.yaml")):
        print(item.stem)
    return 0


def cmd_profile_info(args: argparse.Namespace) -> int:
    path = PROFILES_DIR / f"{args.name}.yaml"
    if not path.exists():
        print(f"profile not found: {args.name}")
        return 1
    data = load_yaml(path)
    print_header(f"Profile: {args.name}")
    print(data.get("description") or data.get("summary") or "")
    print("\nPackages:")
    for item in data.get("packages", []):
        print(f"- {item}")
    print("\nModules:")
    for item in data.get("modules", []):
        print(f"- {item}")
    return 0


def cmd_profile_apply(args: argparse.Namespace) -> int:
    path = PROFILES_DIR / f"{args.name}.yaml"
    if not path.exists():
        print(f"profile not found: {args.name}")
        return 1
    require_root_for_mutation()
    data = load_yaml(path)
    packages = data.get("packages", [])
    modules = data.get("modules", [])
    if packages:
        print(f"Installing packages for profile {args.name}...")
        rc, _, stderr = run(["apt-get", "update"])
        if rc != 0:
            print(stderr)
            return rc
        rc, _, stderr = run(["apt-get", "install", "-y", *packages])
        if rc != 0:
            print(stderr)
            return rc
    current_modules = read_enabled_modules()
    write_enabled_modules(current_modules + modules)
    print(f"Applied profile: {args.name}")
    return 0


def cmd_module_list(_: argparse.Namespace) -> int:
    print_header("Modules")
    if not MODULES_DIR.exists():
        print("modules directory not found")
        return 1
    enabled = set(read_enabled_modules())
    for item in sorted(MODULES_DIR.iterdir()):
        if item.is_dir():
            suffix = " (enabled)" if item.name in enabled else ""
            print(f"{item.name}{suffix}")
    return 0


def cmd_module_info(args: argparse.Namespace) -> int:
    path = MODULES_DIR / args.name / "module.yaml"
    if not path.exists():
        print(f"module not found: {args.name}")
        return 1
    data = load_yaml(path)
    print_header(f"Module: {args.name}")
    print(data.get("description") or data.get("summary") or "")
    print("\nPackages:")
    for item in data.get("packages", []):
        print(f"- {item}")
    print("\nServices:")
    for item in data.get("services", []):
        print(f"- {item}")
    return 0


def cmd_module_enable(args: argparse.Namespace) -> int:
    path = MODULES_DIR / args.name / "module.yaml"
    if not path.exists():
        print(f"module not found: {args.name}")
        return 1
    require_root_for_mutation()
    data = load_yaml(path)
    packages = data.get("packages", [])
    services = data.get("services", [])
    if packages:
        print(f"Installing packages for module {args.name}...")
        rc, _, stderr = run(["apt-get", "update"])
        if rc != 0:
            print(stderr)
            return rc
        rc, _, stderr = run(["apt-get", "install", "-y", *packages])
        if rc != 0:
            print(stderr)
            return rc
    for service in services:
        run(["systemctl", "enable", service])
        run(["systemctl", "start", service])
    enabled = read_enabled_modules()
    write_enabled_modules(enabled + [args.name])
    print(f"Enabled module: {args.name}")
    return 0


def require_virsh() -> bool:
    if shutil.which("virsh") is None:
        print("virsh is not installed or not in PATH")
        return False
    return True


def cmd_vm_list(_: argparse.Namespace) -> int:
    if not require_virsh():
        return 1
    rc, stdout, stderr = run(["virsh", "list", "--all"])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_info(args: argparse.Namespace) -> int:
    if not require_virsh():
        return 1
    rc, stdout, stderr = run(["virsh", "dominfo", args.name])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_start(args: argparse.Namespace) -> int:
    if not require_virsh():
        return 1
    rc, stdout, stderr = run(["virsh", "start", args.name])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def cmd_vm_stop(args: argparse.Namespace) -> int:
    if not require_virsh():
        return 1
    rc, stdout, stderr = run(["virsh", "shutdown", args.name])
    if stdout:
        print(stdout)
    if rc != 0 and stderr:
        print(stderr)
    return rc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sanchosctl")
    subparsers = parser.add_subparsers(dest="group", required=True)

    system = subparsers.add_parser("system")
    system_sub = system.add_subparsers(dest="action", required=True)
    info = system_sub.add_parser("info")
    info.set_defaults(func=cmd_system_info)
    doctor = system_sub.add_parser("doctor")
    doctor.set_defaults(func=cmd_system_doctor)

    profile = subparsers.add_parser("profile")
    profile_sub = profile.add_subparsers(dest="action", required=True)
    profile_list = profile_sub.add_parser("list")
    profile_list.set_defaults(func=cmd_profile_list)
    profile_info = profile_sub.add_parser("info")
    profile_info.add_argument("name")
    profile_info.set_defaults(func=cmd_profile_info)
    profile_apply = profile_sub.add_parser("apply")
    profile_apply.add_argument("name")
    profile_apply.set_defaults(func=cmd_profile_apply)

    module = subparsers.add_parser("module")
    module_sub = module.add_subparsers(dest="action", required=True)
    module_list = module_sub.add_parser("list")
    module_list.set_defaults(func=cmd_module_list)
    module_info = module_sub.add_parser("info")
    module_info.add_argument("name")
    module_info.set_defaults(func=cmd_module_info)
    module_enable = module_sub.add_parser("enable")
    module_enable.add_argument("name")
    module_enable.set_defaults(func=cmd_module_enable)

    vm = subparsers.add_parser("vm")
    vm_sub = vm.add_subparsers(dest="action", required=True)
    vm_list = vm_sub.add_parser("list")
    vm_list.set_defaults(func=cmd_vm_list)
    vm_info = vm_sub.add_parser("info")
    vm_info.add_argument("name")
    vm_info.set_defaults(func=cmd_vm_info)
    vm_start = vm_sub.add_parser("start")
    vm_start.add_argument("name")
    vm_start.set_defaults(func=cmd_vm_start)
    vm_stop = vm_sub.add_parser("stop")
    vm_stop.add_argument("name")
    vm_stop.set_defaults(func=cmd_vm_stop)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
