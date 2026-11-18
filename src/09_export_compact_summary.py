"""Export compact (<2 MB total) GitHub-ready summary datasets from the 26-year processed NetCDFs.

GitHub rejects files >100 MB. Instead of committing 560 MB of daily 3D grids, we export:
  1. data/summary/climatology_grids.nc   (~100 KB) : 2D spatial grids (mean annual rain, mean sm_top1m, valid_pct) for Nigeria & Kenya
  2. data/summary/daily_country_ts.csv   (~1.2 MB) : 26-year daily time series (rain_mm, sm_top1m, sm_z, rain_7d, rain_z7, frac_compound) for Nigeria, Kenya, and the Garissa focal cell
"""
import os
import numpy as np
import pandas as pd
import xarray as xr

os.makedirs("data/summary", exist_ok=True)

clim_vars = {}
ts_frames = []

for c in ["kenya", "nigeria"]:
    ds = xr.open_dataset(f"data/processed/{c}_clean.nc")
    yrs = ds.time.dt.year
    ann_rain = ds["rain_mm"].groupby(yrs).sum("time")
    ann_rain_mean = ann_rain.sel(year=ann_rain.year[(ann_rain.year >= 2001) & (ann_rain.year <= 2025)]).mean("year")
    sm_mean = ds["sm_top1m"].mean("time")
    valid_pct = ds["sm_top1m"].notnull().mean("time") * 100

    clim_ds = xr.Dataset({
        "mean_annual_rain_mm": ann_rain_mean.astype("float32"),
        "mean_sm_top1m_mm": sm_mean.astype("float32"),
        "valid_days_pct": valid_pct.astype("float32"),
    })
    clim_ds.to_netcdf(f"data/summary/{c}_climatology_grid.nc")

    valid_mask = ds["sm_top1m"].notnull().any("time")
    n_cells = int(valid_mask.sum())
    comp = ((ds["sm_z"] >= 1.0) & (ds["rain_z7"] >= 1.0)).where(valid_mask)
    frac_comp = (comp.sum(("lat", "lon")) / n_cells).to_series()

    mean_ts = ds[["rain_mm", "runoff_mm", "sm_top1m", "sm_z", "rain_7d", "rain_z7"]].mean(("lat", "lon")).to_dataframe()
    mean_ts["frac_compound"] = frac_comp
    mean_ts["region"] = c
    ts_frames.append(mean_ts.reset_index())

    if c == "kenya":
        gar = ds.sel(lon=slice(39.50, 39.75), lat=slice(-0.55, -0.30)).mean(("lat", "lon"))
        gar_ts = gar[["rain_mm", "runoff_mm", "sm_top1m", "sm_z", "rain_7d", "rain_z7"]].to_dataframe()
        gar_ts["frac_compound"] = np.nan
        gar_ts["region"] = "garissa_cell"
        ts_frames.append(gar_ts.reset_index())

df_all = pd.concat(ts_frames, ignore_index=True)
for col in ["rain_mm", "runoff_mm", "sm_top1m", "sm_z", "rain_7d", "rain_z7", "frac_compound"]:
    df_all[col] = df_all[col].round(4)

df_all.to_csv("data/summary/daily_timeseries_2000_2026.csv", index=False)

for fn in os.listdir("data/summary"):
    p = os.path.join("data/summary", fn)
    print(f"{fn:35s}: {os.path.getsize(p)/1024:.1f} KB")

