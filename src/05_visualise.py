"""Step 5 - Exploratory visualisation of the cleaned data (zero legend/title overlap).

Figures written to outputs/figures/:
  01_study_area.png          study areas, ADM1 boundaries and 0.25-degree grid cells used
  02_mean_climate_maps.png   mean annual rainfall and mean top-1m soil moisture
  03_seasonal_cycle.png      monthly climatology (rain, soil moisture) per country
  04_timeseries_events.png   country-mean soil-moisture z-score and 7-day rain with documented flood windows
  05_data_quality.png        % valid days per cell (data coverage check)
"""
import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr

C = {"nigeria": "NGA", "kenya": "KEN"}
ds = {c: xr.open_dataset(f"data/processed/{c}_clean.nc") for c in C}
adm0 = {c: gpd.read_file(f"data/raw/boundaries/{i}_ADM0.geojson") for c, i in C.items()}
adm1 = {c: gpd.read_file(f"data/raw/boundaries/{i}_ADM1.geojson") for c, i in C.items()}
events = pd.read_csv("docs/flood_events.csv", parse_dates=["start", "end"])
OUT = "outputs/figures/"

# 01 study area (legend placed cleanly below the maps, never over the coastline) --------------
fig, axs = plt.subplots(1, 2, figsize=(13, 6.2), layout="constrained")
for ax, c in zip(axs, C):
    adm1[c].boundary.plot(ax=ax, lw=0.5, color="grey", label="ADM1 boundary")
    adm0[c].boundary.plot(ax=ax, lw=1.5, color="k", label="National border (ADM0)")
    cells = ds[c]["sm_top1m"].notnull().any("time")
    ys, xs = cells.values.nonzero()
    ax.scatter(cells.lon.values[xs], cells.lat.values[ys], s=7, c="tab:blue",
               label="0.25° EOCIS grid cell centre")
    ax.set_title(f"{c.title()}: {int(cells.sum())} model cells, {len(adm1[c])} ADM1 units",
                 fontweight="bold", pad=8)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.margins(0.06)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="outside lower center", ncol=3, frameon=True, fontsize=9.5)
fig.suptitle("Study Areas and EOCIS 0.25° Soil-Moisture Grid (geoBoundaries ADM1)",
             fontsize=13, fontweight="bold")
fig.savefig(OUT + "01_study_area.png", dpi=150)
plt.close(fig)

# 02 climate maps (constrained layout prevents title/colorbar collision) ----------------------
fig, axs = plt.subplots(2, 2, figsize=(13, 10.5), layout="constrained")
for j, c in enumerate(C):
    d = ds[c]
    yrs = d.time.dt.year
    ann = d["rain_mm"].groupby(yrs).sum("time")
    ann = ann.sel(year=ann.year[(ann.year >= 2001) & (ann.year <= 2025)]).mean("year")
    ann.where(ann > 0).plot(ax=axs[0, j], cmap="Blues", cbar_kwargs={"label": "mm / year", "shrink": 0.88})
    d["sm_top1m"].mean("time").plot(ax=axs[1, j], cmap="YlGnBu", cbar_kwargs={"label": "mm (kg m$^{-2}$)", "shrink": 0.88})
    axs[0, j].set_title(f"{c.title()}: Mean Annual Rainfall (2001–2025)", fontweight="bold", fontsize=11, pad=8)
    axs[1, j].set_title(f"{c.title()}: Mean Top-1m Soil Moisture (JULES)", fontweight="bold", fontsize=11, pad=8)
    for i in (0, 1):
        adm0[c].boundary.plot(ax=axs[i, j], color="k", lw=1)
        axs[i, j].set_xlabel("Longitude (°E)")
        axs[i, j].set_ylabel("Latitude (°N)")
fig.suptitle("25-Year Hydrological Climatology from EOCIS (0.25°)", fontsize=13, fontweight="bold")
fig.savefig(OUT + "02_mean_climate_maps.png", dpi=150)
plt.close(fig)

# 03 seasonal cycle (shared legend placed outside below subplots + extra y headroom) ----------
fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), layout="constrained")
for ax, c in zip(axs, C):
    d = ds[c]
    mon = d[["rain_mm", "sm_top1m"]].mean(("lat", "lon"))
    rain = mon["rain_mm"].groupby("time.month").mean() * 30.4
    sm = mon["sm_top1m"].groupby("time.month").mean()
    ax.bar(rain.month, rain, color="tab:blue", alpha=0.62, label="Monthly rainfall (mm/month)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Rainfall (mm/month)", color="tab:blue", fontweight="bold")
    ax.set_ylim(0, float(rain.max()) * 1.18)
    ax2 = ax.twinx()
    ax2.plot(sm.month, sm, "o-", color="tab:brown", lw=2, label="Top-1m soil moisture (mm)")
    ax2.set_ylabel("Soil moisture (mm)", color="tab:brown", fontweight="bold")
    sm_span = float(sm.max() - sm.min())
    ax2.set_ylim(float(sm.min()) - 0.1 * sm_span, float(sm.max()) + 0.18 * sm_span)
    ax.set_title(f"{c.title()}: Seasonal Hydrological Cycle (Country Mean)", fontweight="bold", pad=8)
    ax.set_xticks(range(1, 13))
    ax.grid(axis="y", ls=":", alpha=0.5)
h1, l1 = axs[0].get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
fig.legend(h1 + h2, l1 + l2, loc="outside lower center", ncol=2, frameon=True, fontsize=10)
fig.savefig(OUT + "03_seasonal_cycle.png", dpi=150)
plt.close(fig)

# 04 time series + events (legend placed outside at bottom) -----------------------------------
fig, axs = plt.subplots(2, 2, figsize=(15, 7.2), sharex="col", layout="constrained")
for j, c in enumerate(C):
    d = ds[c][["sm_z", "rain_7d"]].mean(("lat", "lon")).to_dataframe()
    ev = events[events.country == c]
    axs[0, j].plot(d.index, d["sm_z"], lw=0.7, color="tab:brown", label="Soil-moisture Z-score")
    axs[0, j].axhline(0, color="k", lw=0.5)
    axs[0, j].axhline(1.5, color="r", ls="--", lw=0.9, label="Saturation threshold (Z = +1.5)")
    axs[0, j].set_ylabel("Soil-moisture Z-score")
    axs[1, j].plot(d.index, d["rain_7d"], lw=0.7, color="tab:blue", label="7-day rainfall (mm)")
    axs[1, j].set_ylabel("7-day rainfall (mm)")
    for k_ax, ax in enumerate(axs[:, j]):
        for idx_ev, (_, r) in enumerate(ev.iterrows()):
            lbl = "Documented flood window" if (k_ax == 0 and idx_ev == 0) else None
            ax.axvspan(r.start, r.end, color="orange", alpha=0.3, label=lbl)
    axs[0, j].set_title(f"{c.title()} (Country Mean, 2000–2026)", fontweight="bold", pad=8)
h_top, l_top = axs[0, 0].get_legend_handles_labels()
h_bot, l_bot = axs[1, 0].get_legend_handles_labels()
fig.legend(h_top + h_bot, l_top + l_bot, loc="outside lower center", ncol=4, frameon=True, fontsize=9.5)
fig.savefig(OUT + "04_timeseries_events.png", dpi=150)
plt.close(fig)

# 05 data quality -----------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(13, 5.5), layout="constrained")
for ax, c in zip(axs, C):
    q = ds[c]["sm_top1m"].notnull().mean("time") * 100
    q.plot(ax=ax, cmap="viridis", vmin=0, vmax=100, cbar_kwargs={"label": "% days with valid data", "shrink": 0.88})
    adm0[c].boundary.plot(ax=ax, color="k", lw=1)
    ax.set_title(f"{c.title()}: Valid-Data Coverage per Cell (2000–2026)", fontweight="bold", pad=8)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
fig.savefig(OUT + "05_data_quality.png", dpi=150)
plt.close(fig)
print("05_visualise figures regenerated cleanly.")
