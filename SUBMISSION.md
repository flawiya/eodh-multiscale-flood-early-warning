# EODH Community Notebook Competition Submission Form

## 1. Author Details
- **Author Name:** Flawiya S. More
- **Location:** Liverpool, United Kingdom
- **Affiliation / Background:** MSc Geographic Data Science (University of Liverpool) | Environmental Data Scientist
- **Repository License:** MIT Open-Source License

## 2. Notebook Title
**Multi-Scale Satellite Flood Early-Warning & Parametric Risk Trigger: Synergising Daily Macro-Hydrology (EOCIS 0.25°) with High-Resolution Asset Exposure (CLMS 10 m) and Inundation (Sentinel-2 10 m) across Kenya and Nigeria**

## 3. EODH Datasets Used
1. **EOCIS Soil Moisture Africa v2.3.1** (`eocis-soil-moisture-africa`, CEDA STAC): 26-year daily soil moisture and precipitation baseline (2000–2026).
2. **Copernicus Land Monitoring Service (CLMS) Global 10 m Land Cover** (`clms-lcm-global-10m-yearly-v1-cog`, CEDA STAC): High-resolution asset exposure profiling.
3. **Sentinel-2 Collection 1 Level-2A** (`sentinel-2-c1-l2a`, Element84 STAC): 10-meter multispectral surface reflectance for MNDWI flood extent verification.

## 4. External Open Datasets Integrated
- **geoBoundaries (Open License):** Administrative boundaries (ADM0, ADM1, ADM2) for Nigeria and Kenya.
- **Dartmouth Flood Observatory (DFO, CC-BY):** Historical flood disaster catalog (62 documented events) for empirical trigger benchmarking.

## 5. Summary of Methodology & Innovation
This notebook resolves the spatial scale gap between coarse macro-hydrological models ($0.25^\circ \approx 28\text{ km}$) and localized flood impacts ($10\text{ m}$):
- Computes a 26-year rolling day-of-year climatology and standardized $Z$-score anomaly for top-1m soil moisture and 7-day precipitation.
- Uses CLMS 10 m Land Cover to deconstruct coarse pixels, proving that $>67\%$ of a typical semi-arid riverine pixel is uninhabited shrubland while $<1.5\%$ is critical urban and agricultural land—directly addressing basis risk in parametric underwriting.
- Streams Sentinel-2 10 m bands via STAC to verify sub-pixel floodplain inundation during the May 2024 Kenya flood emergency using MNDWI.
- Benchmarks trigger performance across 62 historical flood events, contrasting localized saturation-excess catchments (Kenya, high skill: median percentile $0.72–0.80$) against transboundary fluvial river systems (Nigeria, driven by upstream routing and dam releases).

## 6. Future Commercial Data Integration Potential
While this workflow relies strictly on open data for reproducibility, operational deployment can incorporate commercial datasets available on the EODH platform:
- **Airbus Radar / SAR (`airbus_sar_data`):** High-resolution X-band/C-band commercial SAR to penetrate cloud cover during peak monsoon storms for real-time sub-meter urban flood depth extraction.
- **PlanetScope (`PSScene`) & SkySat (`SkySatCollect`) & Airbus Pleiades Neo (`airbus_pneo_data`):** Daily 0.3 m – 3 m optical tasking over critical infrastructure (bridges, dams, insured commercial properties) immediately after the EOCIS $0.25^\circ$ soil saturation index crosses the $Z \ge +1.5$ threshold.

## 7. AI-Use Disclosure
In accordance with the competition guidelines, the author declares the following use of AI tools:
- **AI Tool Used:** Antigravity AI coding assistant.
- **Scope of Assistance:** Assisted with STAC API query syntax, data download/cleaning script scaffolding, and Matplotlib multi-panel layout formatting.
- **Author Responsibility:** The research design, selection of study areas, hydrological anomaly formulation, sub-pixel basis risk analysis, verification of academic literature, and interpretation of all outputs were directed and validated by the author.

## 8. Reproducibility & Agreements
- [x] Uses EODH catalogue datasets.
- [x] Compatible with the EODH JupyterLab environment (`requirements.txt` provided).
- [x] Uses exclusively open datasets for full reproducibility.
- [x] Submitted under an open-source license (MIT).
- [x] Author agrees to share contact email with prize-awarding organizations and permits EODH to feature the notebook as a community resource with author attribution.

