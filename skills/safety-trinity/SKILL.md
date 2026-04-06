---
name: safety-trinity
version: 1.0.0
description: "安全三支柱集成分析 — FuSa (ISO 26262) + SOTIF (ISO 21448) + Cybersecurity (ISO 21434) 的交叉映射与联合分析"
---

# 安全三支柱 | Safety Trinity

本技能打破FuSa/SOTIF/CyberSec三个标准的独立分析壁垒，提供交叉映射的统一分析流程。

## 为什么需要三合一？

传统做法：三个团队各做各的分析，最后开一个接口会议"对齐"。
问题：
- HARA识别的hazard可能被SOTIF触发条件放大
- TARA识别的攻击路径可能导致SOTIF功能不足
- 三个分析之间的交互效应被遗漏

## 交叉映射框架

```
FuSa HARA                    SOTIF触发条件              CyberSec TARA
(系统故障→危害)              (功能不足→危害)            (攻击→危害)
    │                            │                         │
    └──────────┬─────────────────┘─────────────────────────┘
               │
    ┌──────────┴──────────┐
    │   Unified Hazard     │
    │   统一危害分析        │
    │                      │
    │  Hazard H-001:       │
    │  ├─ FuSa: 雷达故障    │
    │  ├─ SOTIF: 雨雾漏检   │
    │  └─ Cyber: 雷达欺骗   │
    │                      │
    │  → 统一安全目标       │
    │  → 统一验证策略       │
    └─────────────────────┘
```

## 分析流程

### Step 1: 统一危害识别
- FuSa: 对每个功能做HARA（严重度S×暴露度E×可控性C → ASIL）
- SOTIF: 对每个功能做触发条件分析（感知局限×算法不足×人因误用）
- CyberSec: 对每个功能做TARA（资产→威胁→攻击路径→影响）
- **交叉**：检查三者识别的危害是否有重叠/放大效应

### Step 2: 统一安全目标
- 将三个来源的危害映射到统一的安全目标集合
- 标注每个安全目标的来源（FuSa/SOTIF/Cyber/Multiple）
- 优先处理多来源危害（更高风险）

### Step 3: 统一安全需求
- 功能安全需求（TSR/HSR）
- SOTIF安全需求（场景覆盖+残余风险可接受）
- 网络安全需求（安全机制+监测+响应）
- **交叉需求**：如"雷达欺骗检测"同时满足Cyber+SOTIF

### Step 4: 统一验证矩阵
- 测试场景同时覆盖FuSa故障注入 + SOTIF触发条件 + Cyber攻击场景
- 避免三套测试各跑一遍的资源浪费

## 使用示例

```
用户：我的AEB系统需要做完整的安全分析
输出：
1. 统一HARA表（含FuSa/SOTIF/Cyber三列来源标注）
2. 交叉危害清单（三个领域相互放大的危害）
3. 统一安全需求分解
4. 统一验证计划（合并三类测试场景）
```

## 参考标准
- ISO 26262:2018 Road vehicles — Functional safety
- ISO 21448:2022 Road vehicles — Safety of the intended functionality
- ISO/SAE 21434:2021 Road vehicles — Cybersecurity engineering
- ISO/TR 4804:2020 Safety and cybersecurity for automated driving systems
