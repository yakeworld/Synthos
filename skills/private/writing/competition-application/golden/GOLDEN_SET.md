---
name: competition-application
description: GOLDEN_SET.md
---

# 金测集: competition-application

> 单一真理来源。技能核心：确认赛道后在申报书表格标记"√已选：XXX"，三层叙事（痛点-方案-成效）
> 填充 DOCX，关键数据必须从 `evolution-state.json` 实时提取（凡数必源）。
> 对应 SKILL.md 的 Genes COMP-001 ~ COMP-008 与 VERIFICATION 1-8。

## 测试用例

| ID | 描述 | 覆盖 Genes | 关键检查 | 权重 |
|----|------|-----------|---------|------|
| case_001 | 正常路径：公立医院临床科研实验室，三赛道待选，排除"数据基础设施"并标记"√已选"，三层叙事数据实时提取 | COMP-001/002/003/004/005/006/007/008 | 赛道排除+标记唯一；三层叙事数字与 state 逐项一致；合并单元格无扩散、无模板残留 | critical |
| case_002 | 错误路径：关键数据无法从 `evolution-state.json` 实时提取（score 字段缺失）→ 中断填充，禁止凭记忆/旧材料填写 | COMP-006 / Golden Error | 报"数据源不可用"并中断，绝不静默用历史值；无部分填充产出 | high |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（case_001 必须全绿）
- 错误路径（case_002）必须显式报错，任何静默回退历史值 / 部分填充均判失败
- 所有 JSON 可被 `python3 -c json.load` 解析（P0 证据可溯性：文件真实存在且结构合法）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（正常路径全链路） |
| high | 0.7 | 重要但不致命（错误路径处理正确性） |
| medium | 0.4 | 有价值但不是核心（辅助提示） |

## 验证方法（独立重算）

1. **数据源核验**：`python3 -c "import json; s=json.load(open('evolution-state.json')); print(s.get('cycle'), s.get('score'))"`
   取得 ground-truth，再与申报书内数字逐项比对（claimed == measured）。
2. **赛道标记唯一性**：在填充后 DOCX 全文检索 `√已选`，命中数必须 == 1。
3. **合并单元格扩散检查**：对每个被写入的合并单元格组，组内非锚点单元格不得携带相同长文本。
4. **模板残留检查**：全文检索 `（介绍参赛项目的背景`，命中数必须 == 0。
5. **段落索引核对**：长文本段落必须紧跟标题段落（打印全部段落确认 idx）。

## 文件清单

- `cases/case_001.json` — 正常路径输入
- `expected/case_001.json` — 正常路径期望输出与验证断言
- `cases/case_002.json` — 错误路径输入（score 字段缺失）
- `expected/case_002.json` — 错误路径期望报错与验证断言
