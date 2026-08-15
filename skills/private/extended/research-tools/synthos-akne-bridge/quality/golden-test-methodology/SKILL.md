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
    signature: 'golden-test-methodology -> quality: synthetic skill for golden test methodology'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 技能清单 + 各技能 golden/ 目录状态 — 覆盖率统计对象
- **input**: 扩展优先级排序请求 — 新吸收/高频使用/核心原子/扩展技能
- **output**: golden 覆盖率评级 — ≥70% 可接受 / 30-49% P1 目标 / <30% P0 系统性质量缺口
- **output**: golden 创建方法论 — cases + expected 的结构规范与优先扩展顺序（本技能只定义方法，不创建具体测试）

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

# Golden Test Methodology---





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

## 验证清单 (Verification)

- [ ] 覆盖率统计时：`golden/GOLDEN_SET.md` + `cases/` + `expected/` 三者均存在且非空才计数
- [ ] expected 文件与 cases 数量、命名一一对应
- [ ] 权重未全部设为 critical（保留区分度）
- [ ] 技能 signature/输出格式变更后，golden 已同步更新
- [ ] 补 golden 顺序正确：新吸收技能 → 高频技能 → 核心原子 → 扩展技能（按 DIAGNOSE 分）
