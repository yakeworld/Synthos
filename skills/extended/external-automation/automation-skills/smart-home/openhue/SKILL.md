---
name: openhue
description: openhue
version: 1.0.0
category: devops
signature: 'openhue -> devops: Control Philips Hue lights and scenes via a Hue Bridge
  from the terminal.'
related_skills:
- smart-home
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills: []
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# OpenHue CLI

Control Philips Hue lights and scenes via a Hue Bridge from the terminal.

## Prerequisites

```bash
# Linux (pre-built binary)
curl -sL https://github.com/openhue/openhue-cli/releases/latest/download/openhue-linux-amd64 -o ~/.local/bin/openhue && chmod +x ~/.local/bin/openhue

# macOS
brew install openhue/cli/openhue-cli
```

First run requires pressing the button on your Hue Bridge to pair. The bridge must be on the same local network.

## When to Use

- "Turn on/off the lights"
- "Dim the living room lights"
- "Set a scene" or "movie mode"
- Controlling specific Hue rooms, zones, or individual bulbs
- Adjusting brightness, color, or color temperature

## Common Commands

### List Resources

```bash
openhue get light       # List all lights
openhue get room        # List all rooms
openhue get scene       # List all scenes
```

### Control Lights

```bash
# Turn on/off
openhue set light "Bedroom Lamp" --on
openhue set light "Bedroom Lamp" --off

# Brightness (0-100)
openhue set light "Bedroom Lamp" --on --brightness 50

# Color temperature (warm to cool: 153-500 mirek)
openhue set light "Bedroom Lamp" --on --temperature 300

# Color (by name or hex)
openhue set light "Bedroom Lamp" --on --color red
openhue set light "Bedroom Lamp" --on --rgb "#FF5500"
```

### Control Rooms

```bash
# Turn off entire room
openhue set room "Bedroom" --off

# Set room brightness
openhue set room "Bedroom" --on --brightness 30
```

### Scenes

```bash
openhue set scene "Relax" --room "Bedroom"
openhue set scene "Concentrate" --room "Office"
```

## Quick Presets

```bash
# Bedtime (dim warm)
openhue set room "Bedroom" --on --brightness 20 --temperature 450

# Work mode (bright cool)
openhue set room "Office" --on --brightness 100 --temperature 250

# Movie mode (dim)
openhue set room "Living Room" --on --brightness 10

# Everything off
openhue set room "Bedroom" --off
openhue set room "Office" --off
openhue set room "Living Room" --off
```

## Notes

- Bridge must be on the same local network as the machine running Hermes
- First run requires physically pressing the button on the Hue Bridge to authorize
- Colors only work on color-capable bulbs (not white-only models)
- Light and room names are case-sensitive — use `openhue get light` to check exact names
- Works great with cron jobs for scheduled lighting (e.g. dim at bedtime, bright at wake)

## 验证清单 · VERIFICATION

- [ ] `openhue get light` / `openhue get room` 能列出资源，且所用名称区分大小写、与命令中一致
- [ ] Hue Bridge 与执行终端处于同一局域网；首次运行已按下 Bridge 按钮完成配对
- [ ] 亮度值在 0–100 区间，色温值在 153–500 mirek 区间
- [ ] 设置颜色/RGB 前已确认目标灯泡支持彩色（白光灯泡仅支持开关/亮度/色温）
- [ ] 批量控制或场景切换优先使用 `set room` / `set scene`，而非逐个灯泡操作
- [ ] 定时场景（如 cron 定时调光）已验证在无交互环境下可正常执行

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Openhue

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[OPEN-008]** 首次连接或网络环境变更 → 必须确保 Hue Bridge 与执行终端在同一局域网，并物理按下 Bridge 按钮完成配对授权
- **[OPEN-009]** 控制特定灯光或房间时 → 必须先执行 `openhue get light` 或 `openhue get room` 获取精确名称，因为名称区分大小写
- **[OPEN-010]** 需要调整灯光氛围（如睡前、工作、观影） → 使用预设组合参数（亮度+色温）而非单一开关，例如睡前设为低亮度高色温（450mirek）
- **[OPEN-011]** 尝试设置颜色（Color/RGB）时 → 需确认目标灯泡支持彩色功能，白光灯泡仅支持开关和亮度/色温调整
- **[OPEN-012]** 需要批量控制或自动化场景 → 优先使用 `openhue set room` 或 `openhue set scene` 命令，避免逐个控制灯泡以提高效率
- **[OPEN-013]** 执行定时任务（如定时关灯/调光） → 将 openhue 命令集成到 cron jobs 中，利用其无状态 CLI 特性实现自动化照明
