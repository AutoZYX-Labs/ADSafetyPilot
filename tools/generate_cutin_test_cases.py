#!/usr/bin/env python3
"""Generate cut-in test-case candidates by matching percentile targets to real events."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CASE_POLICIES = {
    "representative": {
        "ego_speed_kmh": "P50",
        "cutin_speed_kmh": "P50",
        "longitudinal_gap_m": "P50",
        "lateral_speed_mps": "P50",
        "cutin_duration_s": "P50",
        "min_ttc_s": "P50",
        "thw_s": "P50",
    },
    "boundary": {
        "ego_speed_kmh": "P50",
        "cutin_speed_kmh": "P50",
        "longitudinal_gap_m": "P10",
        "lateral_speed_mps": "P75",
        "cutin_duration_s": "P25",
        "min_ttc_s": "P10",
        "thw_s": "P10",
    },
    "challenge": {
        "ego_speed_kmh": "P75",
        "longitudinal_gap_m": "P10",
        "lateral_speed_mps": "P95",
        "min_ttc_s": "P10",
        "thw_s": "P10",
        "ego_max_decel_mps2": "P10",
        "cutin_lateral_accel_mps2": "P95",
    },
}

CASE_DESCRIPTIONS = {
    "representative": "Representative cut-in behavior matched to the median region of the selected speed bin.",
    "boundary": "Boundary cut-in behavior near the lower gap / lower time-margin region.",
    "challenge": "High-risk cut-in behavior matched to small time margin, small gap, and high lateral demand.",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        rounded = round(float(value), digits)
        if rounded == 0:
            rounded = 0.0
        text = f"{rounded:.{digits}f}".rstrip("0").rstrip(".")
        return text or "0"
    text = str(value).replace('"', '\\"')
    return f'"{text}"'


def metric_group(distribution: dict[str, Any], metric: str, speed_bin: str) -> dict[str, Any]:
    return distribution["metrics"][metric]["groups"][speed_bin]


def percentile_value(distribution: dict[str, Any], metric: str, speed_bin: str, percentile: str) -> float | None:
    return metric_group(distribution, metric, speed_bin)["percentiles"].get(percentile)


def metric_span(distribution: dict[str, Any], metric: str, speed_bin: str) -> float:
    percentiles = metric_group(distribution, metric, speed_bin)["percentiles"]
    p25 = percentiles.get("P25")
    p75 = percentiles.get("P75")
    if p25 is not None and p75 is not None and p75 != p25:
        return abs(p75 - p25)
    p50 = percentiles.get("P50")
    return max(abs(p50 or 0.0), 1.0)


def select_speed_bins(distribution: dict[str, Any], requested: str | None) -> list[str]:
    groups = distribution["metrics"]["ego_speed_kmh"]["groups"]
    if requested:
        selected = [part.strip() for part in requested.split(",") if part.strip()]
        missing = [speed_bin for speed_bin in selected if speed_bin not in groups]
        if missing:
            raise ValueError(f"Speed bins are not available: {', '.join(missing)}.")
        return selected
    selected = [
        speed_bin
        for speed_bin, group in groups.items()
        if group.get("count", 0) + group.get("missing", 0) >= 100
    ]
    return selected or [max(groups, key=lambda name: groups[name].get("count", 0))]


def case_id(speed_bin: str, case_type: str) -> str:
    speed_code = speed_bin.replace(">=", "GE").replace("<", "LT").replace("-", "")
    type_code = {
        "representative": "REP",
        "boundary": "BOUNDARY",
        "challenge": "CHALLENGE",
    }[case_type]
    return f"TC-CUTIN-{speed_code}-{type_code}-001"


def load_rows(path: Path, speed_bin: str, allow_review: bool) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates = [row for row in rows if row.get("speed_bin") == speed_bin]
    if not allow_review:
        candidates = [row for row in candidates if row.get("sample_quality") == "valid"]
    return candidates


def score_row(row: dict[str, str], targets: dict[str, float], spans: dict[str, float]) -> float | None:
    total = 0.0
    used = 0
    for metric, target in targets.items():
        value = parse_number(row.get(metric))
        if value is None:
            return None
        span = spans[metric] or 1.0
        total += ((value - target) / span) ** 2
        used += 1
    if used == 0:
        return None
    return total / used


def select_exemplar(
    rows: list[dict[str, str]],
    distribution: dict[str, Any],
    speed_bin: str,
    policy: dict[str, str],
) -> tuple[dict[str, str], dict[str, float], dict[str, float], float]:
    targets: dict[str, float] = {}
    spans: dict[str, float] = {}
    for metric, percentile in policy.items():
        target = percentile_value(distribution, metric, speed_bin, percentile)
        if target is None:
            raise ValueError(f"No target value for {metric} {percentile} in {speed_bin}.")
        targets[metric] = target
        spans[metric] = metric_span(distribution, metric, speed_bin)

    best_row: dict[str, str] | None = None
    best_score: float | None = None
    for row in rows:
        score = score_row(row, targets, spans)
        if score is None:
            continue
        if best_score is None or score < best_score:
            best_row = row
            best_score = score
    if best_row is None or best_score is None:
        raise ValueError("No event row can satisfy all target metrics.")
    return best_row, targets, spans, best_score


def yaml_scalar(value: Any) -> str:
    return fmt(value)


def write_cases(
    output_path: Path,
    distribution: dict[str, Any],
    input_csv: Path,
    speed_bins: list[str],
    allow_review: bool,
) -> None:
    lines = [
        "pack_id: ADSAFETY-EVP-CUTIN-001",
        'version: "0.1"',
        "status: generated_exemplar_candidates",
        f"generated_at: {yaml_scalar(datetime.now(timezone.utc).isoformat())}",
        "source:",
        "  parameter_distribution: parameter_distribution.json",
        "  input_events: input_events.csv",
        "  speed_bins:",
        *[f"    - {yaml_scalar(speed_bin)}" for speed_bin in speed_bins],
        f"  candidate_row_policy: {yaml_scalar('valid rows only' if not allow_review else 'valid and review rows')}",
        "generation_policy:",
        "  percentile_targets: Use per-metric percentile targets within one speed bin.",
        "  exemplar_matching: Select the nearest real event row so the case remains physically consistent.",
        "  challenge_case: Use more demanding percentile bands without independently mixing impossible extremes.",
        "cases:",
    ]

    for speed_bin in speed_bins:
        rows = load_rows(input_csv, speed_bin, allow_review)
        if not rows:
            raise ValueError(f"No candidate rows found for speed bin {speed_bin!r}.")
        for case_type, policy in CASE_POLICIES.items():
            row, targets, _spans, score = select_exemplar(rows, distribution, speed_bin, policy)
            lines.extend(
                [
                    f"  - id: {yaml_scalar(case_id(speed_bin, case_type))}",
                    f"    type: {yaml_scalar(case_type)}",
                    "    status: ready_for_review",
                    "    scenario_id: JAMA-SC-002",
                    f"    speed_bin: {yaml_scalar(speed_bin)}",
                    f"    description: {yaml_scalar(CASE_DESCRIPTIONS[case_type])}",
                    "    selected_event:",
                    f"      event_id: {yaml_scalar(row.get('event_id'))}",
                    f"      source_id: {yaml_scalar(row.get('source_id'))}",
                    f"      source_file: {yaml_scalar(row.get('source_file'))}",
                    f"      sample_quality: {yaml_scalar(row.get('sample_quality'))}",
                    f"      match_score: {fmt(score)}",
                    "    percentile_policy:",
                ]
            )
            for metric, percentile in policy.items():
                lines.append(f"      {metric}: {percentile}")
            lines.append("    target_values:")
            for metric, target in targets.items():
                unit = distribution["metrics"][metric]["unit"]
                lines.append(f"      {metric}:")
                lines.append(f"        value: {fmt(target)}")
                lines.append(f"        unit: {yaml_scalar(unit)}")
            lines.append("    selected_event_values:")
            for metric in policy:
                unit = distribution["metrics"][metric]["unit"]
                lines.append(f"      {metric}:")
                lines.append(f"        value: {fmt(parse_number(row.get(metric)))}")
                lines.append(f"        unit: {yaml_scalar(unit)}")
            lines.extend(
                [
                    "    linked_claims:",
                    "      - CLAIM-CUTIN-SOTIF-001",
                    "      - CLAIM-CUTIN-TEST-001",
                ]
            )
            if case_type == "challenge":
                lines.append("      - CLAIM-CUTIN-RISK-001")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameter_distribution", type=Path)
    parser.add_argument("input_events_csv", type=Path)
    parser.add_argument("output_yaml", type=Path)
    parser.add_argument("--speed-bin", help="Optional comma-separated speed bins. Defaults to bins with at least 100 distribution rows.")
    parser.add_argument("--allow-review", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    distribution = load_json(args.parameter_distribution)
    speed_bins = select_speed_bins(distribution, args.speed_bin)
    write_cases(
        args.output_yaml,
        distribution,
        args.input_events_csv,
        speed_bins,
        args.allow_review,
    )
    print(f"Wrote {args.output_yaml} for speed bins {', '.join(speed_bins)}.")


if __name__ == "__main__":
    main()
