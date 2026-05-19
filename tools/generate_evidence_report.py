#!/usr/bin/env python3
"""Generate a Markdown evidence summary from an evidence-pack output folder."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


KEY_METRICS = [
    ("ego_speed_kmh", "Ego speed"),
    ("cutin_speed_kmh", "Cut-in speed"),
    ("relative_speed_kmh", "Relative speed"),
    ("longitudinal_gap_m", "Longitudinal gap"),
    ("lateral_speed_mps", "Lateral speed"),
    ("cutin_duration_s", "Cut-in duration"),
    ("ttc_s", "Reference TTC"),
    ("min_ttc_s", "Minimum TTC"),
    ("thw_s", "Reference THW"),
    ("ego_max_decel_mps2", "Ego max deceleration"),
]

CONVERGENCE_METRICS = [
    "ego_speed_kmh",
    "longitudinal_gap_m",
    "lateral_speed_mps",
    "cutin_duration_s",
    "min_ttc_s",
    "thw_s",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "-"
    if isinstance(value, (int, float)):
        rounded = round(float(value), digits)
        if rounded == 0:
            rounded = 0.0
        text = f"{rounded:.{digits}f}".rstrip("0").rstrip(".")
        return text or "0"
    return str(value)


def metric_groups(distribution: dict[str, Any], metric: str) -> dict[str, Any]:
    return distribution["metrics"].get(metric, {}).get("groups", {})


def total_missing(distribution: dict[str, Any], metric: str) -> int:
    return sum(group.get("missing", 0) for group in metric_groups(distribution, metric).values())


def input_bin_counts(summary: dict[str, Any]) -> dict[str, int]:
    if "speed_bin_counts" in summary:
        return {str(k): int(v) for k, v in summary["speed_bin_counts"].items()}
    return {}


def distribution_bin_counts(distribution: dict[str, Any]) -> dict[str, int]:
    return {
        speed_bin: group.get("count", 0) + group.get("missing", 0)
        for speed_bin, group in metric_groups(distribution, "ego_speed_kmh").items()
    }


def customer_facing_bins(counts: dict[str, int], threshold: int = 100) -> list[str]:
    return [speed_bin for speed_bin, count in counts.items() if count >= threshold]


def build_report(pack_dir: Path, output_path: Path) -> None:
    summary = load_json(pack_dir / "input_events_summary.json")
    distribution = load_json(pack_dir / "parameter_distribution.json")
    imported_counts = input_bin_counts(summary)
    distribution_counts = distribution_bin_counts(distribution)
    strong_bins = customer_facing_bins(distribution_counts)
    low_bins = [speed_bin for speed_bin, count in distribution_counts.items() if count < 100]
    generated_at = datetime.now(timezone.utc).isoformat()
    quality_filter = ", ".join(distribution.get("quality_filter", ["all"]))

    lines: list[str] = [
        "# Evidence Summary: Cut-in v0.1",
        "",
        f"Generated at: `{generated_at}`",
        f"Pack ID: `{distribution.get('pack_id', '-')}`",
        f"Source package: `{summary.get('source_package', '-')}`",
        "Release status: public demo. Current data is one sample package; the listed parameters are not guaranteed to be converged.",
        "",
        "## Imported data",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Scenario workbooks imported | {summary.get('file_count', '-')} |",
        f"| Event rows generated | {distribution.get('source_row_count', summary.get('row_count', '-'))} |",
        f"| Rows used for current distribution | {distribution.get('row_count', '-')} |",
        f"| Distribution quality filter | `{quality_filter}` |",
        f"| Valid rows under current quality rules | {summary.get('valid_count', '-')} |",
        f"| Rows requiring review | {summary.get('review_count', '-')} |",
        f"| Distribution evidence gaps | {len(distribution.get('evidence_gaps', []))} |",
        "",
        "## Speed-bin coverage",
        "",
        "| Speed bin | Imported rows | Distribution rows | Current use |",
        "|---|---:|---:|---|",
    ]

    for speed_bin in sorted(set(imported_counts) | set(distribution_counts)):
        imported = imported_counts.get(speed_bin, 0)
        used = distribution_counts.get(speed_bin, 0)
        use = "public demo percentile evidence" if used >= 100 else "evidence gap; insufficient sample"
        lines.append(f"| `{speed_bin}` | {imported} | {used} | {use} |")

    lines.extend(
        [
            "",
            "## Key percentiles",
            "",
            "The table below reports the bins with at least 100 rows. Values are generated from real extracted events, not illustrative defaults. They demonstrate the evidence-chain method and should not be interpreted as final converged parameters.",
            "",
            "| Metric | Unit | Speed bin | Count | Missing | P10 | P50 | P95 |",
            "|---|---:|---|---:|---:|---:|---:|---:|",
        ]
    )

    for metric, label in KEY_METRICS:
        metric_data = distribution["metrics"].get(metric, {})
        unit = metric_data.get("unit", "-")
        for speed_bin in strong_bins:
            group = metric_data.get("groups", {}).get(speed_bin)
            if not group:
                continue
            percentiles = group.get("percentiles", {})
            lines.append(
                "| "
                f"{label} | {unit} | `{speed_bin}` | {group.get('count', 0)} | {group.get('missing', 0)} | "
                f"{fmt(percentiles.get('P10'))} | {fmt(percentiles.get('P50'))} | {fmt(percentiles.get('P95'))} |"
            )

    lines.extend(
        [
            "",
            "## P10 convergence check",
            "",
            "Rule: split samples by input order into 20 cumulative steps. A metric is marked converged when the last five P10 values fluctuate by less than 5%.",
            "",
            "| Speed bin | Metric | Sample count | Last-five fluctuation | Status |",
            "|---|---|---:|---:|---|",
        ]
    )

    bins = distribution.get("convergence_check", {}).get("bins", {})
    for speed_bin in strong_bins:
        for metric in CONVERGENCE_METRICS:
            result = bins.get(speed_bin, {}).get(metric)
            if not result:
                continue
            status = "converged" if result.get("converged") else "not converged"
            lines.append(
                f"| `{speed_bin}` | `{metric}` | {result.get('sample_count', 0)} | "
                f"{fmt(result.get('relative_fluctuation_percent'))}% | {status} |"
            )

    input_missing = distribution.get("input_missing_counts", {})
    filtered_missing = distribution.get("filtered_missing_counts", {})

    lines.extend(
        [
            "",
            "## Evidence gaps and limits",
            "",
            f"- Low-sample speed bins: {', '.join(f'`{item}`' for item in low_bins) if low_bins else 'none'}.",
            "- Missing values by key metric before and after the distribution quality filter:",
        ]
    )
    for metric, _label in KEY_METRICS:
        before = input_missing.get(metric, 0)
        after = filtered_missing.get(metric, 0)
        if before or after:
            lines.append(f"  - `{metric}`: {before} imported missing rows; {after} distribution missing rows")
    if not any(input_missing.get(metric, 0) or filtered_missing.get(metric, 0) for metric, _label in KEY_METRICS):
        lines.append("  - none")

    lines.extend(
        [
            "",
            "## Current interpretation",
            "",
            f"- The current percentiles are generated with quality filter `{quality_filter}`.",
            "- The pack can support a public minimum sellable demo for data-backed urban-expressway cut-in percentile evidence in the `40-60` and `60-80` speed bins.",
            "- The current data is one sample package, not full highway cut-in ODD coverage; the listed parameters are not guaranteed to be converged.",
            "- Reference-frame TTC is the weakest field in the full import; valid-only filtering removes these rows from the current customer-facing distribution.",
            "- `0-40` and `80-100` bins should not be used for public percentile claims until more valid samples are added.",
            "- Generated test cases are already matched to real exemplar events in `test_cases.yaml`; they still need engineering review before OpenSCENARIO conversion.",
            "",
            "## Next engineering actions",
            "",
            "1. Resolve the reference-frame TTC semantics and decide whether customer-facing claims should use `ttc_s`, `min_ttc_s`, or both.",
            "2. Attach source workbook paths, source video IDs, quality notes, and optional visualization thumbnails to each test case for audit traceability.",
            "3. Add a review rule that blocks OpenSCENARIO export when the selected exemplar row has missing or review-only source metrics.",
            "4. Add an OpenSCENARIO export path after the evidence report and test-case candidates stabilize.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output or args.pack_dir / "EVIDENCE_SUMMARY.md"
    build_report(args.pack_dir, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
