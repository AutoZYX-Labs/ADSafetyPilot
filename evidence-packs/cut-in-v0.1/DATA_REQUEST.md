# Data Contract for Cut-in Evidence Pack v0.1

## Current status

The first real package has been imported:

- Source package: `DRIVEResearch_expressway_1h_cutin_scenarios_20260416`
- Scenario workbooks: 1389
- Event rows: 1389
- Valid rows under current quality rules: 580
- Rows requiring review: 809

Keep this document as the input contract for future cut-in packages.

## Request for future imports

Please provide one event-level cut-in table exported from the DRIVEResearch trajectory/scenario extraction pipeline.

Preferred file name:

```text
input_events.csv
```

Place it at:

```text
evidence-packs/cut-in-v0.1/input_events.csv
```

## Required granularity

One row equals one extracted cut-in event.

Do not provide raw frame-level trajectories for v0.1 unless event-level extraction is not available. Raw trajectories can be added later as source evidence, but the first product loop needs one event summary table.

## Required columns

| Column | Unit | Meaning |
|---|---:|---|
| `event_id` | / | Unique cut-in event ID |
| `source_id` | / | Video / flight / dataset source ID |
| `road_type` | / | `highway` or `urban_expressway` preferred |
| `city` | / | City or collection region |
| `speed_bin` | km/h bin | `0-40`, `40-60`, `60-80`, `80-100`, `100-120` |
| `ego_speed_kmh` | km/h | Ego speed at cut-in reference time |
| `cutin_speed_kmh` | km/h | Cut-in vehicle speed at cut-in reference time |
| `longitudinal_gap_m` | m | Longitudinal gap at cut-in reference time |
| `lateral_speed_mps` | m/s | Cut-in vehicle lateral speed |
| `cutin_duration_s` | s | Time from cut-in start to completion |
| `ttc_s` | s | TTC at cut-in reference time |
| `thw_s` | s | THW at cut-in reference time |

## Recommended columns

| Column | Unit | Meaning |
|---|---:|---|
| `relative_speed_kmh` | km/h | Cut-in vehicle speed minus ego speed |
| `cutin_angle_deg` | deg | Cut-in angle |
| `min_ttc_s` | s | Minimum TTC during the cut-in event |
| `min_thw_s` | s | Minimum THW during the cut-in event |
| `ego_max_decel_mps2` | m/s2 | Maximum ego deceleration during the event |
| `cutin_lateral_accel_mps2` | m/s2 | Cut-in vehicle lateral acceleration |
| `overlap_type` | / | `normal` or `overlap` |
| `sample_quality` | / | `valid`, `review`, or `exclude` |

## Reference time

Use `T1` as the default cut-in reference time if available:

```text
T1 = time when the cut-in vehicle presses the lane marking for the last time.
```

If another reference time is used, add a column:

```text
reference_time_definition
```

and set it consistently for all rows.

## Acceptance check

After a raw workbook package is placed, run the importer:

```bash
python3 tools/import_cutin_scenarios.py \
  evidence-packs/cut-in-v0.1/raw/DRIVEResearch_expressway_1h_cutin_scenarios_20260416 \
  evidence-packs/cut-in-v0.1/input_events.csv \
  --summary-json evidence-packs/cut-in-v0.1/input_events_summary.json
```

Then run:

```bash
python3 tools/compute_parameter_distribution.py \
  evidence-packs/cut-in-v0.1/input_events.csv \
  evidence-packs/cut-in-v0.1/parameter_distribution.json \
  --quality-filter valid
```

The first useful target is not perfection. The first useful target is:

- at least 100 valid cut-in rows in one speed bin;
- no missing values in `ego_speed_kmh`, `longitudinal_gap_m`, `lateral_speed_mps`, `ttc_s`, and `thw_s`;
- visible P5 / P10 / P25 / P50 / P75 / P95 outputs for those metrics;
- `convergence_check` reports P10 speed-bin convergence from 20 cumulative input-order splits.
- `parameter_distribution.json` records `source_row_count`, `row_count`, `quality_filter`, `quality_counts`, and missing counts before and after filtering.
