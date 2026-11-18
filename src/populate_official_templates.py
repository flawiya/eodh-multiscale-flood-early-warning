"""Populate the official EODH competition template files in the project root:
  - LICENSE
  - EODH_Submission_Form_Template.md
  - EODH_Community_Notebook_Competition_2026_Template.ipynb
"""
import os
import shutil
import nbformat as nbf

# 1. Copy official MIT LICENSE from template
shutil.copyfile("docs/official_template/LICENSE", "LICENSE")

# 2. Populate EODH_Submission_Form_Template.md
# Read original declarations block from template so we preserve exact wording
with open("docs/official_template/EODH_Submission_Form_Template.md", "r", encoding="utf8") as f:
    orig_form = f.read()

decl_idx = orig_form.find("## Declarations")
decl_block = orig_form[decl_idx:]

abstract_text = (
    "Flood early-warning systems and parametric insurance triggers across Africa face a critical spatial scale "
    "dilemma: coarse hydrological models (0.25 degrees, ~28 km) capture daily catchment soil saturation but "
    "average out local floodplains and towns, causing severe basis risk. This notebook synergises three open EODH "
    "datasets—EOCIS Soil Moisture Africa (26-year daily baseline, 2000–2026), Copernicus 10 m Land Cover (CLMS), "
    "and Sentinel-2 L2A (10 m MNDWI)—across Kenya and Nigeria. We deconstruct coarse cells by sub-pixel asset "
    "exposure, verify physical inundation during the May 2024 Kenya flood emergency, and benchmark trigger skill "
    "against 62 historical disasters."
)

ai_text = (
    "An AI coding assistant (Antigravity) was used to assist with STAC API query syntax, boilerplate Python "
    "data-cleaning scripts, and Matplotlib multi-panel figure formatting. The author independently conceived the "
    "multi-scale research question, selected the study areas (Kenya and Nigeria), designed the day-of-year rolling "
    "Z-score anomaly methodology, formulated the sub-pixel basis-risk analysis, verified all academic citations "
    "and DOIs, and interpreted all hydrological and parametric insurance findings."
)

refs_text = (
    "- EODH Python Client (`pyeodh`): https://github.com/EO-DataHub/pyeodh\n"
    "- EODH Documentation: https://docs.eodatahub.org.uk/\n"
    "- geoBoundaries Open Administrative Boundaries: https://www.geoboundaries.org/\n"
    "- Dartmouth Flood Observatory (DFO) Archive via HDX: https://data.humdata.org/dataset/global-active-archive-of-large-flood-events-dfo"
)

commercial_text = (
    "Operational deployment of this two-tier trigger can directly integrate commercial EODH datasets via the exact "
    "same pyeodh STAC workflow. When the open 0.25-degree EOCIS saturation index crosses the Z >= +1.5 alert "
    "threshold, the pipeline can automatically query and task commercial high-resolution Synthetic Aperture Radar "
    "(Airbus SAR, collection `airbus_sar_data`) to penetrate storm clouds during peak monsoon conditions, alongside "
    "sub-meter optical imagery (Airbus Pleiades Neo `airbus_pneo_data` and Planet SkySat `SkySatCollect`) to "
    "quantify building-level inundation depths and verify parametric insurance payouts across critical infrastructure."
)

print("Word counts -> Abstract:", len(abstract_text.split()),
      "| AI Disclosure:", len(ai_text.split()),
      "| Commercial:", len(commercial_text.split()))

submission_md = f"""---
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
{abstract_text}

## AI Disclosure: Describe how you used AI in authoring this notebook (100 words)
{ai_text}

## References: Provide the URLs of any code sources that you used in authoring this notebook (optional)
{refs_text}

## Commercial Data: Potential for Future Inclusion of Commercial Data: How could your notebook make use of the commercial datasets on the EODH and how would you adapt the notebook to do this? Not requiring commercial data is a valid response. (100 words)
{commercial_text}

{decl_block}
"""

with open("EODH_Submission_Form_Template.md", "w", encoding="utf8") as f:
    f.write(submission_md)

print("Wrote EODH_Submission_Form_Template.md")

