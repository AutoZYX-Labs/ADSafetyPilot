---
name: dfm-query
version: 0.1.0
description: "驾驶员基础模型查询 — 基于DRIVEResearch航测数据，提供场景级中国驾驶员行为参数基线（DFM）"
---

# DFM 查询 | Driver Foundation Model Query

本技能基于驭研科技（DRIVEResearch）750h+航测自然驾驶数据集，提供中国驾驶员在特定场景下的行为参数分布基线。

## 概念

驾驶员基础模型（DFM）回答五个核心问题：
- **How**: 人类在这个场景下怎么开？→ 参考轨迹
- **What**: 合理范围是什么？→ 能力包络（P5-P95）
- **Where**: 哪里需要格外注意？→ 热点区域
- **When**: 什么触发了行为变化？→ 触发条件
- **Why**: 人类在意哪些信息？→ 关键环境线索

## 数据来源

- 采集方式：无人机航测（上帝视角，无遮挡）
- 数据规模：750h+ 飞行时数，10.5M+ 轨迹片段
- 覆盖范围：高速公路、城市道路、匝道、弯道、环岛、施工区、停车场、冰雪路面
- 数据网站：https://www.driveresearch.tech/

## 可查询参数

| 参数 | 说明 | 单位 |
|------|------|------|
| TTC | 碰撞时间 | s |
| THW | 车头时距 | s |
| DHW | 车头间距 | m |
| Lat_Acc | 横向加速度 | m/s^2 |
| Lon_Acc | 纵向加速度 | m/s^2 |
| Jerk | 加加速度 | m/s^3 |
| Speed | 车速 | km/h |
| Rel_Speed | 相对速度 | km/h |
| Lane_Offset | 车道偏移 | m |

## 输出格式

每个查询返回百分位值分布：
```json
{
  "scenario": "highway_cut_in",
  "matched_trajectories": 12847,
  "parameters": {
    "TTC": {"P5": 2.8, "P25": 4.1, "P50": 6.5, "P75": 10.2, "P95": 18.7, "unit": "s"},
    "THW": {"P5": 0.87, "P25": 1.21, "P50": 1.62, "P75": 2.15, "P95": 3.41, "unit": "s"},
    "Rel_Speed": {"P5": -35.2, "P25": -22.1, "P50": -15.3, "P75": -8.7, "P95": -2.1, "unit": "km/h"}
  },
  "sotif_notes": "P5 THW=0.87s significantly below ISO 22179 threshold of 1.2s"
}
```

## 状态

⚠️ **Phase 2 — 数据注入准备中**

当前为框架定义阶段。DRIVEResearch数据预计算完成后，将注入20个核心场景的行为基线数据。

## 使用示例

```
用户：高速公路匝道合流场景，主路车速100km/h，查询中国驾驶员行为基线
输出：
  场景匹配: Highway Merge (JAMA Annex C Type-2)
  匹配轨迹数: N（待注入）
  行为基线: TTC/THW/加速度 P5-P95分布
  SOTIF建议: 基于P5极端值的安全阈值建议
  与CCDM/RSS对比: 中国数据 vs 欧洲数据差异
```

## 参考文献
- Zhang, Y., Wang, C., & Shum, H. (2026). Benchmarking Autonomous Vehicles: A Driver Foundation Model Framework. CARS 2026.
