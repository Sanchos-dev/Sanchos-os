#!/usr/bin/env python3
from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


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


def cmd_module_list(_: argparse.Namespace) -> int:
    print_header("Modules")
    if not MODULES_DIR.exists():
        print("modules directory not found")
        return 1
    for item in sorted(MODULES_DIR.iterdir()):
        if item.is_dir():
            print(item.name)
    return 0


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

    module = subparsers.add_parser("module")
    module_sub = module.add_subparsers(dest="action", required=True)
    module_list = module_sub.add_parser("list")
    module_list.set_defaults(func=cmd_module_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
