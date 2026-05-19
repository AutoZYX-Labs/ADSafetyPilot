# Scenario Evidence Pack: Cut-in v0.1

Status: real cut-in package imported; v0.1 evidence outputs generated for review.

## Purpose

This pack turns aerial naturalistic driving data into an auditable evidence chain for highway and urban expressway cut-in scenarios.

The productized chain is:

```text
Naturalistic trajectory data
  -> cut-in event extraction
  -> parameter distribution
  -> safety claim support
  -> test case candidates
  -> evidence report
```

## First scenario

- Scenario ID: `JAMA-SC-002`
- Scenario name: Highway cut-in
- Chinese name: 高速前车切入
- Primary customers: PATAC / ZHUOYU / CMC-style testing and assessment projects
- Primary value: replace one-off analysis slides with a reusable evidence pack.

## Current imported data

The first real import uses:

- Source package: `DRIVEResearch_expressway_1h_cutin_scenarios_20260416`
- Raw files: 1389 cut-in scenario workbooks
- Event rows generated: 1389
- Valid rows under current quality rules: 580
- Rows requiring review: 809
- Customer-facing speed bins for v0.1 percentile evidence: `40-60`, `60-80`
- Internal-review-only speed bins because of low sample count: `0-40`, `80-100`
- Current distribution rule: `sample_quality=valid` only

Generated files:

- [input_events.csv](input_events.csv): event-level import from the workbooks.
- [input_events_summary.json](input_events_summary.json): import counts, field notes, and quality summary.
- [parameter_distribution.json](parameter_distribution.json): percentile distributions and P10 convergence checks.
- [test_cases.yaml](test_cases.yaml): exemplar-matched test-case candidates in the `40-60` and `60-80` speed bins.
- [EVIDENCE_SUMMARY.md](EVIDENCE_SUMMARY.md): concise evidence summary for review.
- [CUSTOMER_DEMO_SUMMARY.md](CUSTOMER_DEMO_SUMMARY.md): public demo summary with explicit sample-size and convergence limits.
- [PARAMETER_DICTIONARY.md](PARAMETER_DICTIONARY.md): parameter definitions, reference-frame policy, and open issues.
- [QUALITY_AND_COMPLIANCE.md](QUALITY_AND_COMPLIANCE.md): quality gate, release limits, and external sharing rules.
- [EVIDENCE_CHAIN.json](EVIDENCE_CHAIN.json): artifact hashes and reproducibility manifest.

## Input contract for future imports

Provide an event-level CSV exported from the cut-in extraction pipeline. Required columns are listed in [input_template.csv](input_template.csv).

Minimum required fields:

- `event_id`
- `source_id`
- `road_type`
- `city`
- `speed_bin`
- `ego_speed_kmh`
- `cutin_speed_kmh`
- `longitudinal_gap_m`
- `lateral_speed_mps`
- `cutin_duration_s`
- `ttc_s`
- `thw_s`

Recommended fields:

- `cutin_angle_deg`
- `min_ttc_s`
- `min_thw_s`
- `ego_max_decel_mps2`
- `cutin_lateral_accel_mps2`
- `overlap_type`
- `sample_quality`

## Outputs

The current v0.1 output target is a folder containing:

- `parameter_distribution.json`: P5 / P10 / P25 / P50 / P75 / P95 by metric and speed bin, plus P10 convergence status by speed bin.
- `test_cases.yaml`: representative, boundary, and challenge test-case candidates matched to real event exemplars.
- `safety_mapping.yaml`: links from data parameters to SOTIF / HARA / test planning claims.
- `evidence_sources.yaml`: source traceability and data confidence statements.
- `EVIDENCE_SUMMARY.md`: generated Markdown report summarizing coverage, percentiles, convergence, and gaps.
- `CUSTOMER_DEMO_SUMMARY.md`: public demo summary that states the current data is one sample package and does not guarantee parameter convergence.
- `EVIDENCE_CHAIN.json`: generated chain-of-custody manifest with artifact hashes.

## Acceptance criteria for v0.1

1. One cut-in CSV can be processed without manual spreadsheet work.
2. The output contains sample counts and percentiles for every core parameter.
3. Each proposed test case cites the data distribution that produced it.
4. Every safety claim is linked to at least one metric and one data source.
5. Missing data is reported as an evidence gap instead of being silently filled.
6. Speed-bin convergence is reported from 20 input-order cumulative splits; the default P10 result is converged when the last five steps fluctuate by less than 5%.

## Current decision

The first pack focuses on `cut-in` because it is already present in:

- PATAC structured-road scenario convergence plan.
- ADSafetyPilot `JAMA-SC-002`.
- DRIVEResearch historical cut-in definition and extraction materials from 2021.
- PT7 / PT9 patent materials on percentile-based scenario parameter convergence and risk scoring.

## Rebuild commands

Import the raw workbook package:

```bash
python3 tools/import_cutin_scenarios.py \
  evidence-packs/cut-in-v0.1/raw/DRIVEResearch_expressway_1h_cutin_scenarios_20260416 \
  evidence-packs/cut-in-v0.1/input_events.csv \
  --summary-json evidence-packs/cut-in-v0.1/input_events_summary.json
```

Compute distributions:

```bash
python3 tools/compute_parameter_distribution.py \
  evidence-packs/cut-in-v0.1/input_events.csv \
  evidence-packs/cut-in-v0.1/parameter_distribution.json \
  --quality-filter valid
```

Generate evidence summary and test-case candidates:

```bash
python3 tools/generate_evidence_report.py evidence-packs/cut-in-v0.1

python3 tools/generate_customer_demo_summary.py evidence-packs/cut-in-v0.1

python3 tools/generate_cutin_test_cases.py \
  evidence-packs/cut-in-v0.1/parameter_distribution.json \
  evidence-packs/cut-in-v0.1/input_events.csv \
  evidence-packs/cut-in-v0.1/test_cases.yaml

python3 tools/generate_evidence_chain.py evidence-packs/cut-in-v0.1
```
