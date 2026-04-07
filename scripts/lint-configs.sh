#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys
import yaml

root = Path('.')
paths = list(root.glob('profiles/*.yaml')) + list(root.glob('modules/*/module.yaml'))
errors = []
for path in paths:
    try:
        with path.open() as fh:
            yaml.safe_load(fh)
    except Exception as exc:
        errors.append(f"{path}: {exc}")

if errors:
    for line in errors:
        print(line, file=sys.stderr)
    sys.exit(1)

print(f"validated {len(paths)} yaml files")
PY
