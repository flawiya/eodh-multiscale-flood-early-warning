# Pre-check report: EOCIS soil moisture subsets

- Days attempted: **9528**, downloaded OK: **9528**, failed / missing: **0**

## Nigeria

- Files: 27 (2000-2026), time steps: 9528, 2000-01-01 -> 2026-01-31
- Missing days inside range: **0**; duplicated timestamps: **0**
- Grid: 41 x 50 cells at 0.25 deg; lat 4.125..14.125, lon 2.625..14.875

| variable | NaN % | fill-value % | min (valid) | max (valid) | mean (valid) |
|---|---|---|---|---|---|
| smc_avail_top | 4.29 | 0.00 | 0 | 287.1 | 80.31 |
| smcl | 4.29 | 0.00 | 0.04595 | 864.2 | 150 |
| precip | 0.00 | 6.59 | 0 | 0.001568 | 3.877e-05 |
| runoff | 4.29 | 2.29 | 0 | 0.001408 | 1.237e-05 |
| fao_et0 | 4.29 | 0.00 | 6.742e-06 | 0.0001477 | 4.825e-05 |
- Precipitation converted to mm/day: mean 3.35, 99.9th pct 42.7, max 135.4

## Kenya

- Files: 27 (2000-2026), time steps: 9528, 2000-01-01 -> 2026-01-31
- Missing days inside range: **0**; duplicated timestamps: **0**
- Grid: 43 x 34 cells at 0.25 deg; lat -4.875..5.625, lon 33.875..42.125

| variable | NaN % | fill-value % | min (valid) | max (valid) | mean (valid) |
|---|---|---|---|---|---|
| smc_avail_top | 6.29 | 0.00 | 0 | 259.2 | 28.82 |
| smcl | 6.29 | 0.00 | 0.1122 | 713 | 115.8 |
| precip | 0.00 | 7.93 | 0 | 0.001961 | 2.061e-05 |
| runoff | 6.29 | 1.64 | 0 | 0.001607 | 5.011e-06 |
| fao_et0 | 6.29 | 0.00 | 5.372e-06 | 0.0001064 | 5.136e-05 |
- Precipitation converted to mm/day: mean 1.78, 99.9th pct 50.7, max 169.4

## Issues to handle in the cleaning step
- Cells outside land / outside the model domain are stored either as NaN or as a huge fill value (about 2e20) -> must be masked to NaN.
- Units are per-second fluxes (kg m-2 s-1): convert to mm/day (x 86400).
- `smcl` has 4 soil layers (0-10, 10-35, 35-100, 100-300 cm): derive column totals / root-zone.