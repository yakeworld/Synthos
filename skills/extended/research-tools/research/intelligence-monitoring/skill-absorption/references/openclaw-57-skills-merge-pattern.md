# OpenClaw 57 Skills Merge Pattern

> 吸收日期: 2026-06-05
> 源: openclaw/openclaw (376,897⭐, MIT)
> 类型: 大规模并行技能库吸收模式

## 模式概述

当外部项目包含 **50+ 个并行技能目录**（每个有 SKILL.md），且与 Synthos 有显著重叠但仍有大量新技能时：

1. **列出所有技能名称** — 从 `repo/skills/` 目录获取
2. **与 Synthos 技能列表对比** — `find skills/ -maxdepth 1 -type d`
3. **分类**: overlaps (同名), new (不在 Synthos), unique-oc (仅存在于 OpenClaw)
4. **对 overlaps**: 比较文件大小/内容完整度，决定 KEEP vs MERGE
5. **对 new**: 直接导入，归一化格式
6. **记录**: 吸收报告 + 决策表

## 合并决策规则

| 场景 | 规则 | 示例 |
|:-----|:-----|:-----|
| Synthos >> OpenClaw (>3x) | KEEP Synthos | blogwatcher: 5391B vs 1414B |
| OpenClaw >> Synthos (>5x) | MERGE OpenClaw→Synthos | node-inspect-debugger: 246B vs 3573B |
| 相当大小 | 保留更完整者 (人工判断) | notion: 5536B vs 3864B |
| 不存在 | 直接导入 + 归一化 | 51 new skills |

## 归一化步骤

1. 添加 YAML frontmatter (name, description, license, metadata, allowed-tools)
2. 确认原理层·文言、方法层·白话、触发条件、验证清单结构
3. 统一 allowed-tools 列表
4. 统一 metadata.synthos 字段
5. 检查并修复引用格式

## 验证清单

- [ ] 57 个技能全部被处理 (不遗漏)
- [ ] 重叠技能已决策 (KEEP/MERGE)
- [ ] 新技能已导入
- [ ] 格式已归一化
- [ ] 吸收报告已写入
- [ ] absorption-ledger.json 已更新 (统一台账: /media/yakeworld/sda2/Synthos/absorption-ledger.json)
