"""Step 6a - Build the validation event table from the Dartmouth Flood Observatory (DFO) master list.

Source: DFO Global Active Archive of Large Flood Events (via HDX, CC BY, snapshot 2019-04-18, covers 1985-2019).
We keep events that mention Nigeria or Kenya from 2000 onwards and classify them as:
  major  : severity >= 1.5  OR  deaths >= 50  OR  displaced >= 50,000
  minor  : everything else
Events after Apr 2019 are not in this snapshot - they come from docs/flood_events.csv (verify manually).
Output: docs/dfo_events_nigeria_kenya.csv
"""
import geopandas as gpd
import pandas as pd

g = gpd.read_file("data/raw/dfo/wlf_nhr_fl_dfomasterlist_20190418.shp")
txt = g[["Country__c", "Other", "Nations"]].apply(lambda s: s.fillna(""))
rows = []
for iso, name in [("nigeria", "Nigeria"), ("kenya", "Kenya")]:
    m = txt.apply(lambda s: s.str.contains(name, case=False)).any(axis=1) & (g.Began >= "2000-01-01")
    d = g[m].copy()
    # keep events where the country is the primary country, or listed second (shared events)
    d["country"] = iso
    d["primary"] = d["Country__c"].fillna("").str.contains(name, case=False)
    rows.append(d)
ev = pd.concat(rows)
ev = ev.rename(columns={"Began": "start", "Ended": "end", "Dead": "dead", "Displaced": "displaced",
                        "Severity__": "severity", "Main_cause": "main_cause", "Detailed_L": "location",
                        "Rivers": "rivers", "Affected_s": "area_km2"})
ev["major"] = (ev.severity >= 1.5) | (ev.dead >= 50) | (ev.displaced >= 50000)
keep = ["country", "primary", "start", "end", "dead", "displaced", "severity", "area_km2", "main_cause",
        "location", "rivers", "major"]
ev = ev[keep].sort_values(["country", "start"])
ev.to_csv("docs/dfo_events_nigeria_kenya.csv", index=False)
print(ev.groupby("country").agg(events=("start", "size"), major=("major", "sum")))

