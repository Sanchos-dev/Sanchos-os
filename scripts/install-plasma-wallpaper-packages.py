#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

VALID_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.svg'}
PACKAGE_PREFIX = 'SanchosOs-'


def load_index(base: Path) -> dict:
    index = base / 'index.json'
    if index.exists():
        try:
            return json.loads(index.read_text())
        except Exception:
            pass
    collections: dict[str, list[str]] = {}
    for path in sorted(base.rglob('*')):
        if not path.is_file() or path.name == 'index.json':
            continue
        if path.suffix.lower() not in VALID_EXTS:
            continue
        rel = path.relative_to(base).as_posix()
        parts = rel.split('/')
        collection = parts[0] if len(parts) > 1 else 'default'
        collections.setdefault(collection, []).append(rel)
    default_item = 'default/sanchos-default.svg'
    for items in collections.values():
        if items:
            default_item = items[0]
            break
    return {'default': default_item, 'collections': collections}


def slugify(value: str) -> str:
    value = re.sub(r'[^A-Za-z0-9]+', '-', value).strip('-')
    return value or 'wallpaper'


def ensure_link(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    try:
        target.symlink_to(source)
    except Exception:
        shutil.copy2(source, target)


def write_metadata(target: Path, package_id: str, title: str) -> None:
    data = {
        'KPackageStructure': 'Plasma/Wallpaper',
        'KPlugin': {
            'Id': package_id,
            'License': 'CC-BY-SA-4.0',
            'Name': title,
            'Description': f'{title} wallpaper for sanchos-os',
            'Authors': [
                {
                    'Name': 'Sanchos',
                    'Email': 'sanchos@sanchos.su',
                }
            ],
        },
    }
    (target / 'metadata.json').write_text(json.dumps(data, indent=2) + '\n')


def install_packages(base: Path, output_root: Path) -> int:
    data = load_index(base)
    for entry in output_root.glob(f'{PACKAGE_PREFIX}*'):
        if entry.is_dir():
            shutil.rmtree(entry)

    count = 0
    for collection, items in data.get('collections', {}).items():
        for rel in items:
            source = base / rel
            if not source.exists():
                continue
            stem = Path(rel).stem
            ext = source.suffix.lower() or '.png'
            package_name = f'{PACKAGE_PREFIX}{slugify(collection)}-{slugify(stem)}'
            title = f'Sanchos {collection} / {stem}'
            target = output_root / package_name
            images_dir = target / 'contents' / 'images'
            filename = f'1920x1080{ext}'
            ensure_link(source, images_dir / filename)
            ensure_link(source, target / 'contents' / f'screenshot{ext}')
            write_metadata(target, package_name, title)
            count += 1
    return count


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print('usage: install-plasma-wallpaper-packages.py <source-dir> <output-dir>', file=sys.stderr)
        return 1
    source = Path(argv[1]).expanduser().resolve()
    output = Path(argv[2]).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    count = install_packages(source, output)
    print(f'Installed {count} Plasma wallpaper package(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
