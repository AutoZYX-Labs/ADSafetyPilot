#!/usr/bin/env python3
"""Generate a public customer-demo summary for an evidence pack."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEMO_METRICS = [
    ("ego_speed_kmh", "Ego speed", "km/h"),
    ("longitudinal_gap_m", "Longitudinal gap", "m"),
    ("lateral_speed_mps", "Lateral speed", "m/s"),
    ("cutin_duration_s", "Cut-in duration", "s"),
    ("min_ttc_s", "Minimum TTC", "s"),
    ("thw_s", "Reference THW", "s"),
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


def distribution_rows(distribution: dict[str, Any], speed_bin: str) -> int:
    group = distribution["metrics"]["ego_speed_kmh"]["groups"].get(speed_bin, {})
    return group.get("count", 0) + group.get("missing", 0)


def build_summary(pack_dir: Path, output_path: Path) -> None:
    summary = load_json(pack_dir / "input_events_summary.json")
    distribution = load_json(pack_dir / "parameter_distribution.json")
    generated_at = datetime.now(timezone.utc).isoformat()
    speed_bins = [
        speed_bin
        for speed_bin in sorted(distribution["metrics"]["ego_speed_kmh"]["groups"])
        if distribution_rows(distribution, speed_bin) >= 100
    ]

    lines = [
        "# Customer Demo Summary: Cut-in Evidence Pack v0.1",
        "",
        f"Generated at: `{generated_at}`",
        "Release status: public demo. Current data is one sample package; the listed parameters are not guaranteed to be converged.",
        "",
        "## What this demonstrates",
        "",
        "This evidence pack converts aerial naturalistic driving data into scenario parameter evidence for cut-in testing and safety analysis.",
        "",
        "The demo chain is:",
        "",
        "```text",
        "extracted cut-in events -> valid-only parameter distribution -> convergence check -> evidence gap -> exemplar-matched test cases",
        "```",
        "",
        "## Data scope",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Extracted cut-in events | {summary.get('row_count', '-')} |",
        f"| Valid rows used for distributions | {distribution.get('row_count', '-')} |",
        f"| Review rows retained for audit | {summary.get('review_count', '-')} |",
        f"| Quality filter | `{', '.join(distribution.get('quality_filter', ['all']))}` |",
        "",
        "Current ODD scope: urban expressway cut-in, congested traffic, one collection region. This is not a full highway cut-in ODD claim, and it should not be interpreted as final converged parameter evidence.",
        "",
        "## Usable speed bins",
        "",
        "| Speed bin | Distribution rows | Demo use |",
        "|---|---:|---|",
    ]

    for speed_bin in sorted(distribution["metrics"]["ego_speed_kmh"]["groups"]):
        rows = distribution_rows(distribution, speed_bin)
        use = "show in demo" if rows >= 100 else "evidence gap"
        lines.append(f"| `{speed_bin}` | {rows} | {use} |")

    lines.extend(
        [
            "",
            "## Parameter evidence",
            "",
            "| Metric | Unit | Speed bin | P10 | P50 | P95 |",
            "|---|---:|---|---:|---:|---:|",
        ]
    )

    for metric, label, unit in DEMO_METRICS:
        for speed_bin in speed_bins:
            group = distribution["metrics"][metric]["groups"][speed_bin]
            percentiles = group["percentiles"]
            lines.append(
                f"| {label} | {unit} | `{speed_bin}` | "
                f"{fmt(percentiles.get('P10'))} | {fmt(percentiles.get('P50'))} | {fmt(percentiles.get('P95'))} |"
            )

    lines.extend(
        [
            "",
            "## Evidence gaps to be transparent about",
            "",
            "- Low-sample bins are not used for percentile claims.",
            "- Review rows are retained for audit but excluded from current distributions.",
            "- Reference-frame TTC has substantial missingness in the full import; public interpretation should use the documented valid-only distribution unless the missingness is resolved.",
            "- Workbook keyframe naming must be reconciled with legacy T1/T2 wording before formal engineering use.",
            "",
            "## Demo positioning",
            "",
            "This is not an AI-generated compliance table. It is a reproducible data evidence pack that can feed SOTIF trigger analysis, scenario representativeness claims, and test-case generation.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output or args.pack_dir / "CUSTOMER_DEMO_SUMMARY.md"
    build_summary(args.pack_dir, output_path)


if __name__ == "__main__":
    main()
