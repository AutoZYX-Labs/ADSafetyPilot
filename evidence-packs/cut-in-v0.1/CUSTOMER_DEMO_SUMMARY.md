# Customer Demo Summary: Cut-in Evidence Pack v0.1

Generated at: `2026-05-19T13:57:43.804328+00:00`
Release status: public demo. Current data is one sample package; the listed parameters are not guaranteed to be converged.

## What this demonstrates

This evidence pack converts aerial naturalistic driving data into scenario parameter evidence for cut-in testing and safety analysis.

The demo chain is:

```text
extracted cut-in events -> valid-only parameter distribution -> convergence check -> evidence gap -> exemplar-matched test cases
```

## Data scope

| Item | Value |
|---|---:|
| Extracted cut-in events | 1389 |
| Valid rows used for distributions | 580 |
| Review rows retained for audit | 809 |
| Quality filter | `valid` |

Current ODD scope: urban expressway cut-in, congested traffic, one collection region. This is not a full highway cut-in ODD claim, and it should not be interpreted as final converged parameter evidence.

## Usable speed bins

| Speed bin | Distribution rows | Demo use |
|---|---:|---|
| `0-40` | 6 | evidence gap |
| `40-60` | 270 | show in demo |
| `60-80` | 294 | show in demo |
| `80-100` | 10 | evidence gap |

## Parameter evidence

| Metric | Unit | Speed bin | P10 | P50 | P95 |
|---|---:|---|---:|---:|---:|
| Ego speed | km/h | `40-60` | 48.142 | 55.251 | 59.187 |
| Ego speed | km/h | `60-80` | 61.518 | 66.612 | 76.352 |
| Longitudinal gap | m | `40-60` | 11.544 | 35.706 | 121.7 |
| Longitudinal gap | m | `60-80` | 17.34 | 48.877 | 146.596 |
| Lateral speed | m/s | `40-60` | 0.167 | 0.397 | 0.782 |
| Lateral speed | m/s | `60-80` | 0.111 | 0.425 | 0.865 |
| Cut-in duration | s | `40-60` | 16.016 | 19.467 | 25.1 |
| Cut-in duration | s | `60-80` | 14.41 | 17.233 | 22.737 |
| Minimum TTC | s | `40-60` | 7.632 | 18.995 | 83.911 |
| Minimum TTC | s | `60-80` | 7.421 | 15.938 | 64.922 |
| Reference THW | s | `40-60` | 0.744 | 2.497 | 7.975 |
| Reference THW | s | `60-80` | 0.924 | 2.686 | 7.902 |

## Evidence gaps to be transparent about

- Low-sample bins are not used for percentile claims.
- Review rows are retained for audit but excluded from current distributions.
- Reference-frame TTC has substantial missingness in the full import; public interpretation should use the documented valid-only distribution unless the missingness is resolved.
- Workbook keyframe naming must be reconciled with legacy T1/T2 wording before formal engineering use.

## Demo positioning

This is not an AI-generated compliance table. It is a reproducible data evidence pack that can feed SOTIF trigger analysis, scenario representativeness claims, and test-case generation.
