"""Step 6b - Build a simple flood-hazard trigger from soil moisture + rainfall and validate it against documented floods.

Daily indices (country level, computed from the cleaned grids):
  frac_compound : fraction of country cells where soil-moisture z >= SM_Z and 7-day-rain z >= RAIN_Z
  sm_z_mean     : country-mean soil-moisture z-score
  rain_z7_mean  : country-mean 7-day-rainfall z-score
Local index (events with a valid DFO centroid): same compound index at the nearest grid cell.

Validation (no tuning on the events):
  For every event window [start-PAD, end+PAD] take the maximum of the index. Compare it with the maximum of the
  SAME calendar window in every other year (2000-2025). `pct` = share of those reference windows that are lower
  than the event window (1.0 = the event window was wetter than all other years; 0.5 = no skill).
  Skill is summarised as the median pct and the share of events with pct >= 0.8.
Events: DFO (2000 - Apr 2019, objective) and curated recent events from docs/flood_events.csv (2019+, verify).
Outputs: docs/trigger_validation_events.csv, docs/trigger_validation_summary.csv, outputs/figures/06_*.png
"""
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SM_Z, RAIN_Z, PAD = 1.0, 1.0, 7
COUNTRIES = ["nigeria", "kenya"]
Y0, Y1 = 2000, 2025
DFO_END = pd.Timestamp("2019-04-18")


def load(c):
    return xr.open_dataset(f"data/processed/{c}_clean.nc").load()


def country_indices(ds):
    valid = ds["sm_top1m"].notnull().any("time")
    n = int(valid.sum())
    comp = ((ds.sm_z >= SM_Z) & (ds.rain_z7 >= RAIN_Z)).where(valid)
    out = pd.DataFrame({
        "frac_compound": (comp.sum(("lat", "lon")) / n).to_series(),
        "sm_z_mean": ds.sm_z.mean(("lat", "lon")).to_series(),
        "rain_z7_mean": ds.rain_z7.mean(("lat", "lon")).to_series(),
    })
    # exploratory longer-accumulation indices (country mean, de-seasonalised with a day-of-year z-score)
    out["rain_30d_z_mean"] = doy_z(ds["rain_30d"].mean(("lat", "lon")).to_series())
    out["runoff_14d_z_mean"] = doy_z(ds["runoff_mm"].mean(("lat", "lon")).to_series().rolling(14).mean())
    return out


def doy_z(s, window=15):
    """z-score of a daily series against the same day-of-year (+/- window) in the 2000-2025 baseline."""
    base = s.loc[f"{Y0}-01-01":f"{Y1}-12-31"]
    doy = base.index.dayofyear.values
    mu, sd = {}, {}
    for d in range(1, 367):
        diff = np.abs(((doy - d + 183) % 366) - 183)
        v = base.values[diff <= window]
        mu[d], sd[d] = np.nanmean(v), np.nanstd(v)
    m = s.index.dayofyear.map(mu).values.astype(float)
    sdv = s.index.dayofyear.map(sd).values.astype(float)
    return (s - m) / np.where(sdv > 1e-9, sdv, np.nan)


def local_series(ds, x, y):
    cell = ds.sel(lon=x, lat=y, method="nearest")
    return (cell.sm_z.clip(min=0) * cell.rain_z7.clip(min=0)).to_series(), float(cell.lon), float(cell.lat)


def window_pct(series, start, end):
    """pct of other-year reference windows lower than the event window maximum."""
    s0, s1 = start - pd.Timedelta(days=PAD), end + pd.Timedelta(days=PAD)
    ev = series.loc[s0:s1]
    if ev.dropna().empty:
        return np.nan, np.nan
    emax = ev.max()
    refs = []
    for y in range(Y0, Y1 + 1):
        k = y - start.year
        if k == 0:
            continue
        a, b = s0 + pd.DateOffset(years=k), s1 + pd.DateOffset(years=k)
        r = series.loc[a:b]
        if r.notnull().sum() >= 0.8 * len(ev):
            refs.append(r.max())
    if len(refs) < 10:
        return np.nan, emax
    refs = np.array(refs)
    return float((refs < emax).mean() + 0.5 * (refs == emax).mean()), float(emax)


def main():
    dfo = pd.read_csv("docs/dfo_events_nigeria_kenya.csv", parse_dates=["start", "end"])
    cur = pd.read_csv("docs/flood_events.csv", parse_dates=["start", "end"])
    # all curated events are kept: the DFO snapshot has almost no Nigerian events after 2009
    cur = cur[["country", "event", "start", "end"]].rename(columns={"event": "location"})
    cur["source"], cur["major"], cur["centroid"] = "curated (verify)", True, False
    dfo["source"] = "DFO"
    # centroids from the original shapefile (index aligned by sort order is unreliable -> re-read)
    import geopandas as gpd
    g = gpd.read_file("data/raw/dfo/wlf_nhr_fl_dfomasterlist_20190418.shp")
    g = g[g.Began >= "2000-01-01"]
    key = g[["Began", "Ended", "Country__c", "Centroid_X", "Centroid_Y"]]
    dfo = dfo.merge(key.rename(columns={"Began": "start", "Ended": "end", "Centroid_X": "x", "Centroid_Y": "y"})
                    .assign(primary_name=lambda d: d["Country__c"]).drop(columns="Country__c")
                    .drop_duplicates(["start", "end"]), on=["start", "end"], how="left")
    dfo["centroid"] = (dfo.x.abs() > 0.01) & (dfo.y.abs() > 0.01)
    res = []
    figs = {}
    for c in COUNTRIES:
        ds = load(c)
        idx = country_indices(ds)
        figs[c] = (ds, idx)
        ev = pd.concat([dfo[(dfo.country == c)], cur[cur.country == c]], ignore_index=True)
        for _, e in ev.iterrows():
            row = dict(country=c, source=e.source, start=e.start, end=e.end, location=str(e.location)[:60],
                       major=bool(e.major), dead=e.get("dead"), displaced=e.get("displaced"))
            for col in idx.columns:
                row[f"pct_{col}"], row[f"max_{col}"] = window_pct(idx[col], e.start, e.end)
            if e.centroid and not pd.isna(e.get("x", np.nan)):
                ser, lx, ly = local_series(ds, e.x, e.y)
                if ser.notnull().any():
                    row["pct_local_compound"], row["max_local_compound"] = window_pct(ser, e.start, e.end)
            res.append(row)
    R = pd.DataFrame(res)
    R.to_csv("docs/trigger_validation_events.csv", index=False)

    # summary ---------------------------------------------------------------------------------------
    summ = []
    pcols = [c for c in R.columns if c.startswith("pct_")]
    for c in COUNTRIES + ["both"]:
        sub = R if c == "both" else R[R.country == c]
        for grp, s2 in [("major events", sub[sub.major]), ("all events", sub)]:
            for p in pcols:
                v = s2[p].dropna()
                if len(v):
                    summ.append(dict(country=c, group=grp, index=p[4:], n=len(v), median_pct=v.median(),
                                     share_pct_ge_0_8=(v >= 0.8).mean(), share_pct_ge_0_5=(v >= 0.5).mean()))
    S = pd.DataFrame(summ)
    S.to_csv("docs/trigger_validation_summary.csv", index=False)
    print(S.round(2).to_string(index=False))

    # figures ---------------------------------------------------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, c in zip(axs, COUNTRIES):
        sub = R[R.country == c]
        for i, p in enumerate(["pct_frac_compound", "pct_sm_z_mean", "pct_rain_z7_mean", "pct_local_compound",
                               "pct_rain_30d_z_mean", "pct_runoff_14d_z_mean"]):
            if p not in sub:
                continue
            v = sub[sub[p].notnull()]
            ax.scatter(np.full(len(v), i) + np.random.default_rng(0).uniform(-.12, .12, len(v)), v[p],
                       c=np.where(v.major, "crimson", "grey"), s=36, alpha=.8)
            ax.hlines(v[p].median(), i - .3, i + .3, color="k")
        ax.axhline(0.5, ls="--", c="k", lw=.8)
        ax.set_xticks(range(6)); ax.set_xticklabels(["compound\n(area share)", "soil-moisture z\n(mean)",
                                                    "7-d rain z\n(mean)", "local compound\n(DFO centroid)",
                                                    "30-d rain z\n(exploratory)", "14-d runoff z\n(exploratory)"],
                                                   fontsize=8)
        ax.set_title(f"{c.title()}: event-window percentile vs same season in other years\n"
                     "(red = major event, grey = minor; black = median; dashed = no skill)")
        ax.set_ylabel("percentile (0.5 = no skill)")
    fig.tight_layout(); fig.savefig("outputs/figures/06_event_percentiles.png", dpi=150); plt.close(fig)

    cases = [("nigeria", "2022-06-01", "2022-10-31", "2022-05-01", "2022-12-15"),
             ("kenya", "2018-03-01", "2018-06-15", "2018-01-15", "2018-07-31"),
             ("nigeria", "2012-07-01", "2012-10-31", "2012-06-01", "2012-12-15"),
             ("kenya", "2020-03-01", "2020-06-30", "2020-02-01", "2020-07-31")]
    fig, axs = plt.subplots(len(cases), 1, figsize=(12, 3.1 * len(cases)), layout="constrained")
    for ax, (c, a, b, x0, x1) in zip(axs, cases):
        ds, idx = figs[c]
        d = idx.loc[x0:x1]
        ax.plot(d.index, d["frac_compound"] * 100, c="tab:blue", lw=1.5, label="% of country cells in compound trigger")
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color="orange", alpha=.28, label="Documented flood window")
        ax.set_ylim(0, max(float(d["frac_compound"].max() * 100) * 1.18, 25))
        ax.set_ylabel("% cells"); ax.set_title(f"{c.title()} ({a[:4]})", fontweight="bold")
        ax.grid(axis="y", ls=":", alpha=0.5)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=2, frameon=True, fontsize=10)
    fig.savefig("outputs/figures/07_case_studies.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()

