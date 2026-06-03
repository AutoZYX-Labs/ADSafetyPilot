# Feishu DRIVEResearch Tool Development Extract

Date: 2026-05-15

Source root:

- Feishu wiki: https://adsafety-yytcc.feishu.cn/wiki/YQwmwL85WiHREJkfPlycMbiOn2d
- Root title: 无人机创新技术应用
- Wiki node count crawled: 66
- Relevant docx pages fetched: 58
- Sheets under admin/finance were listed but not extracted.

Scope:

This note extracts information useful for ADSafetyPilot and the Scenario-to-Evidence Copilot direction. It intentionally excludes administrative and finance details unless they affect product packaging or delivery logic.

## High-Value Source Pages

Core strategy and product direction:

- 2026H1 OKR&会议纪要
- ScenarioDataCenter?
- scenario.center @ ika
- 航测数据集自动化构建链路
- 航测新架构
- 航测链路TODOs

Data products and customer-facing materials:

- 航测自然交通流轨迹数据产品和服务
- 航测自然交通流轨迹数据格式与精度
- 自然交通流数据产品特征精度验证方案
- 泛亚自然驾驶数据需求分析及应对
- DRIVEResearch 数据分类统计 V1.0
- Data Portfolio of DRIVEResearch
- DRIVEResearch Sample Data Introduction
- 数据出境情况调研

Scenario extraction and simulation:

- 0. ZYT航测需求管理
- 1. 危险场景指标提取
- 2. 典型场景定义
- 3. 基于航测数据生成端到端仿真场景
- 4. DRIVEResearch 场景文件格式说明
- 高速公路典型驾驶场景提取与参数分析
- 基于航测数据的场景簇提取与自动驾驶测试训练技术方案

Research and institutional use cases:

- 项目研究规划V2—基于讨论纪要更新
- JAMA V4 Annex D 对北京基金项目的参考价值
- 面向智能驾驶拟人化测评的自然驾驶数据方案建议

## Strategic Takeaways

The Feishu materials strongly support the current ADSafetyPilot positioning:

- DRIVEResearch is not only a data vendor. The stronger product is a data-backed safety evidence tool.
- The useful chain is `trajectory data -> scenario extraction -> parameter distribution -> convergence check -> safety boundary -> test cases -> OpenX/simulation -> evidence report`.
- Customer needs from PATAC, ZYT, CATARC, fka and 51Sim converge around the same primitives: data catalog, scenario labels, behavior extraction, percentile distributions, quality evidence and simulation handoff.
- The strongest moat is the connection between real Chinese traffic behavior and safety claims, not generic AI form filling.

## Data Asset Facts To Reuse

Most recent internal portfolio claims:

- `800+` hours of aerial survey video.
- `10.5M+` traffic participant trajectories.
- `10+` cities, `50+` collection locations, `4+` road types.
- 4K, 30 fps aerial videos.
- Reported data quality targets include `MOTA >= 0.85` and trajectory usable rate `>= 90%`.
- Output fields include position, speed, acceleration, heading, yaw rate, vehicle dimensions, lane id, lateral offset, TTC and THW.

Older customer-facing material states `600+` hours as of 2025-10-15. For new public-facing or proposal materials, use the `800+ / 10.5M+` claim unless a newer authoritative dashboard is found.

## Data Format Requirements

The base trajectory data folder should be treated as a first-class data product with:

- `recordingMeta.csv`: video-level metadata.
- `tracksMeta.csv`: trajectory-level metadata.
- `tracks.csv`: frame-level trajectory data.
- Road images: raw/static map image, lane image, grayscale or processed map images.
- OpenDRIVE map when available.

The `tracks.csv` file is the main source for scenario extraction. It contains per-frame per-vehicle state and interaction features. For ADSafetyPilot this implies two layers:

- Raw trajectory layer: frame-level data, suitable for extraction and replay.
- Event layer: one row per extracted scenario event, suitable for evidence packs and percentile statistics.

The current `cut-in-v0.1` evidence pack should continue to request event-level CSV first, while keeping a converter path from raw `Scenario.xlsx` or `tracks.csv`.

## Metadata And Label Schema

PATAC demand analysis shows the current `recordingMeta.csv` labels are not enough. The product needs a richer metadata schema.

Required label dimensions:

- `city`
- `road_type`: freeway, expressway, national road, provincial road, city main road, intersection, roundabout, parking lot, etc.
- `road_section_type`: straight, ramp merge, ramp diverge, curve, slope, toll station, construction area, etc.
- `weekday`
- `is_holiday`
- `start_time`
- `duration_s`
- `weather`
- `temporary_event`
- `has_special_vehicle`
- `straight_lane_count`
- `intersection_lane_count`
- `intersection_entrance_count`
- `has_traffic_light`
- `has_diagonal_zebra_crossing`
- `is_abnormal_intersection`
- `roundabout_lane_count`
- `roundabout_entrance_count`

The newer tag appendix aligns with ISO 45312 / ODD thinking and can be mapped into five groups:

- Top-level road scene.
- Static road environment.
- Traffic facilities.
- Dynamic elements.
- Atmospheric and lighting environment.

Implementation implication:

- Add a shared `metadata.schema.json` later.
- Evidence packs should reference both `recording_id` and `event_id`.
- Every parameter distribution should be filterable by metadata labels.

## Scenario Taxonomy

Priority scenarios recurring across pages:

- Cut-in.
- Cut-out.
- Front vehicle deceleration.
- Stop and Go.
- Dangerous lane change by ego.
- Stable following.
- Ramp merge.
- Roundabout driving.
- Green-light start.
- Red-light deceleration and stop.
- Curve passing.
- VRU crossing.
- Unprotected left turn and other intersection interactions.
- Parking lot cruising, park-in and park-out.

For current MVP, keep the order:

1. Cut-in.
2. Cut-out.
3. Front vehicle deceleration.
4. Stop and Go or stable following, depending on downloaded files.

## Cut-In Evidence Facts

The linked page `高速公路典型驾驶场景提取与参数分析` gives the most useful cut-in evidence source:

- Collection site: Changchun ring expressway, Songyuan / Changchun North exit.
- Flight height: 200 m.
- Video duration collected: 60+ h.
- Quality-checked extraction set: 50 h.
- Scenario counts before and after location filtering:
  - CutIn: `5832 -> 4491`
  - CutOut: `1319 -> 915`
  - Deceleration: `36 -> 22`

The same page defines the extraction chain:

`raw video -> stabilization/reference alignment -> detection and tracking -> trajectory post-processing -> map matching and neighbor relationships -> trajectory visualization -> scenario extraction -> web review`

The page also defines a convergence check:

- Split the event data into 20 portions.
- Accumulate from 5% to 100%.
- At each step compute `P10`, median and mean.
- Use the last five `P10` values, corresponding to 80%-100% data.
- Relative fluctuation below 5% means converged.
- Reported conclusion: CutIn converges in the 60-120 km/h speed range.

For ADSafetyPilot, this should become a `convergence_check` output next to `parameter_distribution.json`.

## Parameter Distribution Rules

PATAC convergence plan:

- Focus on Chinese structured roads: freeway and city expressway.
- Four ISO 34502 style scenarios are the initial scope.
- Each speed bin should output `P5 / P25 / P50 / P75 / P95`.
- Scenario count, not video hours, directly determines convergence.
- Convergence target: each `scenario x speed_bin` has at least `500` extracted events.
- After new samples are added, percentile changes should be below `5%`.
- A convergence status matrix should be generated after each city is processed.

ZYT dangerous scenario page uses a related but not identical thresholding logic:

- It uses the 5th percentile as a human driving boundary.
- Initial speed bins are `0-20`, `20-80`, `80-120`, then expanded in tables to `0-20`, `20-40`, `40-60`, `60-80`, `80-100`, `100-120`.
- Candidate indicators:
  - TTC.
  - THW.
  - ACT.
- Preliminary thresholds in that page:
  - Front vehicle deceleration: TTC `3.3 s`, THW `0.65 s`.
  - Cut-in: ACT `2 s`, THW `0.35 s`.
  - Ego dangerous lane change: ACT `2 s`, THW `0.35 s`.
  - Cut-out: TTC `3.3 s`, THW `0.65 s`.

Note:

These thresholds are marked as preliminary and require sample-basis evidence. They should not be hard-coded as normative thresholds; treat them as customer-provided candidate thresholds with evidence status `draft`.

## Scenario File Package

The DRIVEResearch scenario package should be treated as a reusable import target:

- `Scenario.xlsx`: behavior scenario file with ego and traffic vehicle trajectories plus feature indicators.
- `map.jpg`: aerial scene image.
- `lanes.png`: lane id and lane boundary image.
- `openDRIVE.xodr`: OpenDRIVE map.
- `ScenarioVISU.png`: behavior process visualization.

`Scenario.xlsx` contains:

- `ego_veh` sheet.
- `traffic_veh` sheet.
- `Feature` sheet.

Implementation implication:

- Add an importer that can read `Scenario.xlsx` and convert it to event-level `input_events.csv`.
- Preserve links to map and OpenDRIVE files in evidence metadata.

## OpenX And Simulation Chain

The ZYT simulation page shows a chain that is already partially working:

- 30 Hz to 20 Hz data conversion by interpolation.
- OpenSCENARIO generation using templates.
- Coordinate conversion is required.
- Excel and OpenX coordinate conventions differ; y axis inversion and heading-angle offset were identified and solved.
- Batch workflow exists for generating scenario files and running simulator cases.
- 100 scenes currently take about 50 minutes to run.
- Output comparison includes simulator video, real reference image and error data workbook.

Implementation implication:

- OpenX export should not be the first milestone for `cut-in-v0.1`, but it is the natural next module after event statistics.
- Evidence packs should reserve an `openx_export` section with status fields: `not_started`, `generated`, `simulated`, `validated`.

## Quality And Compliance Evidence

Trajectory quality evidence available in documents:

- Position accuracy within 15 cm when UAV hover height is within 200 m.
- Speed accuracy within 0.3 m/s.
- Real vehicle validation against RT-range inertial navigation reports deviation within 3%.
- Quality validation dimensions include classification accuracy, detection quality, tracking stability, map matching and pixel-to-distance conversion.
- Metrics mentioned include MOTA, RMSE and accuracy.

Data compliance and desensitization:

- Avoid geographic information, surrounding facilities and sensitive infrastructure details.
- Lane abstraction and geographic masking are recommended.
- Raw video metadata may contain GPS, time and device information and should be stripped before external transfer.
- For overseas transfer, geographic and sensitive infrastructure information is the highest-risk dimension.

Implementation implication:

- Evidence packs need a `quality_claims` section and a `data_compliance` section.
- For external/customer reports, raw geolocation should be replaced by abstract labels unless the contract permits disclosure.

## Preventability And Safety Evidence Model

The road safety collaboration materials provide a strong extension beyond ordinary parameter reports:

- Use accident / near-miss data to answer what scenarios matter.
- Use aerial NDD data to answer how normal humans behave in those scenarios.
- Compare accident parameters with NDD behavior distributions to define a preventability index.

Proposed PI logic:

- `PI-A`: accident parameters are outside normal NDD distribution, beyond P25. Normal drivers usually avoid it. AD should pass.
- `PI-B`: accident parameters are near distribution edge, P5-P25. Good drivers may avoid it. AD should attempt to avoid.
- `PI-C`: accident parameters are within the extreme tail, below P5. Normal humans also struggle. Use as pressure test.

Implementation implication:

- This can become `preventability_assessment.yaml` later.
- It should not block the cut-in v0.1 pack, but it is the right medium-term differentiator.

## Mapping To ADSafetyPilot Modules

Near-term modules:

1. Data catalog and metadata schema.
2. Scenario package importer.
3. Event-level scenario schema.
4. Parameter distribution generator.
5. Convergence checker.
6. Evidence gap report.
7. Customer-facing evidence pack export.

Next modules:

1. Scenario threshold review.
2. Data quality claim registry.
3. Compliance/desensitization checklist.
4. OpenX exporter.
5. Simulation validation registry.
6. Preventability index.
7. AI query layer over evidence packs.

## Changes Needed In Current Cut-In v0.1 Pack

Add to current schemas or future schema backlog:

- `recording_id`
- `event_id`
- `source_package`
- `road_section_type`
- `lane_marking_type`
- `traffic_condition`
- `collection_city`
- `collection_time_period`
- `weather`
- `lighting`
- `data_quality_status`
- `review_status`
- `scenario_count_before_filter`
- `scenario_count_after_filter`
- `convergence_status`
- `openx_export_status`

Add to `compute_parameter_distribution.py` later:

- Support P10, because existing cut-in analysis uses P10 for convergence.
- Generate convergence status by speed bin.
- Accept configurable speed bins.
- Accept metadata filters.

## Immediate Next Work After Data Download

When the Baidu package is local:

1. Inspect whether it contains `Scenario.xlsx`, raw `tracks.csv`, or both.
2. If `Scenario.xlsx` exists, identify `ego_veh`, `traffic_veh` and `Feature` sheets.
3. Convert the smallest cut-in batch into `input_events.csv`.
4. Run percentile generation for `ttc_s`, `thw_s`, `ego_speed_kmh`, `cutin_speed_kmh`, `longitudinal_gap_m`, `lateral_speed_mps` and `cutin_duration_s`.
5. Add convergence output using `P10` and the 80%-100% fluctuation rule.
6. Update `test_cases.yaml` with values from real percentiles, not invented numbers.

## Extraction Limitations

- One directory-level docx page under `全威：技术顾问（欧洲/德国）` returned a fetch error. Its child pages were fetched successfully.
- Embedded sheets were not expanded in this pass. Several important details, especially exact column definitions, may be inside sheet tokens and should be fetched later if needed.
- Attached files were not downloaded. Some scripts and sample workbooks referenced in Feishu may be useful later, but current priority is the Baidu scenario package.
