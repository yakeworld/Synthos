---
name: quality-gate
description: ⚡ P0 闸门技能。四层质量架构：L0.5数据诚实门 + L1-L4交付闸门 + G1-G7论文闸门 + SCI 7维评审。通用铁律：任务完成→质量评估→不达标→循环执行。
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    version: 2.9.0
    priority: P0
    atom_type: meta-quality
    author: Synthos
    signature: 'deliverable: str -> gate_result: dict'
    related_skills:
    - project-experience-distillation
    - evolution
    - sci-paper-quality-review
    - paper-pipeline
    absorbed_skills:
    - post-compile-dual-quality-check
    - dual-quality-check-v2
    - bib-integrity-audit
    - reference-quality-triage
    - academic-thesis-review
    execution_note: 吸收内容见 references/*-absorbed.md
---

# Quality Gate — 质量闸门

## 核心理念（文言）

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| 无记录=门不通过 | **无录不过** | 无skill_view记录视为未执行 |
| G5引用质量最关键 | **引质为要，G5最重** | 论文质量上限=引用质量 |
| 凡数必源，不源不取 | **无源不取** | 无实验记录的数据声明=编造 |
| 一次一个维度 | **一维一渡** | 每次只聚焦一个等级，不跳步 |

## 四层架构

| 层 | 范围 | 触发 |
|:---|:-----|:------|
| L0 动灵层 | 交付物方向与系统生长路径一致性 | 每次评估前 |
| L0.5 数据诚实门 | 每个可验证数据声明是否有源文件支撑 | 每次论文评审前 |
| L1 响应级 | 当前会话输出质量 | PreResponse Hook |
| L2 项目级 | 交付物D1-D6 | 项目阶段完成 |
| L3 管线级 | 论文G1-G7原子闸门 | 写作管线每阶段切换 |
| L4 内容级 | SCI 7维评审 | G7通过后自动 |

## L0.5 数据诚实门

提取论文中所有数值声明→逐条追溯源文件：

| 声明类型 | 源文件验证方法 |
|:---------|:--------------|
| 进化数据 | `evolution-state.json` → evolution_count / trust_score |
| 基准测试 | `BENCHMARKS.md` → golden test输出 |
| 实验结果 | 实验代码输出/JSON文件/日志 |
| 对比基线值 | 追溯原始论文PDF确认具体数值 |

**通过条件**：全部数据声明有源✅或已标注estimated🟡。否则❌不通过。

## G1-G7 论文闸门

| 闸门 | 检查 | 通过条件 |
|:-----|:-----|:---------|
| G1 ACQ | 文献搜索 | ≥60候选, ≥30 PDF |
| G2 EXT | 知识提取 | 结构化提取 |
| G3 ASC | 关联空白发现 | 关联+空白矩阵 |
| G4 HYP | 假设生成 | 可证伪假设 |
| G5 ARG | 论文论证+引用全文验证 | 无虚构引用+无僵尸/孤儿 |
| G6 VER | 观点验证 | 验证通过 |
| G7 latex | 编译验证 | cite×bib×pdf三维匹配 |

详细检查清单见 `references/writing-pipeline-checklist.md`。

## 双质量评分

```
Layer A: 本地7维评审（基于实际读到的paper.tex）
Layer B: NotebookLM Gemini 7维评审
校准分 = min(Layer A, Layer B)

| 校准平均分 | 判定 |
|:----------:|:-----|
| ≥0.85 | T1 PASS |
| ≥0.80 | T2 PASS |
| ≥0.75 | T3 PASS |
| <0.75 | FAIL → 自动修订循环 |
```

修订循环：不达标→自动修订→重评。连续3轮无进展→降级目标期刊。

## 关键陷阱

- G5c门：Layer B执行前必须验证NotebookLM源数 ≥ D8×80%
- L0.5文献观察≠实验发现：措辞必须分级
- 实验数值必须有实验代码（不可编造）
- 消融表所有行必须来自同一模型管线
- 派生值同步检查：修改原始值后重算百分比/ratio

## 参考文件

- `references/writing-pipeline-checklist.md` — G1-G7详细检查清单
- `references/bibitem-integrity-verification.md` — Bibitem完整性验证
- `references/ref-citation-audit-protocol.md` — 引用审计协议
- `references/data-leakage-audit-protocol.md` — 数据泄露审计
- `references/full-claim-l05-verification-2026-06-01.md` — 全量声明L0.5验证
- `references/pre-commit-security-scan.md` — 提交前安全扫描
- `references/gap-hypothesis-congruence.md` — G5d空假一致性门
