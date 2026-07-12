---
name: quality-gate
category: core
signature: "quality-gate -> core: 四层质量架构，固定流程强制执行"
description: P0 质量闸门。四层架构：L0动灵层 → L0.5数据诚实门 → G1-G7管线门 → L4内容评审。固定模板，零自由发挥。
author: Synthos
license: MIT
version: 3.1.0
priority: P0
entrypoint_type: cognitive
entrypoint_cmd: "检查D8≥80%, D10a≥90%, 0 undefined citation"
entrypoint_desc: "质量闸门。输入: paper_dir, 输出: gate_result"
metadata:
  synthos:
    priority: P0
    atom_type: meta-component
    description: 质量闸门 — 强制固定流程，不靠Agent自行判断。
    signature: "paper_dir: str -> quality_report: dict"
    related_skills: ['knowledge-extraction', 'paper-pipeline']
---

# Quality Gate — 质量闸门

> 一次一件事，达标才停。不达标→循环修复。无 skill_view 记录=门不通过。

## 执行步骤（固定流程）
## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

### Step 1: 确定论文目录

输入：论文目录路径（含 `paper.tex`）。
- 从 `outputs/papers/` 目录查找
- 从用户输入提取
- 从 `pipeline_trace.json` 获取

### Step 2: 运行质量检查引擎

```bash
cd /media/yakeworld/sda2/Synthos/skills/core/quality-gate/scripts/

# 完整模式（G1-G7 + L0.5）
python3 quality-gate-runner.py \
    --paper-dir "{paper_dir}" \
    --output "{output_dir}/quality_report.json" \
    --mode full

# 快速模式（仅 G1+G2+L0.5，预检）
python3 quality-gate-runner.py \
    --paper-dir "{paper_dir}" \
    --output "{output_dir}/quality_report_fast.json" \
    --mode fast
```

### Step 3: 解析报告

从 `quality_report.json` 读取：
- `overall_score` — 总体评分
- `overall_pass` — 是否通过（≥0.85）
- `gates` — 每门详细结果
- `issues` — 问题清单

**判定**：
- `overall_score` ≥ 0.85 且 `overall_pass` = true → 通过
- `L0.5_data_honesty` score < 0.5 → 一票否决，必须修复
- 任何 P0 问题（G4_constitution, L0.5）→ 必须修复

### Step 4: 生成报告

按固定模板生成报告，使用 `refs/comprehensive-quality-report-template.md`：

```bash
# 将 quality_report.json 加载，按模板输出 Markdown 报告
# 模板：报告一（通用六域）+ 报告二（类型专项）+ 报告三（引用审查）+ 报告四（检查员报告）
```

**如果 quality-gate-runner.py 输出 JSON 符合模板结构，直接转换输出。**

### Step 5: 修复循环（如未通过）

1. 按 severity 排序 issues（P0 → P1 → P2）
2. 对每个问题，参考 `refs/quality-gate-fix-recipes.md` 获取修复方案
3. 执行修复（patch paper.tex / 清理 bib / 重编译）
4. 重编译验证：
   ```bash
   cd {paper_dir}
   pdflatex paper.tex 2>&1 | grep -c "Error"  # = 0
   pdflatex paper.tex 2>&1 | grep -c "Overfull"  # = 0
   ```
5. 重新运行 Step 2-4
6. 连续 3 次未通过 → 报告"需要人工介入"

### Step 6: 输出交付

将最终报告保存为 `{paper_dir}/quality-report.md`，更新 `{paper_dir}/state.json` 的 quality_score 字段。

## 闸门清单

| 门 | 名称 | 阈值 | 一票否决 | 说明 |
|:---|:-----|:----:|:--------:|:-----|
| G1 | 身份 | — | ❌ | AGENT_MANIFEST.yaml 存在且有效 |
| G2 | 编译 | — | ❌ | .tex 语法合法，编译通过 |
| G3 | 引用完整 | 0.8 | ❌ | cite{} 与 bibitem 匹配率 ≥80% |
| G4 | 宪法合规 | 1.0 | ✅ | 无硬编码凭证，不违宪法 |
| G5 | 引用质量 | 0.8 | ❌ | 引用功能分类，恰当率 ≥80% |
| G6 | 影响映射 | 0.6 | ❌ | 方法论已描述 |
| G7 | 内容评审 | 0.6 | ❌ | 结构完整性（Intro/Methods/Results/Discussion） |
| L0.5 | 数据诚实 | 0.5 | ✅ | 数值声明有源可追溯 |

**通过条件**：所有门 score ≥ 阈值 且 无 P0 问题

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|:-----|:-----|:----:|:-----|
| paper_dir | string | ✅ | 论文目录路径 |
| mode | string | ❌ | `full`（默认）或 `fast` |

## 输出契约

```json
{
  "paper_dir": "/path/to/paper",
  "paper_name": "paper-name",
  "overall_pass": true,
  "overall_score": 0.92,
  "gates": {
    "G1_identity": {"gate": "G1_identity", "pass": true, "score": 1.0},
    "L0.5_data_honesty": {"gate": "L0.5_data_honesty", "pass": true, "score": 0.8}
  },
  "issues": [
    {
      "gate": "G3_citation_integrity",
      "severity": "P1",
      "findings": ["3 orphan citations"],
      "suggestions": ["Add missing bib entries"]
    }
  ]
}
```

## 脚本清单

| 脚本 | 路径 | 用途 |
|------|------|------|
| quality-gate-runner.py | `scripts/quality-gate-runner.py` | 固定流程引擎，G1-G7 + L0.5 |

## 固定报告模板

- `refs/comprehensive-quality-report-template.md` — 报告结构模板（四份报告）
- `refs/quality-gate-fix-recipes.md` — 每个常见问题的修复方案
- `refs/codex-g7-quality-workflow.md` — G7 详细工作流
- `refs/stale-quality-report-trap.md` — 旧报告过期陷阱

## 陷阱

- **旧报告不可信**：state.json 中的 quality_score 可能过期 → 必须重新运行 runner
- **L0.5 一票否决**：即使其他门全过，L0.5 失败 → 整体不通过
- **state.json 自报 vs 独立审计不一致**：以 runner 输出为准
- **Ensemble 混用**：paper 声称的 ensemble 成员与实际 JSON 不一致 → P0

## 验证清单

- [ ] 运行了 quality-gate-runner.py
- [ ] 报告 JSON 解析成功
- [ ] 所有门 score ≥ 阈值
- [ ] L0.5 score ≥ 0.5
- [ ] 无 P0 未修复问题
- [ ] 报告保存为 quality-report.md
- [ ] state.json 已更新

## 边界声明

- 不保证论文质量高（只保证检查流程完整）
- 不执行自行编写的质量检查逻辑（全部走脚本）
- 报告生成后必须执行修复循环，不达标不退出

## Golden

- Golden Input: `{paper_dir: "outputs/papers/pima-crispdm"}`
- Golden Output: overall_score ≥ 0.85, all gates pass, quality-report.md generated
- Golden Error: exit code 1 when any P0 issue remains unrepaired
