# Parameter Dictionary: Cut-in v0.1

This document fixes the current event-level parameter contract for the cut-in evidence pack.

## Scope

- Source package: `DRIVEResearch_expressway_1h_cutin_scenarios_20260416`
- Data source type: extracted cut-in scenario workbooks
- Frame rate: 30 fps
- Current reference-frame policy: `keyframe3,keyframe2,keyframe1,keyframe4,keyframe5` priority order
- Current duration policy: `(keyframe4 - keyframe1) / 30 fps`

Open issue before external release:

The current workbook uses `keyframe1` to `keyframe5`, while legacy cut-in materials describe T1/T2-style reference moments. The current import uses `keyframe3` for reference-frame kinematics because it is consistently available in the workbook and aligned with the extracted interaction point. The exact mapping between workbook keyframes and legacy T labels must be confirmed before customer-facing claims use T1/T2 wording.

## Event identity

| Field | Definition | Current source | Quality rule |
|---|---|---|---|
| `event_id` | Unique event ID combining source video and workbook stem. | source directory + workbook filename | Required |
| `source_id` | Source video or flight directory. | parent DJI directory | Sensitive for external release |
| `source_file` | Workbook path relative to raw package. | local raw package path | Sensitive for external release |
| `sample_quality` | Current row-level quality label. | importer rules | `valid` rows enter current distribution |
| `quality_notes` | Semicolon-separated review reasons. | importer rules | Must be reviewed before export |

## Core metrics

| Field | Unit | Definition | Current source | Missing/review rule |
|---|---:|---|---|---|
| `ego_speed_kmh` | km/h | Absolute ego longitudinal velocity at reference frame. | `ego_veh.longitudinal_velocity_m_per_s * 3.6` | Missing marks row review |
| `cutin_speed_kmh` | km/h | Absolute cut-in vehicle longitudinal velocity at reference frame. | `traffic_veh.longitudinal_velocity_m_per_s * 3.6` | Missing marks row review |
| `relative_speed_kmh` | km/h | Cut-in speed minus ego speed. Negative means the cut-in vehicle is slower. | computed | Missing if either speed is missing |
| `longitudinal_gap_m` | m | Ego headway distance at reference frame. | Prefer `ego_veh.DHW`; geometry fallback is noted | Missing marks row review |
| `longitudinal_gap_signed_m` | m | Signed geometric projection from ego to cut-in vehicle. | computed fallback only | Blank when source DHW is used |
| `lateral_speed_mps` | m/s | Absolute cut-in lateral velocity at reference frame. | `traffic_veh.lateral_velocity_m_per_s` | Missing marks row review |
| `cutin_angle_deg` | deg | Cut-in vehicle heading minus ego heading, normalized to [-180, 180]. | `traffic_veh.heading - ego_veh.heading` | Missing if either heading is missing |
| `cutin_duration_s` | s | Current lane-change duration proxy. | `(keyframe4 - keyframe1) / 30` | Missing marks row review |
| `ttc_s` | s | Ego TTC at reference frame. | `ego_veh.TTC` | Negative or missing marks row review |
| `thw_s` | s | Ego THW at reference frame. | `ego_veh.THW`; computed fallback only when necessary | Negative or missing marks row review |
| `min_ttc_s` | s | Minimum TTC recorded by the scenario extractor. | `feature.TTC_min_s` | Missing does not by itself exclude current valid row |
| `min_thw_s` | s | Minimum non-negative THW over common ego and cut-in frames. | `ego_veh.THW` over event frames | Missing is reported in distribution |
| `ego_max_decel_mps2` | m/s2 | Maximum ego deceleration during the event; negative value is preserved. | `feature.Max_deacceration_mps2` | Missing is reported in distribution |
| `cutin_lateral_accel_mps2` | m/s2 | Maximum absolute cut-in lateral acceleration over event frames. | `traffic_veh.lateral_acceleration_m_per_s2` | Missing is reported in distribution |

## Current distribution rule

`parameter_distribution.json` is generated with:

```bash
python3 tools/compute_parameter_distribution.py \
  evidence-packs/cut-in-v0.1/input_events.csv \
  evidence-packs/cut-in-v0.1/parameter_distribution.json \
  --quality-filter valid
```

This means `review` rows remain in `input_events.csv` for audit, but do not enter the current percentile or convergence results.
