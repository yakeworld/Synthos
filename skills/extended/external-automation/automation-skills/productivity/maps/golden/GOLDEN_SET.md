---
name: maps
description: GOLDEN_SET.md
---

# 金测集: maps

> 地理编码/POI/路径/时区技能的标准测试用例集。覆盖正常地理编码、
> 区域歧义错误路径、区域 POI 查询。每个用例有明确的"通过"标准。

## 技能定位

`maps` 基于 OpenStreetMap/Nominatim、Overpass API、OSRM、TimeAPI.io
提供 8 个命令：search / reverse / nearby / distance / directions / timezone / area / bbox。
零依赖（Python stdlib only），无需 API key。

输入 `query: str`（地点名/坐标/POI 类别等），
输出 `geo_data: dict`（经纬度/地址/POI 列表/路线/时区等）。

## 测试用例

| ID | 文件 | 描述 | 关键检查 | 权重 |
|----|------|------|---------|------|
| case_001 | `cases/case_001.json` | 地理编码"Statue of Liberty"（正常路径） | 返回 lat ~40.689、lon ~-74.044 | critical |
| case_002 | `cases/case_002.json` | nearby 仅给邮编"90210"无上下文（全球歧义失败路径） | 返回歧义提示，要求补充国家/州；不返回空或错误坐标 | critical |
| case_003 | `cases/case_003.json` | area + bbox 区域 POI 查询（正常路径） | 先 area 取边界框再 bbox 搜索；请求频率 ≤1 req/s | high |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- `search` 基准通过："Statue of Liberty" 返回 lat ~40.689、lon ~-74.044
- `nearby` 调用提供了 lat/lon 或 `--near` 之一
- 全球歧义输入（仅邮编/通用名）已补充国家/州
- `distance`/`directions` 目的地使用 `--to` 标志并指定出行模式
- 区域 POI 查询先 `area` 获取边界框再调 `bbox`
- 请求频率 ≤1 req/s（Nominatim ToS）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 与 SKILL.md 验证清单的映射

- `search` 基准通过 → case_001
- `nearby` 基准通过 → case_002（歧义路径）
- `nearby` 调用提供了 lat/lon 或 `--near` 之一 → case_002
- 全球歧义输入已补充国家/州 → case_002
- `distance`/`directions` 目的地使用 `--to` 标志 → case_003
- 区域 POI 查询先 `area` 再 `bbox` → case_003
- 请求频率 ≤1 req/s → case_003
