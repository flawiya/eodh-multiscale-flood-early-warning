"""Step 4 - Clean and prepare the soil-moisture data.

Cleaning
  * mask fill values (~2e20) and non-land cells -> NaN
  * convert fluxes from kg m-2 s-1 to mm/day (x 86400)
  * keep only cells whose centre is inside the country polygon (geoBoundaries ADM0)
Derived variables (all per grid cell, daily)
  * sm_top1m      : soil moisture of top 1 m (kg m-2 = mm) = sum of the first 3 JULES layers (0.1+0.25+0.65 m)
  * sm_pct        : percentile rank of sm_top1m against the same day-of-year (+/-7 days) 2000-2025 baseline
  * sm_z          : standardised anomaly (z-score) of sm_top1m against the same day-of-year baseline
  * rain_3d/7d/30d: rolling rainfall sums (mm)
  * rain_z7       : z-score of 7-day rainfall against same-season baseline
Outputs
  data/processed/<country>_clean.nc     (gridded, analysis-ready)
  data/processed/<country>_adm1_daily.csv (ADM1-mean daily time series of the key variables)
"""
import glob
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio.features
import xarray as xr
from affine import Affine

FILL = 1e10
ISO = {"nigeria": "NGA", "kenya": "KEN"}
BASE_START, BASE_END = "2000-01-01", "2025-12-31"
LAYER_THICK = np.array([0.1, 0.25, 0.65, 2.0])  # m, JULES 4-layer soil (documented in product metadata)


def country_mask(ds, iso):
    adm0 = gpd.read_file(f"data/raw/boundaries/{iso}_ADM0.geojson").to_crs(4326)
    lat, lon = ds.lat.values, ds.lon.values
    res = 0.25
    # raster transform with rows ordered as in ds (lat ascending -> flip for rasterize)
    transform = Affine(res, 0, lon.min() - res / 2, 0, -res, lat.max() + res / 2)
    m = rasterio.features.rasterize(
        [(g, 1) for g in adm0.geometry], out_shape=(len(lat), len(lon)),
        transform=transform, fill=0, all_touched=False, dtype="uint8")
    m = m[::-1, :]  # flip so that index 0 = lowest latitude
    return xr.DataArray(m.astype(bool), coords={"lat": ds.lat, "lon": ds.lon}, dims=("lat", "lon"))


def doy_baseline_stats(da, window=7):
    """mean / std / for each day-of-year using a +/- window-day pool over the baseline period."""
    base = da.sel(time=slice(BASE_START, BASE_END))
    doy = base.time.dt.dayofyear
    mean = []
    std = []
    for d in range(1, 367):
        dd = np.abs(((doy - d + 183) % 366) - 183)
        sel = base.where(dd <= window, drop=True)
        mean.append(sel.mean("time"))
        std.append(sel.std("time"))
    mean = xr.concat(mean, dim="dayofyear").assign_coords(dayofyear=np.arange(1, 367))
    std = xr.concat(std, dim="dayofyear").assign_coords(dayofyear=np.arange(1, 367))
    return mean, std


def zscore(da, mean, std):
    doy = da.time.dt.dayofyear
    return (da - mean.sel(dayofyear=doy)) / std.sel(dayofyear=doy).where(lambda s: s > 1e-6)


def prepare(country):
    iso = ISO[country]
    files = sorted(glob.glob(f"data/interim/sm_{country}_*.nc"))
    ds = xr.concat([xr.open_dataset(f).load() for f in files], dim="time")
    ds = ds.sortby("time")
    n_before = int(ds.time.size)
    ds = ds.isel(time=np.unique(ds.time.values, return_index=True)[1])  # drop duplicate days if any

    # --- cleaning -------------------------------------------------------------------------
    for v in ds.data_vars:
        ds[v] = ds[v].where(ds[v] <= FILL)
    inside = country_mask(ds, iso)
    ds = ds.where(inside)
    land = ds["smc_avail_top"].notnull().any("time")  # cells that actually have model output
    ds = ds.where(land)

    out = xr.Dataset(coords=ds.coords)
    out["rain_mm"] = ds["precip"] * 86400
    out["runoff_mm"] = ds["runoff"] * 86400
    out["et0_mm"] = ds["fao_et0"] * 86400
    out["sm_top1m"] = ds["smcl"].isel(soil=slice(0, 3)).sum("soil", skipna=False)
    out["sm_total"] = ds["smcl"].sum("soil", skipna=False)
    out["sm_avail_top1m"] = ds["smc_avail_top"]

    # --- derived --------------------------------------------------------------------------
    m, s = doy_baseline_stats(out["sm_top1m"])
    out["sm_z"] = zscore(out["sm_top1m"], m, s)
    for w in (3, 7, 30):
        out[f"rain_{w}d"] = out["rain_mm"].rolling(time=w, min_periods=w).sum()
    r7 = out["rain_7d"]
    m7, s7 = doy_baseline_stats(r7)
    out["rain_z7"] = zscore(r7, m7, s7)
    out["compound"] = (out["sm_z"].clip(min=0) * out["rain_z7"].clip(min=0))  # simple wet-soil x heavy-rain index

    out.attrs.update(title=f"Cleaned EOCIS soil moisture subset, {country}",
                     source="EOCIS Soil Moisture Africa v2.3.1 via EODH (TAMSAT/JULES)",
                     baseline=f"{BASE_START}..{BASE_END}", units_note="rain/runoff/et0 in mm/day; sm in kg m-2 (= mm)")
    enc = {v: {"zlib": True, "complevel": 4, "dtype": "float32"} for v in out.data_vars}
    out.to_netcdf(f"data/processed/{country}_clean.nc", encoding=enc)

    # --- ADM1 daily means -----------------------------------------------------------------
    adm1 = gpd.read_file(f"data/raw/boundaries/{iso}_ADM1.geojson").to_crs(4326)
    name_col = "shapeName"
    frames = []
    lat, lon = out.lat.values, out.lon.values
    res = 0.25
    transform = Affine(res, 0, lon.min() - res / 2, 0, -res, lat.max() + res / 2)
    for _, row in adm1.iterrows():
        m_ = rasterio.features.rasterize([(row.geometry, 1)], out_shape=(len(lat), len(lon)),
                                         transform=transform, fill=0, all_touched=True, dtype="uint8")[::-1, :]
        mk = xr.DataArray(m_.astype(bool), coords={"lat": out.lat, "lon": out.lon}, dims=("lat", "lon"))
        if int(mk.sum()) == 0:
            continue
        sub = out[["rain_mm", "runoff_mm", "sm_top1m", "sm_z", "rain_7d", "rain_z7", "compound"]].where(mk).mean(("lat", "lon"))
        df = sub.to_dataframe().reset_index()
        df["adm1"] = row[name_col]
        df["n_cells"] = int(mk.sum())
        frames.append(df)
    pd.concat(frames).to_csv(f"data/processed/{country}_adm1_daily.csv", index=False)

    valid = float(out["sm_top1m"].notnull().mean() * 100)
    print(f"{country}: {n_before} days, {int(land.sum())} land cells in country, "
          f"{valid:.1f}% valid sm cells, ADM1 units: {len(frames)}", flush=True)


if __name__ == "__main__":
    for c in (sys.argv[1:] or ["nigeria", "kenya"]):
        prepare(c)
