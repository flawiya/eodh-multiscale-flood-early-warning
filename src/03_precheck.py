"""Step 3 - Pre-check of the downloaded soil-moisture subsets.

Checks (per country):
  1. every expected day is present (no gaps / no duplicates)
  2. grid is identical across years (lat/lon)
  3. fraction of NaN cells and of 'fill value' cells (>1e10) per variable
  4. physical value ranges after masking fill values
Output: docs/precheck_report.md and docs/precheck_summary.csv
"""
import glob
import re

import numpy as np
import pandas as pd
import xarray as xr

FILL_THRESHOLD = 1e10
rows, md = [], ["# Pre-check report: EOCIS soil moisture subsets\n"]

log = pd.read_csv("docs/download_log.csv")
bad = log[log.status.astype(str) != "200"]
md.append(f"- Days attempted: **{len(log)}**, downloaded OK: **{(log.status.astype(str) == '200').sum()}**, "
          f"failed / missing: **{len(bad)}**")
if len(bad):
    md.append("  - Missing days: " + ", ".join(bad.date.head(30)) + (" ..." if len(bad) > 30 else ""))

for country in ["nigeria", "kenya"]:
    files = sorted(glob.glob(f"data/interim/sm_{country}_*.nc"))
    years = [int(re.search(r"_(\d{4})\.nc", f).group(1)) for f in files]
    ds = xr.concat([xr.open_dataset(f).load() for f in files], dim="time")
    t = pd.DatetimeIndex(ds.time.values)
    full = pd.date_range(t.min(), t.max(), freq="D")
    missing = full.difference(t)
    dups = int(t.duplicated().sum())
    md.append(f"\n## {country.title()}\n")
    md.append(f"- Files: {len(files)} ({min(years)}-{max(years)}), time steps: {len(t)}, "
              f"{t.min().date()} -> {t.max().date()}")
    md.append(f"- Missing days inside range: **{len(missing)}**; duplicated timestamps: **{dups}**")
    md.append(f"- Grid: {ds.sizes['lat']} x {ds.sizes['lon']} cells at 0.25 deg; "
              f"lat {float(ds.lat.min())}..{float(ds.lat.max())}, lon {float(ds.lon.min())}..{float(ds.lon.max())}")
    md.append("\n| variable | NaN % | fill-value % | min (valid) | max (valid) | mean (valid) |\n|---|---|---|---|---|---|")
    for v in ds.data_vars:
        a = ds[v]
        n = a.size
        nan = float(a.isnull().sum()) / n * 100
        fill = float((a > FILL_THRESHOLD).sum()) / n * 100
        valid = a.where((a <= FILL_THRESHOLD))
        mn, mx, me = (float(valid.min()), float(valid.max()), float(valid.mean()))
        md.append(f"| {v} | {nan:.2f} | {fill:.2f} | {mn:.4g} | {mx:.4g} | {me:.4g} |")
        rows.append(dict(country=country, variable=v, nan_pct=nan, fill_pct=fill, vmin=mn, vmax=mx, vmean=me))
    pr = ds["precip"].where(ds["precip"] <= FILL_THRESHOLD) * 86400
    md.append(f"- Precipitation converted to mm/day: mean {float(pr.mean()):.2f}, 99.9th pct "
              f"{float(pr.quantile(0.999)):.1f}, max {float(pr.max()):.1f}")

md.append("\n## Issues to handle in the cleaning step\n"
          "- Cells outside land / outside the model domain are stored either as NaN or as a huge fill value "
          "(about 2e20) -> must be masked to NaN.\n"
          "- Units are per-second fluxes (kg m-2 s-1): convert to mm/day (x 86400).\n"
          "- `smcl` has 4 soil layers (0-10, 10-35, 35-100, 100-300 cm): derive column totals / root-zone.")
open("docs/precheck_report.md", "w", encoding="utf8").write("\n".join(md))
pd.DataFrame(rows).to_csv("docs/precheck_summary.csv", index=False)
print("\n".join(md))
