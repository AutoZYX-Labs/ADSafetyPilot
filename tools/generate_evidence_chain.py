#!/usr/bin/env python3
"""Generate an auditable evidence-chain manifest for an evidence pack."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARTIFACTS = [
    "scenario.yaml",
    "PARAMETER_DICTIONARY.md",
    "QUALITY_AND_COMPLIANCE.md",
    "input_events.csv",
    "input_events_summary.json",
    "parameter_distribution.json",
    "test_cases.yaml",
    "EVIDENCE_SUMMARY.md",
    "CUSTOMER_DEMO_SUMMARY.md",
    "safety_mapping.yaml",
    "evidence_sources.yaml",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_entry(pack_dir: Path, relative_path: str) -> dict[str, Any]:
    path = pack_dir / relative_path
    if not path.exists():
        return {
            "path": relative_path,
            "exists": False,
        }
    return {
        "path": relative_path,
        "exists": True,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def raw_package_entry(pack_dir: Path) -> dict[str, Any]:
    raw_dir = pack_dir / "raw"
    files = [
        path
        for path in sorted(raw_dir.glob("**/*"))
        if path.is_file() and path.name != ".DS_Store"
    ]
    suffix_counts = Counter(path.suffix.lower() or "<none>" for path in files)
    manifest_items = []
    for path in files:
        manifest_items.append(
            {
                "path": str(path.relative_to(pack_dir)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest_digest = hashlib.sha256(
        json.dumps(manifest_items, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "path": "raw",
        "file_count": len(files),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "manifest_sha256": manifest_digest,
    }


def build_manifest(pack_dir: Path, output_path: Path) -> None:
    manifest = {
        "pack_id": "ADSAFETY-EVP-CUTIN-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_status": "public_demo",
        "raw_package": raw_package_entry(pack_dir),
        "commands": [
            {
                "step": "import_raw_workbooks",
                "command": (
                    "python3 tools/import_cutin_scenarios.py "
                    "evidence-packs/cut-in-v0.1/raw/DRIVEResearch_expressway_1h_cutin_scenarios_20260416 "
                    "evidence-packs/cut-in-v0.1/input_events.csv "
                    "--summary-json evidence-packs/cut-in-v0.1/input_events_summary.json"
                ),
            },
            {
                "step": "compute_valid_distribution",
                "command": (
                    "python3 tools/compute_parameter_distribution.py "
                    "evidence-packs/cut-in-v0.1/input_events.csv "
                    "evidence-packs/cut-in-v0.1/parameter_distribution.json "
                    "--quality-filter valid"
                ),
            },
            {
                "step": "generate_test_cases",
                "command": (
                    "python3 tools/generate_cutin_test_cases.py "
                    "evidence-packs/cut-in-v0.1/parameter_distribution.json "
                    "evidence-packs/cut-in-v0.1/input_events.csv "
                    "evidence-packs/cut-in-v0.1/test_cases.yaml"
                ),
            },
            {
                "step": "generate_evidence_summary",
                "command": "python3 tools/generate_evidence_report.py evidence-packs/cut-in-v0.1",
            },
        ],
        "artifacts": [artifact_entry(pack_dir, path) for path in ARTIFACTS],
        "publication_policy": {
            "allowed_to_publish_values": True,
            "raw_package_committed": False,
            "raw_package_reason": "Raw workbooks are kept outside the public repository because of size and update cadence.",
        },
        "notes": [
            "This is one real extracted sample package, not a full highway cut-in ODD claim.",
            "Current parameters demonstrate the method and are not guaranteed to be converged.",
            "Current distributions are valid-only.",
            "Review rows remain in input_events.csv for audit but are excluded from parameter_distribution.json.",
        ],
    }
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output or args.pack_dir / "EVIDENCE_CHAIN.json"
    build_manifest(args.pack_dir, output_path)


if __name__ == "__main__":
    main()
