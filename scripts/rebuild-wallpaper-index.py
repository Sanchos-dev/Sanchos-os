#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

VALID_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.svg'}
PREFERRED_COLLECTIONS = ['default', 'purple', 'fox']


def collect(base: Path) -> dict:
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

    ordered: dict[str, list[str]] = {}
    for name in PREFERRED_COLLECTIONS:
        ordered[name] = collections.pop(name, [])
    for name in sorted(collections):
        ordered[name] = collections[name]

    default_path = 'default/sanchos-default.svg'
    if ordered.get('default'):
        if default_path not in ordered['default']:
            default_path = ordered['default'][0]
    else:
        for items in ordered.values():
            if items:
                default_path = items[0]
                break

    return {
        'default': default_path,
        'collections': ordered,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: rebuild-wallpaper-index.py <wallpaper-dir>', file=sys.stderr)
        return 1
    base = Path(argv[1]).expanduser().resolve()
    if not base.exists():
        print(f'wallpaper directory not found: {base}', file=sys.stderr)
        return 1
    data = collect(base)
    target = base / 'index.json'
    target.write_text(json.dumps(data, indent=2) + '\n')
    print(f'Wrote wallpaper index: {target}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
