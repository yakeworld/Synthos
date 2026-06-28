# `/learn` 生成技能 vs Synthos 标准技能对比

## 来源
- Cycle 183 (2026-06-28)：用户问"如何使/learn生成的技能符合synthos标准？"和"你调用/learn生成的技能调用和synthos有什么不同吗？"
- 完整对比分析输出

## 核心差异

### `/learn` 输出（四块结构）

```yaml
--- name: <skill-name>
description: <60字以内简述>
version: 1.0.0
---
## When to Use（什么时候用）
## Procedure（步骤）
## Pitfalls（陷阱记录）
## Verification（怎么确认成功）
```

**调用方式**：用户指令 → Agent 加载 SKILL.md → 读→做。无中间层。

**本质**：操作手册（怎么做）。Agent 逐行执行 Procedure。

### Synthos 标准技能（五节法 + 契约层）

```yaml
--- name: ... version: ... signature: ... related_skills: ...
metadata:
  synthos:
    priority: P0
    atom_type: cognitive-atom
    description: ...
---
# Skill Name
## 思想（文言原则）
## 原理（方法 + 白话解释）
## IO_CONTRACT（输入输出规范）
## BOUNDARY（边界声明）
## EVIDENCE_SCHEMA（证据标准）
## CHANGE_LOG
## 触发条件 + 运行模式 + 步骤 + 规则 + 陷阱 + 验证清单
## references/（引用文件）
## scripts/（可执行脚本）
```

**调用方式**：用户指令 → Agent 理解契约约束 → 在边界内选择执行路径 → 执行 → 按证据标准验证。

**本质**：契约语言（做什么+不做什么+怎么验证）。Agent 先读边界约束，再在约束内选择执行路径。

## 四块 → 五节法映射

| `/learn` 四块 | Synthos 五节 | 转换规则 |
|---|---|---|
| When to Use | → 思想层 + 触发条件 | 思想层提炼核心理念（文言一句话），触发条件列出具体场景 |
| Procedure | → 原理 → 方法 | 原理是为什么这样做，方法是具体步骤 |
| Pitfalls | → 规则 + 已知陷阱 | 规则是通用铁律，陷阱是具体案例 |
| Verification | → 验证清单 + EVIDENCE_SCHEMA | 清单是检查项，Schema 是证据标准 |

## 缺失契约层

| Synthos 契约 | `/learn` 是否生成 | 差距 |
|---|---|---|
| BOUNDARY（功能边界） | ❌ 无 | 无功能范围界定 |
| IO_CONTRACT（输入输出规范） | ❌ 无 | 仅有 Procedure 隐含输入输出 |
| EVIDENCE_SCHEMA（证据标准） | ❌ 无 | 无验证证据框架 |
| CHANGE_LOG（版本追踪） | ❌ 无 | 无版本历史 |
| golden/（黄金测试） | ⚠️ 部分 | 测试是验证步骤，不是测试用例集 |
| references/（外部化深度知识） | ❌ 无 | 无引用文件 |
| scripts/（可执行脚本） | ❌ 无 | 无自动化脚本 |
| metadata.synthos.* | ❌ 无 | 缺少 atom_type、priority、signature、related_skills |

## 桥接方案

### 路径 A：Hermes 原生支持
向 Hermes Agent 官方 PR，在 `/learn` 中添加 `--synthos` 标志，自动注入完整契约层。

### 路径 B：本地 post-processor（当前推荐）
创建 `learn-to-synthos` 转换管道：
1. 读取 `/learn` 生成的 SKILL.md
2. 注入元数据（author, license, metadata.synthos.*, signature, related_skills）
3. 生成 BOUNDARY（从 Procedure/Pitfalls 反推边界）
4. 生成 IO_CONTRACT（从 Procedure 提取输入输出）
5. 生成 EVIDENCE_SCHEMA（从 Verification 反推）
6. 生成 CHANGE_LOG（初始条目）
7. 五节法转换（四块→思想→原理→方法→规则→参考）
8. 生成 golden/ 目录骨架

### 路径 C：MVP 三件套（最小可行）
1. 元数据注入（signature + metadata）
2. BOUNDARY 生成
3. IO_CONTRACT 生成
→ 使 `/learn` 生成的技能达到 Synthos"简单工具"标准（SKILL.md + IO_CONTRACT）

## 调用层级对比

| 维度 | `/learn` 技能 | Synthos 技能 |
|---|---|---|
| 本质 | 操作手册（Instruction） | 宪法（Contract） |
| Agent 理解 | 逐行执行 | 先约束后选择 |
| 错误处理 | Pitfalls 是"踩到会出问题" | BOUNDARY 是"不在本技能范围内" |
| 输入验证 | 隐含在 Procedure 中 | IO_CONTRACT 显式声明 |
| 输出验证 | Verification 检查列表 | EVIDENCE_SCHEMA 定义证据标准 |
| 扩展方式 | 改 Procedure | 改 IO_CONTRACT + 新增模式 + 加 CHANGE_LOG |
| 复合调用 | 无显式接口 | 技能间通过 IO_CONTRACT 对接 |
| 版本管理 | 无 | CHANGE_LOG + 版本号 + 变更原因 |

## 实战案例

`quality-gate` 为例：
- `/learn` 版本：步骤1 读取交付物 → 步骤2 检查结构 → 步骤3 评分 → 步骤4 输出报告
- Synthos 版本：先定义"我只检查不生产。范围覆盖 L0-L4。不覆盖内容生产。触发：每次任务完成。退出：score≥0.85"，再选择运行模式（正常/快速/深度/审计），最后按证据标准验证。

调用者看到 Synthos 版本会知道不能做什么、输入什么格式、用什么证据、以什么模式做。看到 `/learn` 版本只会知道"跟着步骤做就行"。
