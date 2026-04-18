from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NoReturn


def error(s: str) -> NoReturn:
    print(f"ERROR: {s}")
    sys.exit(2)


path = Path.home() / ".wtyt.json"
if not path.exists():
    error(f"missing config file at {path}")
with path.open() as file:
    data = json.load(file)


yamtrack_url = data.pop("yamtrack_url")
rustypaste_url = data.pop("rustypaste_url")


if data:
    error(f"found extra configuration key(s): {", ".join(data)}")
