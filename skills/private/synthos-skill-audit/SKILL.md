---
name: synthos-skill-audit
description: Synthos技能质量审计 — 思想密度、代码占比、入口单一性评估方法论。具体审计命令和修复细节见 references/。
version: 2.0.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P0
    atom_type: audit-skill
    description: "Synthos skill quality audit — thought density, code ratio, single entry point evaluation methodology."
    signature: 'directory_a: str, directory_b: str -> audit_report: dict, sync_plan: list'
    related_skills: [akne-maintenance, maintenance, skill-integrity-audit]
---

# Synthos Skill Audit

## 思想

> 技能即原子。高质量技能 = 高思想密度 × 单一入口 × 可验证契约。
> 系统性审计和修复 Synthos 技能目录（sda2/Synthos/skills）和 Hermes 技能目录（~/.hermes/skills）。

## 原理

1. **思想密度**：SKILL.md 中原则、方法、规则的内容占比应高于示例代码。代码和 API 文档是案例，不是主体。
2. **入口单一性**：每个技能应有唯一的入口点（SKILL.md），子技能通过父级 SKILL.md 索引，而非通过同名文件重复注册。
3. **契约完整性**：类级别技能需具备 SKILL.md + IO_CONTRACT + BOUNDARY + EVIDENCE_SCHEMA，简单工具可简化。
4. **双向同步**：Synthos 与 Hermes 两个目录应保持同步，Hermes 为主源（最新编辑在 Hermes）。
5. **隐私隔离**：含凭证/内部审计数据的技能存放在 private/ 目录，gitignore 保护不推 GitHub。

## IO Contract

- **Input**: directory_a (str), directory_b (str) — 两个技能目录路径
- **Output**: audit_report (dict), sync_plan (list) — 审计结果和同步计划

## 核心流程

### 总览

```
定位权威源 → 目录扫描 → 重复检测 → 内容一致性 → 结构完整性 → 重复同步 → 跨目录同步 → Graph 同步 → 隐私扫描
```

### 阶段说明

| 阶段 | 方法 | 产出 |
|------|------|------|
| 定位权威源 | find + wc 统计各路径 SKILL.md 数量 | 权威源确认 |
| 目录扫描 | 发现两个目录所有同名技能 | 重复集合 |
| 内容一致性 | 比较整个目录（不仅 SKILL.md） | 不一致清单 |
| 结构完整性 | 检查 SKILL.md + IO_CONTRACT + BOUNDARY + EVIDENCE_SCHEMA | 结构报告 |
| 重复同步 | 以 Hermes 为主源，rmtree → copytree | 同步完成 |
| 跨目录同步 | 仅 Synthos 的技能 → 复制到 Hermes，反之亦然 | 双向覆盖 |
| Graph 同步 | 更新 graph.json：添加缺失节点，删除孤立节点 | 图-磁盘一致 |
| 隐私扫描 | 六项扫描检测凭证、路径、论文数据 | 隐私报告 |

## 各阶段方法

### 阶段1：权威源确认

路径识别是关键陷阱：
- `/home/yakeworld/Synthos/` — 空壳目录（仅2个SKILL.md文件），**不是**权威源
- `/media/yakeworld/sda2/Synthos/` — 权威源（211个SKILL.md，完整Git仓库）
- `~/.hermes/skills/` — Hermes 独有扩展技能（57个SKILL.md），与 Synthos 独立

快速诊断：
```bash
find /media/yakeworld/sda2/Synthos -name 'SKILL.md' | wc -l  # 应有 ~200+
find /home/yakeworld/Synthos -name 'SKILL.md' | wc -l          # 空壳应 <5
```

### 阶段2：重复检测

发现两个目录所有同名技能，计算重复集合。**注意**：嵌套层级是用户偏好，不扁平化。

**同名冲突**：同一目录树内同名技能触发 AMBIGUOUS 错误，`skill_view(name)` 直接拒绝加载。优先标记经常被 cron 引用技能的重复：
- paper-pipeline
- quality-gate
- sci-paper-quality-review
- skill-integrity-audit

**跨目录同名**（如 sda2/quality 和 hermes/quality）不触发 AMBIGUOUS 错误，因为 Hermes 将 external_dirs 和 builtin 路径分开处理。

### 阶段3：结构完整性

**类级别技能**需要：SKILL.md + IO_CONTRACT + BOUNDARY + EVIDENCE_SCHEMA + golden + CHANGE_LOG

**简单工具**：SKILL.md（可选 IO_CONTRACT）

**父级目录**：SKILL.md（索引子技能）。有子技能的父级目录必须有 SKILL.md，包含子技能索引表和使用场景描述。

**golden 目录**：完整原子技能应包含 golden/GOLDEN_SET.md（黄金测试用例）。

### 阶段4：重复技能同步

**原则**：Hermes 为主源（最新编辑在 Hermes）。
```python
shutil.rmtree(SYNTHOS) → shutil.copytree(HERMES, SYNTHOS)
```

仅 Synthos 的技能 → 复制到 Hermes。仅 Hermes 的技能（有 SKILL.md 或有子技能） → 复制到 Synthos。

### 阶段5：目录结构清理

**五步清理**：
1. 空目录扫描 — 确认是结构模板还是垃圾
2. 单文件目录扫描 — 目录索引保留/展平
3. 内容重复检测 — 过时精简版直接删除
4. 位置纠正 — 错放内容移到正确子目录
5. 嵌套 Git 检测 — 独立仓库不删除，移出或彻底移除

**执行原则**：
- 明确无用的空目录 → 直接 `rmdir`
- 1-2个文件的嵌套目录（<1MB） → 展平或移动，不需确认
- 含用户数据（>100MB / 竞赛 / 个人） → 给选项+推荐
- 含嵌套 .git → 提示用户，移出或删除
- 确认属于结构规范模板 → 保留不动

### 阶段6：Graph 同步

更新 graph.json：添加缺失节点（磁盘有但图无），删除孤立节点（图有但磁盘无）。

**关键原则**：文件删除和图更新是两个独立操作，必须都完成才算修复完成。

**文件去重策略**：
1. 精确 basename 匹配：同一文件名在不同目录 → 保留最大文件
2. 激进 stem 匹配：去除日期/版本后缀 → 保留最新/最大版本
3. 去重后必须恢复"保留文件"的类别边

### 阶段7：隐私扫描

**分级标准**：

| 等级 | 标签 | 含义 | 存放位置 |
|:----:|:----:|:------|:---------|
| 🔴 | 私有 | 含凭证/SSO/服务器IP/内部审计数据/研究方向专有 | Synthos/skills/private/ |
| 🟡 | 去敏后可公开 | 含本机路径或论文示例但不含凭证 | 去敏后 → Synthos/public/ |
| 🟢 | 直接公开 | 无隐私内容 | Synthos/skills/public/ |

**六项隐私扫描**：

| # | 检测项 | 方法 | 风险 |
|:-:|:-------|:-----|:----:|
| 1 | 凭证/API Key | grep -rli 'api_key\|password\|secret\|token\|auth\|credential\|sso' | 🔴 |
| 2 | 本机用户名 | grep -rl 'yakeworld' | 🟡 |
| 3 | 绝对路径 | grep -rl '/media/yakeworld' | 🟡 |
| 4 | 论文数据 | grep -rl 'outputs/papers' | 🟡 |
| 5 | 服务器IP | grep -rnE '\d+\.\d+\.\d+\.\d+' 排除内网段 | 🔴 |
| 6 | 内部审计结果 | 含 .json 或 .md 审计报告文件 | 🔴 |

**隐私隔离原则**：2026-06-25 起，所有含隐私风险的技能从 ~/.hermes/skills/ 搬至 Synthos/skills/private/，Hermes 通过 external_dirs 自动加载。

## 项目健康检查

当用户要求"检查synthos项目"或"项目健康检查"时，执行：

1. **定位权威仓库** — find + wc 确认路径
2. **进化状态** — 读取 evolution-state.json（cycle, version, status, overall_score）
3. **论文管线** — outputs/papers/ 目录数、投稿包、研究审计状态
4. **Git 健康** — 未跟踪数、落后/领先远端数、远端地址（注意：cron 自动提交常导致 >10 commits behind，属正常）
5. **AKNE 知识库** — CATALOG.md, graph.json, vectors.db
6. **技能结构** — 完整性统计、缺失列表

输出报告：项目概览 → 论文管线 → 技能系统健康 → Git 状态 → 问题清单 → 结论。

## 规则

1. **路径优先确认** — 审计前必须用 find + wc 确认权威源，避免空壳路径
2. **同名即冲突** — 同一目录树内同名技能触发 AMBIGUOUS，优先修复 cron 依赖技能
3. **跨目录不同名** — sda2 和 hermes 的跨目录同名是镜像冗余，不触发错误
4. **Hermes 主源** — 重复技能同步时，Hermes 为最新编辑的主源
5. **父级有 SKILL.md** — 所有有子技能的父级目录必须有 SKILL.md
6. **文件删除=图更新** — 两个独立操作必须都完成
7. **隐私隔离** — 含敏感数据的技能必须存放在 private/，gitignore 保护
8. **慎问即行** — 小改动直接执行，大改动（>100MB / 含用户数据）先给选项

## 参考文件

- `references/dedup-sync-pattern.md` — 重复技能同步详细步骤：发现→检查→统一→双向同步→验证
- `references/ambiguous-name-recovery.md` — 运行时别名冲突恢复：skill_view AMBIGUOUS 故障处理
- `references/path-redundancy-2026-06-18.md` — 路径冗余诊断
- `references/path-trap-2026-06-21.md` — 路径陷阱诊断方法
- `references/learn-vs-synthos-comparison.md` — `/learn` 生成技能 vs Synthos 标准技能对比（调用方式差异、四块→五节法映射、桥接方案）— 用于评估 AI 自动生成的技能质量

## 陷阱 · AI 生成技能与人工精修

> **陷阱**：`/learn` 等 AI 工具生成的技能是"说明书"（操作手册），不是"宪法"（契约语言）。直接落地为 Synthos 标准会缺失 BOUNDARY、IO_CONTRACT、EVIDENCE_SCHEMA 等核心契约层。
>
> **修复**：AI 生成的四块结构（When/Procedure/Pitfalls/Verification）必须经过 post-processor 补全，或人工补充五节法结构。见 `references/learn-vs-synthos-comparison.md` 完整映射表。


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-28 | 2.1.0 | 新增 `references/learn-vs-synthos-comparison.md` — `/learn` 生成技能 vs Synthos 标准完整对比，四块→五节法映射，调用层级差异分析 |
| 2026-06-27 | 2.0.0 | 重构：提炼思想/原理/IO Contract/流程/方法/规则。具体命令、案例移至 references/ |
| 2026-06-25 | 1.5.0 | 新增双仓库架构、隐私技能迁移、隐私扫描分级 |
| 2026-06-21 | 1.4.0 | 新增路径陷阱检测、权限修复 |
| 2026-06-18 | 1.3.0 | 合并 project-health-audit，新增项目健康检查流程 |



# Synthos Skill Audit

