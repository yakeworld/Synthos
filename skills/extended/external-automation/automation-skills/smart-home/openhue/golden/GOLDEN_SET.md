---
name: openhue
description: Golden set — Philips Hue 灯光与场景控制（openhue CLI）
---

# 金测集 · openhue

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 输入/输出样本位于 `cases/` 与 `expected/`，一一对应。

## 测试用例

| ID | 场景 | 基因 | 关键检查 | case | expected |
|----|------|------|---------|------|----------|
| case_001 | 正常路径：睡前预设（房间调光 + 色温） | OPEN-003, OPEN-005 | 使用 `set room`（而非逐灯）；brightness 在 0-100；temperature 在 153-500 mirek；名称与 `get room` 精确一致 | `cases/case_001.json` | `expected/case_001.json` |
| case_002 | 错误路径：设置颜色到不支持彩色的白光灯泡 | OPEN-004 | 白光灯泡不支持 color/rgb → 命令失败或参数被拒绝；错误信息含上下文与恢复建议（先确认灯泡能力） | `cases/case_002.json` | `expected/case_002.json` |

## 覆盖的基因

- **OPEN-003** 氛围预设（亮度+色温组合） — case_001
- **OPEN-004** 颜色能力校验 — case_002
- **OPEN-005** 批量控制优先 `set room` / `set scene` — case_001

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 备注

- 参数合法区间：brightness ∈ [0, 100]；color temperature ∈ [153, 500] mirek。
- 房间/灯光名称区分大小写，执行 set 前应先 `openhue get room` / `openhue get light` 核对（OPEN-002）。
- Bridge 须与执行终端同处一个局域网；首次运行需物理按下 Bridge 按钮完成配对（OPEN-001）。
