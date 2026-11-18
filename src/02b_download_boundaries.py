"""Step 2b - Download open admin boundaries (geoBoundaries gbOpen) for Nigeria (NGA) and Kenya (KEN).

ADM1 = states / counties, ADM2 = LGAs / sub-counties. Saved in data/raw/boundaries/.
"""
import os

import requests

os.makedirs("data/raw/boundaries", exist_ok=True)
for iso in ["NGA", "KEN"]:
    for lvl in ["ADM0", "ADM1", "ADM2"]:
        meta = requests.get(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/{lvl}/", timeout=60).json()
        url = meta["gjDownloadURL"]
        out = f"data/raw/boundaries/{iso}_{lvl}.geojson"
        r = requests.get(url, timeout=300)
        r.raise_for_status()
        open(out, "wb").write(r.content)
        print(iso, lvl, meta.get("boundaryYearRepresented"), meta.get("boundaryLicense"), f"{len(r.content)/1e6:.1f} MB")

