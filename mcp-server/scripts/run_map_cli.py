from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from gis_automate.commands.map_command import run_map

shapefile = sys.argv[1]
fmt = sys.argv[2]
title = sys.argv[3] if sys.argv[3] else None
style = sys.argv[4] if sys.argv[4] else None
output = sys.argv[5] if sys.argv[5] else None

try:
    run_map(shapefile, fmt=fmt, title=title, style=style, output=output)
    print("done", flush=True)
finally:
    os._exit(0)
