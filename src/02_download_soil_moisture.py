"""Step 2 - Download EOCIS Soil Moisture Africa (v2.3.1, daily) and crop to Nigeria and Kenya.

Source : EODH STAC collection `eocis-soil-moisture-africa` (files hosted on CEDA, open access).
Each daily file is ~2 MB for the whole of Africa, so we download one day at a time, crop it to the
study-area boxes, keep only the variables we need and delete the full-size file.
Output : data/interim/sm_<country>_<year>.nc  (one file per country per year, resumable)
Log    : docs/download_log.csv  (every day: status / http code - used in the pre-check step)

Usage  : python src/02_download_soil_moisture.py 2000 2026 [workers]
"""
import csv
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import requests
import xarray as xr

BASE = ("https://dap.ceda.ac.uk/neodc/eocis/data/global_and_regional/soil_moisture_africa/"
        "v2.3.1/daily/{y:04d}/{m:02d}/EOCIS-SM-L4-WB-AFRICA-TAMSAT-{y:04d}{m:02d}{d:02d}-fv2.3.1.nc")

# (lon_min, lon_max, lat_min, lat_max) - rough boxes around each country with a small margin
BOXES = {
    "nigeria": (2.5, 15.0, 3.9, 14.2),
    "kenya": (33.7, 42.2, -5.1, 5.7),
}
VARS = ["smc_avail_top", "smcl", "precip", "runoff", "fao_et0"]
OUT_DIR = "data/interim"
LOG = "docs/download_log.csv"


def fetch_day(day: date, session: requests.Session, retries: int = 4):
    url = BASE.format(y=day.year, m=day.month, d=day.day)
    last = None
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=120)
            if r.status_code == 404:
                return day, None, 404
            r.raise_for_status()
            fd, path = tempfile.mkstemp(suffix=".nc", dir="data/raw")
            with os.fdopen(fd, "wb") as f:
                f.write(r.content)
            try:
                with xr.open_dataset(path) as ds:
                    out = {}
                    for name, (x0, x1, y0, y1) in BOXES.items():
                        sub = ds[VARS].sel(lon=slice(x0, x1), lat=slice(y0, y1)).load()
                        out[name] = sub
            finally:
                try:
                    os.remove(path)
                except OSError:
                    pass
            return day, out, 200
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (attempt + 1))
    return day, None, f"ERR {last}"


def do_year(year: int, workers: int, end_limit: date):
    todo = [n for n in BOXES if not os.path.exists(f"{OUT_DIR}/sm_{n}_{year}.nc")]
    if not todo:
        print(year, "already done", flush=True)
        return []
    d0, d1 = date(year, 1, 1), min(date(year, 12, 31), end_limit)
    days = [d0 + timedelta(i) for i in range((d1 - d0).days + 1)]
    results, log = {n: [] for n in BOXES}, []
    with requests.Session() as s, ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(fetch_day, d, s) for d in days]
        for f in as_completed(futs):
            day, out, status = f.result()
            log.append((day.isoformat(), status))
            if out:
                for n in BOXES:
                    results[n].append(out[n])
    for n in BOXES:
        if results[n]:
            ds = xr.concat(sorted(results[n], key=lambda a: a.time.values[0]), dim="time")
            enc = {v: {"zlib": True, "complevel": 4} for v in ds.data_vars}
            ds.to_netcdf(f"{OUT_DIR}/sm_{n}_{year}.nc", encoding=enc)
    ok = sum(1 for _, st in log if st == 200)
    print(f"{year}: {ok}/{len(days)} days ok", flush=True)
    return sorted(log)


def main():
    y0, y1 = int(sys.argv[1]), int(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "status"])
        for y in range(y0, y1 + 1):
            for row in do_year(y, workers, date(2026, 1, 31)):
                w.writerow(row)
            f.flush()


if __name__ == "__main__":
    main()

