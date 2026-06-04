---
name: evolution
description: ⚡ P0 自进化引擎。Synthos evolution engine v2.17 — 四态决策+硬收敛+GEPA反射分析+自动基准+Pareto优化+外部吸收+教训学习+黄金验证+自扩关键词+漂移检测+渐进披露+Git即记忆。
license: MIT
metadata:
  synthos:
    version: 2.18.0
    priority: P0
    atom_type: meta-evolution
    author: Synthos
    signature: 'cycle: int -> evolution_report: dict'
    related_skills:
    - project-experience-distillation
    - quality-gate
    - skill-absorption
    - cognitive-atom-architecture
---

# Evolution Engine — 自进化引擎

## 核心流程

```
DIAGNOSE → 结构探查 + 功能基准 + Pareto多维优化
  ↓
OPTIMIZE → GEPA反射式分析 + 自动数据集
  ↓
VERIFY → 黄金验证 + 收敛检查
  ↓
CRYSTALLIZE → 技能结晶 + 教训学习
  ↓
BENCHMARK → 更新基准 + 自扩关键词
  ↓
SELF_REFLECT → 漂移检测 + 宪法集成
  ↓
→ 下一周期
```

## 四态决策

| 状态 | 触发条件 | 执行 |
|:-----|:---------|:-----|
| OPTIMIZE | 基线+改进方向清晰 | GEPA分析→技能建议 |
| DIAGNOSE | 指标未达标 | Pareto扫描→薄弱维度定位 |
| CRYSTALLIZE | 技能结晶点 | 事后分析→SKILL.md |
| EXPLORE | 方向不明确 | 自扩关键词→新方向 |

## 硬收敛护栏

- `EDIT_BUDGET`: 每次最多修改3个文件
- `rejected_buffer`: 被驳回的技能建议存入buffer，同方向不再提
- 连续3轮无进展 → 降级至探索模式
- 相同目标连续2次 → 自动切换到其他维度

## 查询命令

```bash
# 状态查询
cat evolution-state.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Cycles: {d[\"evolution_count\"]}, Score: {d[\"composite_score\"]}')"

# 最新日志
tail -50 evolution-log.md

# 基准测试
cat BENCHMARKS.md | grep -E "Pass|Fail|Score"
```

## 输出

- `evolution-state.json` — 状态持久化
- `evolution-log.md` — 操作日志
- `BENCHMARKS.md` — 自动数据集基准
- `skill_registry.json` — 技能注册表更新

## 参考文件

- `references/evolution-cycle-detail.md` — 完整周期流程Deep Dive
- `references/pareto-optimization.md` — Pareto多维优化策略
- `references/gepa-reflection.md` — GEPA反射式分析协议
- `references/benchmark-automation.md` — 自动基准测试
- `references/drift-detection.md` — 漂移检测和宪法集成
