"""Step 1 - Explore the EODH STAC catalogue (public, no login needed).

Lists every collection with its spatial/temporal extent so we can decide which
datasets cover Nigeria and Kenya. Output: docs/catalogue_summary.csv
"""
import csv
import json
import requests

ROOT = "https://eodatahub.org.uk/api/catalogue/stac"

def get_all_collections():
    out, url = [], f"{ROOT}/collections?limit=200"
    while url:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        j = r.json()
        out += j["collections"]
        url = next((l["href"] for l in j.get("links", []) if l["rel"] == "next"), None)
    return out

def main():
    cols = get_all_collections()
    rows = []
    for c in cols:
        ext = c.get("extent", {})
        bbox = (ext.get("spatial", {}).get("bbox") or [[None]])[0]
        interval = (ext.get("temporal", {}).get("interval") or [[None, None]])[0]
        rows.append({
            "id": c["id"],
            "title": c.get("title", ""),
            "bbox": json.dumps(bbox),
            "start": interval[0],
            "end": interval[1],
            "parent": next((l["href"] for l in c["links"] if l["rel"] == "parent"), ""),
        })
    with open("docs/catalogue_summary.csv", "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f'{r["id"]:45s} {r["bbox"]:40s} {r["start"]} -> {r["end"]}')
    print(len(rows), "collections")

if __name__ == "__main__":
    main()

