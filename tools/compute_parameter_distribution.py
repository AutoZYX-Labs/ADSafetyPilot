#!/usr/bin/env python3
"""Compute percentile distributions for Scenario Evidence Pack event CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PERCENTILES = {
    "P5": 0.05,
    "P10": 0.10,
    "P25": 0.25,
    "P50": 0.50,
    "P75": 0.75,
    "P95": 0.95,
}

DEFAULT_METRICS = {
    "ego_speed_kmh": "km/h",
    "cutin_speed_kmh": "km/h",
    "relative_speed_kmh": "km/h",
    "longitudinal_gap_m": "m",
    "lateral_speed_mps": "m/s",
    "cutin_angle_deg": "deg",
    "cutin_duration_s": "s",
    "ttc_s": "s",
    "thw_s": "s",
    "min_ttc_s": "s",
    "min_thw_s": "s",
    "ego_max_decel_mps2": "m/s2",
    "cutin_lateral_accel_mps2": "m/s2",
}


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if not text or text.lower() in {"na", "n/a", "null", "none", "-"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def percentile_label_to_q(label: str) -> float:
    normalized = label.strip().upper()
    if not normalized.startswith("P"):
        raise ValueError(f"Percentile must use Pxx format, got {label!r}.")
    try:
        value = float(normalized[1:])
    except ValueError as exc:
        raise ValueError(f"Percentile must use Pxx format, got {label!r}.") from exc
    if value < 0 or value > 100:
        raise ValueError(f"Percentile must be between P0 and P100, got {label!r}.")
    return value / 100


def build_group_key(row: dict[str, str], group_by: list[str]) -> str:
    values = []
    for column in group_by:
        raw = row.get(column, "").strip()
        values.append(raw if raw else "unknown")
    return " | ".join(values)


def row_quality(row: dict[str, str]) -> str:
    return row.get("sample_quality", "").strip() or "unknown"


def parse_quality_filter(value: str) -> set[str] | None:
    selected = {part.strip() for part in value.split(",") if part.strip()}
    if not selected or selected == {"all"}:
        return None
    return selected


def quality_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(Counter(row_quality(row) for row in rows))


def missing_counts(rows: list[dict[str, str]], metrics: dict[str, str]) -> dict[str, int]:
    counts = {}
    for metric in metrics:
        counts[metric] = sum(
            1
            for row in rows
            if metric not in row or parse_number(row.get(metric)) is None
        )
    return counts


def convergence_steps(values: list[float], q: float, split_count: int) -> list[dict]:
    steps = []
    for step in range(1, split_count + 1):
        cutoff = math.ceil(len(values) * step / split_count)
        sample = values[:cutoff]
        steps.append(
            {
                "step": step,
                "cumulative_percent": step * 100 / split_count,
                "sample_count": len(sample),
                "value": percentile(sample, q),
            }
        )
    return steps


def relative_fluctuation_percent(values: list[float]) -> float | None:
    if not values:
        return None
    mean_value = sum(values) / len(values)
    if mean_value == 0:
        return 0.0 if max(values) == min(values) else None
    return (max(values) - min(values)) / abs(mean_value) * 100


def compute_convergence_by_speed_bin(
    rows: list[dict[str, str]],
    metrics: dict[str, str],
    target_percentile: str,
    split_count: int,
    threshold_percent: float,
) -> dict:
    target_q = percentile_label_to_q(target_percentile)
    speed_bin_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    missing_speed_bin = 0

    for row in rows:
        speed_bin = row.get("speed_bin", "").strip()
        if not speed_bin:
            missing_speed_bin += 1
            speed_bin = "unknown"
        for metric in metrics:
            if metric not in row:
                continue
            value = parse_number(row.get(metric))
            if value is not None:
                speed_bin_values[speed_bin][metric].append(value)

    bins = {}
    for speed_bin in sorted(speed_bin_values):
        metric_results = {}
        for metric in metrics:
            values = speed_bin_values[speed_bin].get(metric, [])
            steps = convergence_steps(values, target_q, split_count) if values else []
            last_steps = steps[-5:]
            last_values = [step["value"] for step in last_steps if step["value"] is not None]
            fluctuation = relative_fluctuation_percent(last_values) if len(last_values) == 5 else None
            metric_results[metric] = {
                "sample_count": len(values),
                "target_percentile": target_percentile.strip().upper(),
                "split_count": split_count,
                "last_step_count": len(last_values),
                "last_five_values": last_values,
                "relative_fluctuation_percent": fluctuation,
                "threshold_percent": threshold_percent,
                "converged": fluctuation is not None and fluctuation < threshold_percent,
                "steps": steps,
            }
        bins[speed_bin] = metric_results

    return {
        "group_by": "speed_bin",
        "rule": (
            "Split samples by input order, compute cumulative target percentile at each step, "
            "and mark converged when the last five values fluctuate below the threshold."
        ),
        "target_percentile": target_percentile.strip().upper(),
        "split_count": split_count,
        "threshold_percent": threshold_percent,
        "missing_speed_bin_rows": missing_speed_bin,
        "bins": bins,
    }


def compute_distribution(
    input_path: Path,
    output_path: Path,
    pack_id: str,
    group_by: list[str],
    metrics: dict[str, str],
    convergence_target_percentile: str = "P10",
    convergence_split_count: int = 20,
    convergence_threshold_percent: float = 5.0,
    include_convergence: bool = True,
    quality_filter: set[str] | None = None,
) -> dict:
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")
        source_rows = list(reader)

    rows = (
        [row for row in source_rows if row_quality(row) in quality_filter]
        if quality_filter is not None
        else source_rows
    )
    if not rows:
        selected = ", ".join(sorted(quality_filter or [])) or "all"
        raise ValueError(f"No rows remain after applying quality filter: {selected}.")

    grouped_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    grouped_missing: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    evidence_gaps = []

    for row in rows:
        group_key = build_group_key(row, group_by)
        for metric in metrics:
            if metric not in row:
                continue
            value = parse_number(row.get(metric))
            if value is None:
                grouped_missing[metric][group_key] += 1
            else:
                grouped_values[metric][group_key].append(value)

    output_metrics = {}
    for metric, unit in metrics.items():
        groups = {}
        all_group_keys = sorted(set(grouped_values[metric]) | set(grouped_missing[metric]))
        if not all_group_keys:
            evidence_gaps.append(
                {
                    "metric": metric,
                    "gap_type": "missing_column_or_empty_values",
                    "message": f"No numeric values found for {metric}.",
                }
            )
        for group_key in all_group_keys:
            values = grouped_values[metric][group_key]
            groups[group_key] = {
                "count": len(values),
                "missing": grouped_missing[metric][group_key],
                "percentiles": {
                    label: percentile(values, q)
                    for label, q in DEFAULT_PERCENTILES.items()
                },
            }
            if len(values) < 100:
                evidence_gaps.append(
                    {
                        "metric": metric,
                        "group": group_key,
                        "gap_type": "low_sample_count",
                        "count": len(values),
                        "message": "Below the minimum useful threshold for customer-facing percentile evidence.",
                    }
                )
        output_metrics[metric] = {"unit": unit, "groups": groups}

    result = {
        "pack_id": pack_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_from": str(input_path),
        "source_row_count": len(source_rows),
        "row_count": len(rows),
        "quality_filter": sorted(quality_filter) if quality_filter is not None else ["all"],
        "quality_counts": quality_counts(source_rows),
        "filtered_quality_counts": quality_counts(rows),
        "input_missing_counts": missing_counts(source_rows, metrics),
        "filtered_missing_counts": missing_counts(rows, metrics),
        "grouping": group_by,
        "metrics": output_metrics,
        "evidence_gaps": evidence_gaps,
    }
    if include_convergence:
        result["convergence_check"] = compute_convergence_by_speed_bin(
            rows,
            metrics,
            convergence_target_percentile,
            convergence_split_count,
            convergence_threshold_percent,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--pack-id", default="ADSAFETY-EVP-CUTIN-001")
    parser.add_argument("--group-by", default="speed_bin")
    parser.add_argument(
        "--convergence-percentile",
        default="P10",
        help="Target percentile for speed-bin convergence checks. Default: P10.",
    )
    parser.add_argument(
        "--convergence-splits",
        type=int,
        default=20,
        help="Number of input-order splits for cumulative convergence checks. Default: 20.",
    )
    parser.add_argument(
        "--convergence-threshold-percent",
        type=float,
        default=5.0,
        help="Relative fluctuation threshold for convergence. Default: 5.0.",
    )
    parser.add_argument(
        "--no-convergence-check",
        action="store_true",
        help="Disable speed_bin convergence output.",
    )
    parser.add_argument(
        "--metrics",
        default=",".join(DEFAULT_METRICS),
        help="Comma-separated metric columns to compute.",
    )
    parser.add_argument(
        "--quality-filter",
        default="all",
        help="Comma-separated sample_quality values to include, or 'all'. Example: valid.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.convergence_splits < 5:
        raise ValueError("--convergence-splits must be at least 5.")
    percentile_label_to_q(args.convergence_percentile)
    selected_metrics = {}
    for name in [part.strip() for part in args.metrics.split(",") if part.strip()]:
        selected_metrics[name] = DEFAULT_METRICS.get(name, "unknown")
    result = compute_distribution(
        args.input_csv,
        args.output_json,
        args.pack_id,
        [part.strip() for part in args.group_by.split(",") if part.strip()],
        selected_metrics,
        args.convergence_percentile,
        args.convergence_splits,
        args.convergence_threshold_percent,
        not args.no_convergence_check,
        parse_quality_filter(args.quality_filter),
    )
    print(
        f"Wrote {args.output_json} with {result['row_count']} rows "
        f"from {result['source_row_count']} source rows and "
        f"{len(result['evidence_gaps'])} evidence gaps."
    )


if __name__ == "__main__":
    main()
