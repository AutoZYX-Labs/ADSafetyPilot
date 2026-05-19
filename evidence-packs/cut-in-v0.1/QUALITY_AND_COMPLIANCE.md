# Quality and Compliance Notes: Cut-in v0.1

This pack is suitable for public demonstration of the evidence-chain method. The current data is one sample package and should not be interpreted as final converged parameter evidence for a full cut-in ODD.

## Current quality gate

Rows enter `parameter_distribution.json` only when `sample_quality = valid`.

A row is marked `review` when any required reference-frame metric is missing or invalid:

- `ego_speed_kmh`
- `cutin_speed_kmh`
- `longitudinal_gap_m`
- `lateral_speed_mps`
- `cutin_duration_s`
- `ttc_s`
- `thw_s`

Current import result:

- Source workbooks: 1389
- Valid rows: 580
- Review rows: 809
- Customer-facing percentile bins for v0.1: `40-60`, `60-80`
- Internal-review-only bins: `0-40`, `80-100`

## Known evidence limits

- The current dataset is urban expressway cut-in data from one city, one road area, one traffic condition, and one collection time period.
- It supports an urban-expressway cut-in evidence demo, not a full highway cut-in ODD claim.
- Reference-frame TTC is missing in many imported rows. This is handled by valid-only filtering, but the missingness itself remains an evidence gap.
- `ego_max_decel_mps2` can still be missing in some valid rows because the current valid rule focuses on reference-frame scenario parameters.
- Workbook keyframe naming must be reconciled with legacy T1/T2 naming before external claims use T1/T2 wording.

## Public sharing rules

Public sharing is allowed for this v0.1 demonstration. Keep the following interpretation limits visible:

- current data is one sample package;
- current values are method-demonstration parameters, not guaranteed converged parameters;
- current values do not represent a full highway cut-in ODD boundary;
- raw workbook packages are not committed to the public repository because of size and update cadence.

## Quality claims still needed

The following evidence should be added before unrestricted customer delivery:

- trajectory extraction quality metrics;
- review/exclude rules for abnormal TTC, THW, DHW, and keyframe values;
- validation sample showing workbook values against visualization screenshots;
- explicit statement that generated test cases are candidates until engineering review and OpenSCENARIO conversion.
