---
participant_full_name: "Flawiya S. More"
email_address: "flavia.more.fm@gmail.com"
notebook_authors: [
    "Flawiya S. More"
]
notebook_title: "Multi-Scale Satellite Flood Early-Warning and Parametric Risk Trigger across Kenya and Nigeria"
coding_language_used: "Python"
makes_use_of_eodh_data: true
runs_on_eodh_jupyter_environment: true
data_sources_used: ["eocis-soil-moisture-africa", "clms-lcm-global-10m-yearly-v1-cog", "sentinel-2-c1-l2a"]
all_declarations_affirmed: true
---

# Submission

## Abstract (100 words)
Flood early-warning systems and parametric insurance triggers across Africa face a spatial scale mismatch: coarse hydrological models (0.25 degrees, roughly 28 km) capture daily catchment soil saturation but average out local floodplains and towns, causing basis risk. This notebook combines three open EODH datasets: EOCIS Soil Moisture Africa (26-year daily baseline, 2000-2026), Copernicus 10 m Land Cover (CLMS), and Sentinel-2 L2A (10 m MNDWI) across Kenya and Nigeria. We break down coarse cells by 10 m land cover exposure, map floodwater during the May 2024 Kenya flood disaster, and test trigger skill across 62 historical flood events.

## AI Disclosure: Describe how you used AI in authoring this notebook (100 words)
An AI coding assistant (Antigravity) was used to help with STAC API query syntax, Python data-cleaning script structure, and figure layout adjustments. The author independently conceived the multi-scale research question, selected the study areas (Kenya and Nigeria), designed the day-of-year rolling Z-score anomaly method, formulated the sub-pixel basis-risk analysis, verified all academic citations and DOIs, and wrote the hydrological and parametric insurance interpretations.

## References: Provide the URLs of any code sources that you used in authoring this notebook (optional)
- EODH Python Client (pyeodh): https://github.com/EO-DataHub/pyeodh
- EODH Documentation: https://docs.eodatahub.org.uk/
- geoBoundaries Open Administrative Boundaries: https://www.geoboundaries.org/
- Dartmouth Flood Observatory (DFO) Archive via HDX: https://data.humdata.org/dataset/global-active-archive-of-large-flood-events-dfo

## Commercial Data: Potential for Future Inclusion of Commercial Data: How could your notebook make use of the commercial datasets on the EODH and how would you adapt the notebook to do this? Not requiring commercial data is a valid response. (100 words)
Operational deployment of this three-stage workflow can integrate commercial EODH datasets through the same pyeodh STAC interface. When the open 0.25-degree EOCIS soil moisture Z-score crosses the +1.5 alert threshold over an exposed cell, the pipeline can query commercial Synthetic Aperture Radar (Airbus SAR, collection airbus_sar_data) to map floodwater through storm clouds, alongside high-resolution optical imagery (Airbus Pleiades Neo airbus_pneo_data and Planet SkySat SkySatCollect) to check building-level flood damage and verify insurance payouts.

## Declarations
By submitting this notebook:
- I/we agree to abide by the competition rules.
- I/we confirm this submission is my/our own original work.
- I/we grant the Earth Observation Data Hub a non-exclusive license to use, reproduce, modify, and display my/our work for promotional and educational purposes, including featuring it in the EODH Processes Catalogue and Documentation Site.
- I/we confirm that the code submitted may be published under the MIT license.
- I/we agree for the provided email address to be shared with the prize awarding organisations in the case that my/our notebook is a winning selection.

## Additional Notes (optional)

