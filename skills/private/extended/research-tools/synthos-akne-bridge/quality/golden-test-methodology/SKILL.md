---
name: golden-test-methodology
description: 覆盖率 = 有完整golden的技能数 / 总技能数
signature: 'golden-test-methodology -> quality: synthetic skill for golden test methodology'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 覆盖率 = 有完整golden的技能数 / 总技能数
    signature: 'golden-test-methodology -> quality: synthetic skill for golden test
      methodology'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---


## IO_CONTRACT

- **input**: 技能清单 + 各技能 golden/ 目录状态 — 覆盖率统计对象
- **input**: 扩展优先级排序请求 — 新吸收/高频使用/核心原子/扩展技能
- **output**: golden 覆盖率评级 — ≥70% 可接受 / 30-49% P1 目标 / <30% P0 系统性质量缺口
- **output**: golden 创建方法论 — cases + expected 的结构规范与优先扩展顺序（本技能只定义方法，不创建具体测试）

## 原则 (Principles)

- **空函不计**：仅存 `golden/` 目录而无 cases/expected 实物的，视同无测试——名实不符，不可入册。
- **有界则明**：预期（expected）须与用例（cases）一一配对，数量与命名不齐，则检验失其准的。
- **轻重相济**：权重不可尽置 critical，否则通一而断一切，测试便失其区分之能。
- **动则随更**：技能 signature 或输出既变，golden 必同步而更，否则陈法验新器，无所取信。

|
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


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[GOLD-001]** 统计 golden 覆盖率时 → 仅当 `GOLDEN_SET.md`、`cases/` 和 `expected/` 三者均存在且非空时才计入有效覆盖，空目录或仅存目录不计入。
- **[GOLD-002]** 定义测试预期时 → 确保 `expected` 文件与 `cases` 在数量与命名上严格一一配对，避免检验失准。
- **[GOLD-003]** 设置测试权重时 → 避免将所有检查项均设为 critical，需保留权重区分度以防止测试失去判别能力。
- **[GOLD-004]** 技能 signature 或输出格式发生变更时 → 必须同步更新对应的 golden 测试，确保陈法不验新器。
- **[GOLD-005]** 规划 golden 扩展优先级时 → 优先为新吸收的技能立即创建，其次按使用频率从高到低补充高频技能，最后按 DIAGNOSE 分数从低到高处理扩展技能。
- **[GOLD-006]** 评估覆盖率等级时 → 若覆盖率低于 30% 则标记为 P0 系统性质量缺口，30-49% 标记为 P1 改进目标，≥70% 视为可接受基线。

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

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。


# Golden Test Methodology