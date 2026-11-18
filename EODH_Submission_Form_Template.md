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
Flood early-warning systems and parametric insurance triggers across Africa face a critical spatial scale dilemma: coarse hydrological models (0.25 degrees, ~28 km) capture daily catchment soil saturation but average out local floodplains and towns, causing severe basis risk. This notebook synergises three open EODH datasets—EOCIS Soil Moisture Africa (26-year daily baseline, 2000–2026), Copernicus 10 m Land Cover (CLMS), and Sentinel-2 L2A (10 m MNDWI)—across Kenya and Nigeria. We deconstruct coarse cells by sub-pixel asset exposure, verify physical inundation during the May 2024 Kenya flood emergency, and benchmark trigger skill against 62 historical disasters.

## AI Disclosure: Describe how you used AI in authoring this notebook (100 words)
An AI coding assistant (Antigravity) was used to assist with STAC API query syntax, boilerplate Python data-cleaning scripts, and Matplotlib multi-panel figure formatting. The author independently conceived the multi-scale research question, selected the study areas (Kenya and Nigeria), designed the day-of-year rolling Z-score anomaly methodology, formulated the sub-pixel basis-risk analysis, verified all academic citations and DOIs, and interpreted all hydrological and parametric insurance findings.

## References: Provide the URLs of any code sources that you used in authoring this notebook (optional)
- EODH Python Client (`pyeodh`): https://github.com/EO-DataHub/pyeodh
- EODH Documentation: https://docs.eodatahub.org.uk/
- geoBoundaries Open Administrative Boundaries: https://www.geoboundaries.org/
- Dartmouth Flood Observatory (DFO) Archive via HDX: https://data.humdata.org/dataset/global-active-archive-of-large-flood-events-dfo

## Commercial Data: Potential for Future Inclusion of Commercial Data: How could your notebook make use of the commercial datasets on the EODH and how would you adapt the notebook to do this? Not requiring commercial data is a valid response. (100 words)
Operational deployment of this two-tier trigger can directly integrate commercial EODH datasets via the exact same pyeodh STAC workflow. When the open 0.25-degree EOCIS saturation index crosses the Z >= +1.5 alert threshold, the pipeline can automatically query and task commercial high-resolution Synthetic Aperture Radar (Airbus SAR, collection `airbus_sar_data`) to penetrate storm clouds during peak monsoon conditions, alongside sub-meter optical imagery (Airbus Pleiades Neo `airbus_pneo_data` and Planet SkySat `SkySatCollect`) to quantify building-level inundation depths and verify parametric insurance payouts across critical infrastructure.

## Declarations
By submitting this notebook:
- I/we agree to abide by the competition rules.
- I/we confirm this submission is my/our own original work.
- I/we grant the Earth Observation Data Hub a non-exclusive license to use, reproduce, modify, and display my/our work for promotional and educational purposes, including featuring it in the EODH Processes Catalogue and Documentation Site.
- I/we confirm that the code submitted may be published under the MIT license.
- I/we agree for the provided email address to be shared with the prize awarding organisations in the case that my/our notebook is a winning selection.

## Additional Notes (optional)

