# Evidence Summary: Cut-in v0.1

Generated at: `2026-05-19T13:57:43.801530+00:00`
Pack ID: `ADSAFETY-EVP-CUTIN-001`
Source package: `DRIVEResearch_expressway_1h_cutin_scenarios_20260416`
Release status: public demo. Current data is one sample package; the listed parameters are not guaranteed to be converged.

## Imported data

| Item | Value |
|---|---:|
| Scenario workbooks imported | 1389 |
| Event rows generated | 1389 |
| Rows used for current distribution | 580 |
| Distribution quality filter | `valid` |
| Valid rows under current quality rules | 580 |
| Rows requiring review | 809 |
| Distribution evidence gaps | 26 |

## Speed-bin coverage

| Speed bin | Imported rows | Distribution rows | Current use |
|---|---:|---:|---|
| `0-40` | 30 | 6 | evidence gap; insufficient sample |
| `40-60` | 853 | 270 | public demo percentile evidence |
| `60-80` | 496 | 294 | public demo percentile evidence |
| `80-100` | 10 | 10 | evidence gap; insufficient sample |

## Key percentiles

The table below reports the bins with at least 100 rows. Values are generated from real extracted events, not illustrative defaults. They demonstrate the evidence-chain method and should not be interpreted as final converged parameters.

| Metric | Unit | Speed bin | Count | Missing | P10 | P50 | P95 |
|---|---:|---|---:|---:|---:|---:|---:|
| Ego speed | km/h | `40-60` | 270 | 0 | 48.142 | 55.251 | 59.187 |
| Ego speed | km/h | `60-80` | 294 | 0 | 61.518 | 66.612 | 76.352 |
| Cut-in speed | km/h | `40-60` | 270 | 0 | 43.522 | 51.386 | 61.073 |
| Cut-in speed | km/h | `60-80` | 294 | 0 | 48.059 | 57.928 | 69.068 |
| Relative speed | km/h | `40-60` | 270 | 0 | -8.904 | -2.997 | 9.094 |
| Relative speed | km/h | `60-80` | 294 | 0 | -20.03 | -8.68 | -0.541 |
| Longitudinal gap | m | `40-60` | 270 | 0 | 11.544 | 35.706 | 121.7 |
| Longitudinal gap | m | `60-80` | 294 | 0 | 17.34 | 48.877 | 146.596 |
| Lateral speed | m/s | `40-60` | 270 | 0 | 0.167 | 0.397 | 0.782 |
| Lateral speed | m/s | `60-80` | 294 | 0 | 0.111 | 0.425 | 0.865 |
| Cut-in duration | s | `40-60` | 270 | 0 | 16.016 | 19.467 | 25.1 |
| Cut-in duration | s | `60-80` | 294 | 0 | 14.41 | 17.233 | 22.737 |
| Reference TTC | s | `40-60` | 270 | 0 | 13.736 | 41.05 | 516.589 |
| Reference TTC | s | `60-80` | 294 | 0 | 8.994 | 22.296 | 186.33 |
| Minimum TTC | s | `40-60` | 270 | 0 | 7.632 | 18.995 | 83.911 |
| Minimum TTC | s | `60-80` | 294 | 0 | 7.421 | 15.938 | 64.922 |
| Reference THW | s | `40-60` | 270 | 0 | 0.744 | 2.497 | 7.975 |
| Reference THW | s | `60-80` | 294 | 0 | 0.924 | 2.686 | 7.902 |
| Ego max deceleration | m/s2 | `40-60` | 263 | 7 | -1.204 | -0.543 | -0.157 |
| Ego max deceleration | m/s2 | `60-80` | 285 | 9 | -1.519 | -0.575 | -0.135 |

## P10 convergence check

Rule: split samples by input order into 20 cumulative steps. A metric is marked converged when the last five P10 values fluctuate by less than 5%.

| Speed bin | Metric | Sample count | Last-five fluctuation | Status |
|---|---|---:|---:|---|
| `40-60` | `ego_speed_kmh` | 270 | 0.237% | converged |
| `40-60` | `longitudinal_gap_m` | 270 | 4.069% | converged |
| `40-60` | `lateral_speed_mps` | 270 | 4.342% | converged |
| `40-60` | `cutin_duration_s` | 270 | 2.648% | converged |
| `40-60` | `min_ttc_s` | 270 | 0.929% | converged |
| `40-60` | `thw_s` | 270 | 6.379% | not converged |
| `60-80` | `ego_speed_kmh` | 294 | 0.147% | converged |
| `60-80` | `longitudinal_gap_m` | 294 | 1.578% | converged |
| `60-80` | `lateral_speed_mps` | 294 | 29.086% | not converged |
| `60-80` | `cutin_duration_s` | 294 | 1.488% | converged |
| `60-80` | `min_ttc_s` | 294 | 1.797% | converged |
| `60-80` | `thw_s` | 294 | 2.718% | converged |

## Evidence gaps and limits

- Low-sample speed bins: `0-40`, `80-100`.
- Missing values by key metric before and after the distribution quality filter:
  - `ttc_s`: 807 imported missing rows; 0 distribution missing rows
  - `min_ttc_s`: 472 imported missing rows; 0 distribution missing rows
  - `thw_s`: 19 imported missing rows; 0 distribution missing rows
  - `ego_max_decel_mps2`: 55 imported missing rows; 16 distribution missing rows

## Current interpretation

- The current percentiles are generated with quality filter `valid`.
- The pack can support a public minimum sellable demo for data-backed urban-expressway cut-in percentile evidence in the `40-60` and `60-80` speed bins.
- The current data is one sample package, not full highway cut-in ODD coverage; the listed parameters are not guaranteed to be converged.
- Reference-frame TTC is the weakest field in the full import; valid-only filtering removes these rows from the current customer-facing distribution.
- `0-40` and `80-100` bins should not be used for public percentile claims until more valid samples are added.
- Generated test cases are already matched to real exemplar events in `test_cases.yaml`; they still need engineering review before OpenSCENARIO conversion.

## Next engineering actions

1. Resolve the reference-frame TTC semantics and decide whether customer-facing claims should use `ttc_s`, `min_ttc_s`, or both.
2. Attach source workbook paths, source video IDs, quality notes, and optional visualization thumbnails to each test case for audit traceability.
3. Add a review rule that blocks OpenSCENARIO export when the selected exemplar row has missing or review-only source metrics.
4. Add an OpenSCENARIO export path after the evidence report and test-case candidates stabilize.
