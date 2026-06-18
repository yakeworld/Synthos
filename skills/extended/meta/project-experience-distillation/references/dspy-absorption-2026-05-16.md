# DSPy 外部吸收报告 — 签名系统 + 自动优化器

> 吸收日期: 2026-05-16
> 来源: stanfordnlp/dspy (20K+⭐)
> 吸收方式: 拓宽 evolution 引擎 v2.5→v2.6 + 创建 SKILL_SIGNATURE_STANDARD.md
> 吸收类型: Phase 3 — 声明式编程范式

## 分析路径

按五层提取规范的前三层必选顺序：

1. **思想** → DSPy 的核心信念是"编程而非提示"（Programming, not prompting）。与 Synthos 的"技能式认知"哲学相容但不相同——DSPy 相信自动编译，Synthos 相信手动精炼。可借鉴但不全部吸收。
2. **规范** → 声明式签名系统 `'inputs -> outputs: type'` 比 Synthos 的 IO_CONTRACT 更精确、更形式化。吸收为 `signature` frontmatter 字段 + SKILL_SIGNATURE_STANDARD.md。
3. **规律** → 自动优化器模式（基于测试失败自动调整 prompt）= 通用模式，吸收为 evolution OPTIMIZE 步骤。

## 吸收了什么

| 来源模式 | 吸收目标 | 变更 |
|:---------|:---------|:-----|
| 声明式签名 | 所有 Synthos 技能 | frontmatter 新增 signature 字段 |
| 签名类型系统 | SKILL_SIGNATURE_STANDARD.md | 新建共享参考文档 |
| auto-optimizer | evolution v2.6 | 新增 OPTIMIZE 步骤（收集失败→分析根因→补丁→验证→迭代） |
| 优化边界 | evolution v2.6 | 可优化（description/步骤/golden/验证）vs 不可优化（signature/原子逻辑/宪法） |
| 效果评估 | evolution v2.6 | DIAGNOSE 8.5 OPTIMIZE效果指标 + 回归撤销机制 |
| 指标驱动 | evolution v2.6 | 综合评分加入 OPTIMIZE效果权重10% |

## 仍未吸收但记录为参考

- **DSPy 编译时验证**: Synthos 是运行时 Agent 驱动，非编译时——不适用
- **模块化组合（`__init__`+`forward`）**: 已有 related_skills，模式不同
- **fine-tuning 集成**: Synthos 不做 model fine-tuning——不适用

## 原始分析

DSPy README + Modules docs + Optimization docs 通过 `curl` 从 GitHub raw 获取。

## 吸收统计

| 项目 | Claude Code (Phase 1-2) | DSPy (Phase 3) |
|:-----|:-----------------------|:---------------|
| 吸收模式数 | 8 | 6 |
| P0 吸收 | 4（哲学免疫/漂移检测/宪法/记忆护栏） | 2（签名系统/自动优化） |
| 文件创建 | CONSTITUTION v5.0 + 2共享文档 | SKILL_SIGNATURE_STANDARD.md |
| 技能升级 | evolution v2.4→v2.5 + 3其他 | evolution v2.5→v2.6 |
