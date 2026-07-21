from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from gis_automate.commands.web_command import run_web

shapefile = sys.argv[1]
title = sys.argv[2]
field = sys.argv[3] if sys.argv[3] else None
output = sys.argv[4] if sys.argv[4] else None

try:
    run_web(shapefile, title=title, field=field, output=output)
    print("done", flush=True)
finally:
    os._exit(0)
