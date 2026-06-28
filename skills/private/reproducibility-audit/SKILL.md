---
name: reproducibility-audit
description: >-
  论文实验可复现性审计 — 实验审计方法论（代码+数据+输出验证），
  提炼核心原则、方法、规则。具体检查步骤、命令、案例见 references/。
version: 2.0.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: quality
    description: >-
      论文实验可复现性审计 — 实验审计方法论。
      代码即证，逐层验证：代码→环境→数据→输出→论文声称。
    related_skills: [paper-improvement, paper-improvement-patterns, paper-d8-d10a-scan, notebooklm-cli, quality-gate]
signature: "reproducibility-audit -> processed_result"
---

# 可复现性审计

## 思想

> 数必可验，代码即证。同源不同果，非伪即异。
> 不复现，不轻信；不复现，不改字。
> **发现即修复** — 审计发现的数值不一致应在同一轮会话中直接修复，而非输出"待修列表"。

## 原理

1. **可验性原则**：任何论文声称的数值必须能在独立环境中复现。不可复现的数值等于不存在。
2. **同源追踪**：同一方法在同一环境应产生一致结果。差异的根源只能是环境、数据或随机流三者之一。
3. **逐层验证**：审计自下而上——代码→环境→数据→输出→论文声称。顶层声称错误时，底层验证提供定位依据。
4. **发现即修复**：审计的价值在于修正，不在清单。

## IO Contract

- **Input**: paper_dir (str) — 论文目录路径
- **Output**: audit_report (dict) — 审计结果，含环境对比、数值对比、伪造检测、修复建议

## 核心流程

### 总览

```
定位代码 → 提取输出 → 环境比对 → 逐方法复现 → 根因诊断 → 论文验证 → 伪造检测 → 论文修正
```

各阶段详见 `references/` 目录。

### 阶段说明

| 阶段 | 方法 | 产出 |
|------|------|------|
| 定位实验代码 | 搜索 .ipynb / .py / requirements.txt | 代码清单 |
| 提取 Notebook 输出 | JSON 解析 cell outputs，构建 cell→值映射 | 输出值表 |
| 环境比对 | 对比 Python/包版本、安装方式、路径 | 差异清单 |
| 逐方法复现 | 提取完整 source，在当前环境执行 | 复现结果 |
| 根因诊断 | 检查代码一致性→环境差异→数据一致性→随机流 | 根因结论 |
| 论文验证 | 对比复现值与论文声称值 | 不一致清单 |
| 伪造检测 | 模式匹配：直接伪造/方法混淆/数值漂移 | 伪造报告 |
| 论文修正 | 按章节顺序应用补丁，清理引用，更新 state.json | 修复完成 |

## 各阶段方法

### 阶段1：模型数量审计（Pre-Check）

**规则**：在开始数值对比前，必须先验证模型数量是否一致。

- 论文提取：grep 数字 + model/baseline/classifier，数表格列数
- 代码提取：统计产生 metric 的 cell 数 / 模型定义数 / 结果文件唯一模型名
- 不一致 → 暂停，标记 `MODEL_COUNT_SUSPECT`

**详细方法见**：`references/protocol-gap-analysis-pima.md`

### 阶段2：逐层验证

**代码层**：验证 cell source 与脚本代码是否完全一致，检测过时 output。

**环境层**：Python 版本 → 包版本 → 安装方式。差异源：
- Python 版本（3.11 vs 3.12）— 随机种子行为可能不同
- 包版本（sklearn, imblearn）— API 变更、默认参数改变
- 安装方式（Kaggle 预装 vs 手动 pip）

**数据层**：列名、列顺序、缺失值编码、零值分布。OpenML 与本地数据一致性验证。

**随机流层**：seed vs RandomState、cross_validate 自动重置 vs 手动循环状态残留。

### 阶段3：伪造检测

**模式分类**：

| 模式 | 检测方法 | 严重度 |
|------|---------|--------|
| 直接伪造 | 声称值完全不在任何代码输出中 | 致命 |
| 方法混淆 | 声称值来自不同方法的输出 | 严重 |
| 数值漂移 | 声称值与代码输出有显著差异 | 中等 |
| 方向反转 | 变化方向被反转（实际↓但声称↑） | 致命 |
| 选择性报告 | 只报告最好的结果，隐藏差的 | 中等 |
| 伪造引用 | 引用条目不完整或缺失 | 严重 |

**方向性反转检测**：
```python
def detect_direction_reversal(actual_before, actual_after, paper_before, paper_after):
    actual_direction = 'up' if actual_after > actual_before else 'down'
    paper_direction = 'up' if paper_after > paper_before else 'down'
    if actual_direction != paper_direction:
        return 'NARRATIVE_REWRITE_REQUIRED'
    return 'VALUE_UPDATE_ONLY'
```

- `VALUE_UPDATE_ONLY`：方向一致但幅度不同 → 替换数字，调整叙事语气
- `NARRATIVE_REWRITE_REQUIRED`：方向相反 → 重构依赖该指标的所有论证段落

### 阶段4：论文修正

**修正顺序**：Abstract → Figure → Introduction → Algorithm → Results → Discussion → Conclusion → 全局残留搜索。

**防错规则**：
- 每个 patch 使用精确的 old_string（包含足够上下文确保唯一性）
- patch 失败时重新读取该区域确认当前内容
- 全局搜索旧值确认无残留
- 清理依赖伪造数据的 \cite{} 引用
- 修正后更新 state.json

## 规则

1. **先模型数量，后数值对比** — 模型数量不一致时所有数值对比无效
2. **比较同一方法** — 不同方法产生不同结果，比较前必须确认方法一致
3. **验证数据一致性再归因** — F1 不同不等于数据不同，可能是实验协议问题
4. **过时 output 检测** — 重运行 cell 对比输出，不一致说明 output 过时
5. **版本敏感** — imbalanced-learn 0.13+ API 变更（n_neighbors → k_neighbors）
6. **Kaggle 环境差异** — Python 3.11, sklearn 1.3.x, imblearn 0.12.x 是常见基线
7. **Track A 论文位置** — 可能不在 Synthos/outputs/ 下，在 /media/yakeworld/sda2/投稿文件汇总/
8. **发现即修复** — 不在同一轮中修复的问题清单不是有效审计

## 参考文件

- `references/fabrication-detection-patterns.md` — 数值伪造检测模式库：直接伪造、方法混淆、数值漂移、选择性报告、伪造引用
- `references/pima-crispdm-audit-2026-06-20.md` — PIMA-CRISPDM 完整审计报告，含双结构检测、声-实对比表、方向性反转
- `references/notebook-code-paper-audit.md` — Notebook ↔ Code ↔ Paper 对齐审计
- `references/protocol-gap-analysis-pima.md` — Protocol Gap Analysis 方法论，数据一致性验证

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-27 | 2.0.0 | 重构：提炼思想/原理/IO Contract/流程/方法/规则。代码示例、案例移至 references/ |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
