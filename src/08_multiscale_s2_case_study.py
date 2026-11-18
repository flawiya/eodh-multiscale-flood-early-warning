"""Step 08 (Refined, Zero Legend Overlap) - Multi-scale verification: 0.25-deg EOCIS vs 10-m Sentinel-2 MNDWI.

Places legends outside the time-series curve and outside the satellite image canvas so zero data pixels are covered.
Generates:
  outputs/figures/08_multiscale_s2_validation.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
import xarray as xr
import pandas as pd
import pystac_client

OUT_FIG = "outputs/figures/08_multiscale_s2_validation.png"
LON_MIN, LON_MAX = 39.50, 39.75
LAT_MIN, LAT_MAX = -0.55, -0.30

ds = xr.open_dataset("data/processed/kenya_clean.nc")
cell = ds.sel(lon=slice(LON_MIN, LON_MAX), lat=slice(LAT_MIN, LAT_MAX)).mean(("lat", "lon"))
df_time = cell[["sm_z", "rain_mm", "rain_7d", "sm_top1m"]].sel(time=slice("2024-01-01", "2024-07-31")).to_dataframe()

cat = pystac_client.Client.open("https://eodatahub.org.uk/api/catalogue/stac/catalogs/public/catalogs/element84")
it_dry = cat.get_collection("sentinel-2-c1-l2a").get_item("S2A_T37MEV_20240310T074424_L2A")
it_flood = cat.get_collection("sentinel-2-c1-l2a").get_item("S2A_T37MEV_20240519T074617_L2A")

def read_multispectral(item, bounds_4326):
    with rasterio.open(item.assets["visual"].href) as src_vis:
        b_utm = transform_bounds("EPSG:4326", src_vis.crs, *bounds_4326)
        win = from_bounds(*b_utm, src_vis.transform)
        rgb = src_vis.read(window=win)
        rgb = np.clip(rgb.transpose(1, 2, 0) / 255.0, 0, 1)

    with rasterio.open(item.assets["green"].href) as src_g:
        green = src_g.read(1, window=win).astype(float)
    with rasterio.open(item.assets["swir16"].href) as src_swir:
        win_swir = from_bounds(*b_utm, src_swir.transform)
        swir = src_swir.read(1, window=win_swir, out_shape=green.shape).astype(float)

    denom = green + swir
    mndwi = np.where(denom > 0, (green - swir) / denom, -1.0)
    return rgb, mndwi

rgb_dry, mndwi_dry = read_multispectral(it_dry, (LON_MIN, LAT_MIN, LON_MAX, LAT_MAX))
rgb_flood, mndwi_flood = read_multispectral(it_flood, (LON_MIN, LAT_MIN, LON_MAX, LAT_MAX))

water_dry = (mndwi_dry > 0.0)
water_flood = (mndwi_flood > -0.05)
new_inundation = water_flood & (~water_dry)

new_flood_pixels = int(np.sum(new_inundation))
total_water_pixels = int(np.sum(water_flood))
total_pixels = water_flood.size
inundation_area_km2 = (new_flood_pixels * 100) / 1e6
total_water_km2 = (total_water_pixels * 100) / 1e6
cell_area_km2 = (total_pixels * 100) / 1e6

fig = plt.figure(figsize=(16, 12.6))
gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 1.45], hspace=0.38, wspace=0.18)

# Panel A: Time series with legend placed cleanly OUTSIDE above/below the plot lines
ax_ts = fig.add_subplot(gs[0, :])
ax_ts_rain = ax_ts.twinx()

ax_ts_rain.bar(df_time.index, df_time["rain_mm"], width=1.0, color="#6baed6", alpha=0.55, label="Daily Rainfall (mm)")
ax_ts.plot(df_time.index, df_time["sm_z"], color="#b15928", lw=2.2, label="Soil Moisture Z-Score (EOCIS 0.25°)")
ax_ts.axhline(0, color="gray", lw=0.8, ls="--")
ax_ts.axhline(1.5, color="red", lw=1.2, ls=":", label="Catchment Saturation Trigger (Z = +1.5)")

ax_ts.axvline(pd.Timestamp("2024-03-10"), color="green", lw=1.9, ls="-", label="S2 Baseline Scene (10 Mar 2024)")
ax_ts.axvline(pd.Timestamp("2024-05-19"), color="blue", lw=2.0, ls="-", label="S2 Flood Peak Scene (19 May 2024)")
ax_ts.axvspan(pd.Timestamp("2024-04-15"), pd.Timestamp("2024-05-31"), color="orange", alpha=0.22, label="Kenya Flood Emergency Window")

ax_ts.set_ylim(-0.15, 2.35)
ax_ts_rain.set_ylim(0, 42)
ax_ts.set_ylabel("Soil Moisture Z-score", fontsize=11, fontweight="bold", color="#b15928")
ax_ts_rain.set_ylabel("Daily Rainfall (mm/day)", fontsize=11, fontweight="bold", color="#3182bd")
ax_ts.set_title("A. Regional Catchment Early Warning Signal: EOCIS 0.25° Daily Soil Moisture & Rainfall (Tana River / Garissa, 2024)",
                 fontsize=12.5, fontweight="bold", pad=48)

lines1, labels1 = ax_ts.get_legend_handles_labels()
lines2, labels2 = ax_ts_rain.get_legend_handles_labels()
ax_ts.legend(lines1 + lines2, labels1 + labels2, loc="lower center", bbox_to_anchor=(0.5, 1.01),
             frameon=True, fontsize=9, ncol=3)

# Panel B: Dry baseline Sentinel-2 true color
ax_b = fig.add_subplot(gs[1, 0])
ax_b.imshow(rgb_dry)
ax_b.set_title("B. Dry Season Baseline (10 m)\nSentinel-2 True Color (10 March 2024)", fontsize=11, fontweight="bold", pad=8)
ax_b.set_xticks([])
ax_b.set_yticks([])

# Panel C: Flood peak Sentinel-2 true color
ax_c = fig.add_subplot(gs[1, 1])
ax_c.imshow(rgb_flood)
ax_c.set_title("C. Peak Flood Inundation (10 m)\nSentinel-2 True Color (19 May 2024)", fontsize=11, fontweight="bold", pad=8)
ax_c.set_xticks([])
ax_c.set_yticks([])

# Panel D: Sub-pixel flood extent with legend placed OUTSIDE below Panel D (never covering the river!)
ax_d = fig.add_subplot(gs[1, 2])
ax_d.imshow(rgb_flood, alpha=0.55)

flood_overlay = np.zeros((*water_flood.shape, 4))
flood_overlay[water_dry] = [0.0, 0.2, 0.8, 0.9]
flood_overlay[new_inundation] = [0.0, 0.85, 1.0, 0.95]
ax_d.imshow(flood_overlay)

h, w = water_flood.shape
rect = Rectangle((2, 2), w - 4, h - 4, linewidth=3.5, edgecolor="crimson", facecolor="none", linestyle="--")
ax_d.add_patch(rect)

custom_legend = [
    Patch(facecolor=[0.0, 0.85, 1.0], edgecolor="k", label=f"Submerged Floodplain: {inundation_area_km2:.1f} km²"),
    Patch(facecolor=[0.0, 0.2, 0.8], edgecolor="k", label="Permanent River Channel"),
    Patch(facecolor="none", edgecolor="crimson", linestyle="--", label="0.25° Catchment Cell (~770 km²)")
]
ax_d.legend(handles=custom_legend, loc="upper center", bbox_to_anchor=(0.5, -0.02),
            frameon=True, fontsize=9, ncol=1)

ax_d.set_title(f"D. Sub-Pixel Inundation Footprint (MNDWI, 10 m)\nFlooded River Corridor: {total_water_km2:.1f} km² ({total_water_km2/cell_area_km2*100:.1f}% of Cell)",
               fontsize=11, fontweight="bold", pad=8)
ax_d.set_xticks([])
ax_d.set_yticks([])

fig.suptitle("Multi-Scale Hydrological Verification: Connecting Regional Macro-Sponge (0.25°) with Local Surface Inundation (10 m)",
             fontsize=14.5, fontweight="bold", y=0.98)

os.makedirs("outputs/figures", exist_ok=True)
fig.savefig(OUT_FIG, dpi=160, bbox_inches="tight")
plt.close(fig)
print(f"Successfully generated: {OUT_FIG}")
