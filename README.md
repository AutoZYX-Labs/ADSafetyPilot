<p align="center">
  <strong>ADSafetyPilot</strong><br>
  智能驾驶安全开发助手 | AI-Powered AD Safety Engineering Copilot
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" /></a>
  <a href="https://adsafetypilot.autozyx.com"><img src="https://img.shields.io/badge/Website-adsafetypilot.autozyx.com-green" alt="Website" /></a>
  <a href="https://github.com/AutoZYX/ADSafetyPilot"><img src="https://img.shields.io/badge/GitHub-AutoZYX-181717?logo=github" alt="GitHub" /></a>
</p>

---

## What is ADSafetyPilot?

ADSafetyPilot is a domain-specific AI copilot for **autonomous driving safety engineering**. It combines:

- **Safety Knowledge Engine**: Deep expertise in FuSa (ISO 26262), SOTIF (ISO 21448), and Cybersecurity (ISO 21434) — with a unique "Safety Trinity" integrated analysis approach
- **China Regulatory Intelligence**: Full coverage of Chinese mandatory standards (GB 44495/44496, ADAS Safety Requirements) and development practices
- **DFM Data Engine**: Scenario-specific human driving behavior baselines derived from 800h+ aerial naturalistic driving data (10.5M+ trajectories) via [DRIVEResearch](https://www.driveresearch.tech/)
- **Scenario Library**: Standardized test scenarios aligned with JAMA V4.0 framework and Chinese L2/L3 mandatory standards

## Architecture

```
ADSafetyPilot
├── skills/              # AI Skills (Claude Code compatible)
│   ├── sotif-deep/      # ISO 21448 full lifecycle
│   ├── china-regulatory/# Chinese standards & practices
│   ├── safety-trinity/  # FuSa + SOTIF + CyberSec integrated
│   └── dfm-query/       # Driver Foundation Model queries
├── scenarios/           # Standardized scenario library
│   ├── jama-v4/         # JAMA V4.0 complete scenario set
│   ├── china-l2-adas/   # Chinese L2 ADAS mandatory test scenarios
│   ├── china-l3-ads/    # GB 44495 L3 scenarios
│   └── china-parking/   # GB 44496 parking scenarios
├── evidence-packs/      # Scenario-to-evidence product packages
│   └── cut-in-v0.1/     # First reusable Scenario Evidence Pack
├── schemas/             # Evidence pack JSON schemas
├── tools/               # Data processing and report generation tools
├── knowledge-base/      # Curated standards & references
│   ├── standards/       # ISO/GB/SAE standards index
│   ├── projects/        # PEGASUS, ENABLE-S3, SAKURA, PAXAS
│   └── best-practices/  # Industry best practices
├── data/                # DFM behavioral baselines
│   ├── dfm-baselines/   # Human driving parameter distributions
│   └── scenario-params/ # Scenario-specific parameters (P5-P95)
└── website/             # Project website (GitHub Pages)
```

## Core Capabilities

### 1. Safety Trinity Analysis
Integrated FuSa + SOTIF + Cybersecurity analysis — not three separate silos:
```
Input:  "ACC function, highway ODD, 60-120km/h"
Output: HARA table + Triggering Conditions + TARA threats
        with cross-references between all three
```

### 2. Chinese Regulatory Compliance
```
Input:  "Check my L2 ADAS system against Chinese mandatory standards"
Output: Gap analysis against GB ADAS Safety Requirements
        + Required test scenarios with pass/fail criteria
```

### 3. Scenario Evidence Packs
```
Input:  "Event-level cut-in data from DRIVEResearch"
Output: Parameter distributions by speed bin:
        P5 / P25 / P50 / P75 / P95 for TTC, THW, gap, speed, lateral speed
        + SOTIF trigger-condition support
        + test case candidates
        + evidence gaps
```

The first reusable pack is [cut-in-v0.1](evidence-packs/cut-in-v0.1/README.md). It is designed to turn what used to be a one-off analysis report into a repeatable data evidence package.

A bilingual web presentation is available at [docs/evidence/cut-in-v01.html](docs/evidence/cut-in-v01.html) for customer-facing explanation of the evidence-pack value, data scope, outputs, and limitations.

### 4. Scenario-Driven Test Planning
```
Input:  "Generate SOTIF validation plan for AEB function"
Output: Test scenarios from JAMA V4.0 + Chinese standards
        with parameterized test cases and acceptance criteria
```

## Relationship to Automotive Claude Code Agents

ADSafetyPilot is designed to complement [automotive-claude-code-agents](https://github.com/theja0473/automotive-claude-code-agents) — a comprehensive AI copilot for the full automotive engineering stack (221 domain agents, 4600+ skills).

| | automotive-claude-code-agents | ADSafetyPilot |
|---|---|---|
| **Scope** | Full automotive stack (ADAS to cloud) | Safety engineering (deep & narrow) |
| **Differentiator** | Breadth of domain coverage | Depth of safety expertise + real data |
| **Data** | Standards knowledge only | Standards + naturalistic driving data |
| **China** | Basic coverage | Deep regulatory intelligence |
| **Use together** | General engineering tasks | Safety-specific analysis & validation |

## Quick Start

```bash
# Clone
git clone https://github.com/AutoZYX/ADSafetyPilot.git
cd ADSafetyPilot

# Use with Claude Code (skills are directly compatible)
claude "Using ADSafetyPilot, analyze SOTIF risks for my AEB system"

# Or use standalone
claude "Generate HARA table for ACC function on Chinese highways"
```

## Roadmap

- [x] Phase 1: Safety Knowledge Engine (SOTIF + FuSa + CyberSec skills)
- [x] Phase 1: China Regulatory Intelligence (GB standards coverage)
- [ ] Phase 2: Scenario Library (JAMA V4.0 + Chinese standard scenarios)
- [ ] Phase 2: DFM Behavioral Baselines (20 core scenarios)
- [ ] Phase 3: Web interface & documentation site
- [ ] Phase 3: OpenSCENARIO scenario generation

## Author

**Yuxin Zhang** (张玉新)
- Associate Professor, Jilin University | Functional Safety Lead, ZHUOYU Technology | Founder, [DRIVEResearch](https://www.driveresearch.tech/)
- Visiting Scholar, Newcastle University, UK
- Research: SOTIF, Functional Safety, Scenario-driven V&V

## License

MIT License. See [LICENSE](LICENSE) for details.
