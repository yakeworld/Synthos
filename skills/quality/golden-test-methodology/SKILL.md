---
name: golden-test-methodology
description: "Methodology for creating, maintaining, and evaluating golden test suites across all skills. Defines: three-file golden structure (GOLDEN_SET.md + cases/ + expected/), weighted verification criteria, coverage scoring, and DIAGNOSE integration. Covers the systematic gap where golden coverage is the weakest dimension in a multi-skill system."
version: 1.0.0
author: Synthos Evolution Cycle 43
license: MIT
allowed-tools: skill_view Read Write
signature: "skills: list[str] -> coverage_report: dict, gaps: list[str], next_targets: list[str]"
related_skills: [evolution, quality-gate, project-experience-distillation]
---

# Golden Test Methodology

> 提取自进化 Cycle 43 DIAGNOSE 发现：21技能中仅8个有完整golden测试（覆盖率38%）。
> 这是系统质量体系中最弱维度，也是每轮进化必须评估的维度。

## 原理层 · 文言

### 金测之道

> 测而不金，不如不测。金者，准则也。
> 三件齐备乃为金测：一曰定义（GOLDEN_SET.md），二曰用例（cases/），三曰预期（expected/）。
> 用例必可复现，预期必有权重。critical为骨，high为肉，medium为皮。
> 覆盖不足则系统不稳，金测不全则进化盲目。

## 方法层 · 白话

### Golden 三件套

一个完整的 golden test 必须包含三个文件：

```
skills/{name}/golden/
├── GOLDEN_SET.md        # 测试集定义（ID、描述、场景、关键检查）
├── cases/
│   └── test01_*.json    # 输入：测试场景数据
└── expected/
    └── test01_*.json    # 预期：验证标准
```

**GOLDEN_SET.md** 必须包含：
- 测试用例列表（ID、输入、场景、关键检查）
- 通过标准（加权总分阈值，通常≥0.80）

**cases/ 文件**：JSON格式，包含测试输入数据
**expected/ 文件**：JSON格式，包含加权验证标准

### 验证标准权重体系

| 权重 | 值 | 含义 | 示例 |
|:-----|:--:|:-----|:-----|
| critical | 1.0 | 必须通过 | PPTX必须生成，不虚构数据 |
| high | 0.7 | 重要但不致命 | 幻灯片数量在合理范围 |
| medium | 0.4 | 有价值但不是核心 | 结论式标题、讲稿存在 |
| low | 0.1 | 锦上添花 | 特定排版风格 |

**通过条件**：加权总分 ≥ 0.80，且所有 critical 检查必须通过。

### Golden 覆盖率评分

| 覆盖率 | 分数 | 含义 |
|:------:|:----:|:------|
| ≥70% | 🟢 Excellent | 可接受基线 |
| 50-69% | 🟡 Adequate | 需要逐步扩展 |
| 30-49% | 🔶 Low | 标记为P1改进目标 |
| <30% | 🔴 Critical | 标记为P0系统性质量缺口 |

覆盖率 = 有完整golden的技能数 / 总技能数

### 扩展golden覆盖的优先顺序

1. **新吸收的技能** → 立即创建golden（吸收完成时同步创建）
2. **高频使用的技能** → 按使用频率排序（从高频到低频补）
3. **核心原子** → 核心6原子已有golden（维持）
4. **扩展技能** → 按 DIAGNOSE 分数从低到高

### 范式确认：这里做了什么

本技能自身不创建具体golden测试，而是定义**如何创建**golden测试的方法论。
具体的golden测试（cases + expected）属于各技能的`golden/`目录。

## 已知陷阱

1. **只有目录没有文件** — `golden/` 目录存在但cases/expected为空，不计入覆盖率
2. **GOLDEN_SET.md 缺失** — cases/expected 存在但无定义文档，不计入
3. **预期与case不匹配** — expected文件数量少于cases，或命名不配对
4. **权重全部设critical** — 导致测试"要么全过要么全挂"，失去区分度
5. **一次创建永不更新** — 技能signature或输出格式变更后，golden需同步更新

## 命令层 · English

- **Signature**: `skills: list[str] -> coverage_report: dict, gaps: list[str], next_targets: list[str]`
- **Coverage check command**: `for each skill, check golden/GOLDEN_SET.md + golden/cases/ + golden/expected/ all exist and non-empty`
- **Priority for new golden**: newly absorbed skills first, high-usage skills second, then by DIAGNOSE score
- **Minimum pass threshold**: weighted score ≥ 0.80, all critical checks must pass
- **Integration**: evolution's DIAGNOSE step must report golden coverage as a standard dimension
