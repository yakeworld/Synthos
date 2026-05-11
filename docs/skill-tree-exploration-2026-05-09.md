# ⚠️ 已归档 — Synthos 技能树探索报告 v3.1

此文件于 **2026-05-10** 归档，原因：v4.0→v4.2.0 重构。

## 归档说明

**此报告描述的是 v3.1 架构（Python实现 + 14辅助脚本），已不再代表当前系统状态。**

### 发生了什么变化

| 旧架构 (v3.1) | 新架构 (v4.2.0) |
|---------------|-----------------|
| 6 Python原子类 + 14个Python脚本 | 7个纯 SKILL.md，Agent直接执行 |
| `core/` 目录 (16文件, ~4000行) | 已删除 |
| `run_pipeline.py` CLI入口 | 已删除 |
| 机械原子 vs 认知原子分裂 | 统一为技能驱动 |
| Python编排引擎 | Agent IS the Runtime |

### 当前架构请参阅

- **`docs/SKILL-architecture.md`** — 四层架构模型
- **`docs/SKILL-principles.md`** — P0-P3 宪法
- **`docs/SKILL-spec-profile.md`** — SKILL.md 规范
- **`evolution-state.json`** — 当前演化状态
- **`falsification-summary.md`** — 最新证伪检验结果

---

*原内容保留在此行以下供历史参考，不再更新。*
*删除时间: 2026-05-10*
*Deleted: entire core/ directory (16 Python files, ~4,000 lines)*
*Deleted: run_pipeline.py (CLI entry point)*
*Rewritten: all atoms are pure SKILL.md — Agent loads and executes directly*
