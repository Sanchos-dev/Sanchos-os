#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("python3-yaml is required")
    sys.exit(1)

failed = False
for path in Path('.').rglob('*.yaml'):
    try:
        yaml.safe_load(path.read_text())
        print(f"ok  {path}")
    except Exception as exc:
        failed = True
        print(f"bad {path}: {exc}")

sys.exit(1 if failed else 0)
PY
