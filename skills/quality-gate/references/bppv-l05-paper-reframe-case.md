# PAP-04 Type A 全量虚构案例

> 2026-05-25 实战教训。此案例展示了 L0.5 数据诚实门检测到"设计提案打扮成实验结果"的全过程。

## 背景

- **论文**：PAP-04 "BPPV as a Slow-Dynamics Probe" (vor-sparse-modular)
- **目标期刊**：PLOS Computational Biology
- **当前状态**：310行完整IMRaD LaTeX草稿，编译为13页PDF
- **发现方式**：空闲任务推进 cron 自动审计

## 检测过程

### Step 1: 引用计数 — 立即触发可疑信号

```bash
grep -c '\\cite{' paper.tex
# 结果: 7篇引用（PLOS Comp Biol 通常需40-60篇）
```

触发阈值：完整草稿 + 引用 < 10 → 🚩

### Step 2: 搜索实验代码 — 零结果

```bash
find /media/yakeworld/sda2/Synthos -name '*.py' | xargs grep -liE '(bppv|vor|sparse.modular|digital.twin)' 2>/dev/null
# 结果: 空（零文件）
```

触发阈值：有定量表(±SD/p值) + 无可执行代码 → 🚩🚩

### Step 3: Bib 交叉污染检测

检查 references.bib 中无关条目：

```bash
grep 'title\s*=' references.bib | grep -iE '(iris|segmentation|breast|pima)'
# 发现: he2008toward — "Toward Accurate and Fast Iris Segmentation for Iris Biometrics" 
# 这是一个虹膜分割论文，与BPPV/VOR完全无关
```

触发阈值：有明显跨项目污染条目 → 🚩🚩🚩

### Step 4: 物理合理性检查

审查表格中最可疑的数值：

| 声明 | 期望值 | 实际值 | 判定 |
|:-----|:-------|:-------|:-----|
| VOR高频增益(25-50Hz) | <1.0（VOR在高频增益下降） | 1.62±0.12 | ❌ 物理不合理 |

触发阈值：物理不合理数值 → **确认全量虚构**

## 论文概念 vs 数据真实性

| 维度 | 评价 |
|:-----|:-----|
| BPPV-as-slow-dynamics-probe 范式 | ✅ 确实新颖 |
| 稀疏模块BIN架构（解剖同构） | ✅ 动机清晰 |
| Neural ODE + hypernetwork（涌现倾泻衰减） | ✅ 技术路径合理 |
| 慢校准/快验证范式 | ✅ 解决了真实问题 |
| 全文定量数据（三张表+临床案例） | ❌ 全部无源文件 |
| 引用基（7篇） | ❌ 不足 |

**结论**：概念好、数据假。论文是"设计提案"穿上了"实验结果"的衣服。

## 正确响应

全量虚构 ≠ 论文无价值。正确的处理：

1. **保留核心观点**：BPPV-as-slow-dynamics-probe 是新颖范式，值得发表为理论框架
2. **删除/标记所有定量数据**：三张表全部标注为 "estimated" / "projected"
3. **重写 Abstract 和 Results**：从 "We demonstrate... gain 0.95±0.05" 改为 "We propose... projected to achieve approximately 0.95"
4. **扩展引用基**：7篇 → 30+篇（通过正式 ACQ 管线）
5. **清理 bib**：移除跨项目污染的 6 条条目
6. **补充 Limitations**：清晰说明所有定量结果为理论推算，待实验验证

## 与 Type B（引用链传播）的区别

| 维度 | Type A（全量虚构） | Type B（引用链传播） |
|:-----|:-------------------|:---------------------|
| 核心问题 | 数据从未被运行过 | 数据真实但引用归属错误 |
| 论文外观 | 看起来像完整的实验论文 | 看起来像严谨的综述 |
| 检测方法 | 搜索项目代码 + 计数引用 | 追溯PDF原文数值 |
| 修复规模 | 整篇论文重写为理论框架 | 仅修复引用归属 |
| 耗时 | ~1次完整写作会话 | 每条引用5-10分钟 |

## Bib 交叉污染症状清单

bib文件中出现以下模式时，提示跨项目污染：

| 模式 | 示例（从BPPV论文中发现） | 来源项目 |
|:-----|:-------------------------|:---------|
| 完全无关主题的论文 | `he2008toward` — "Iris Segmentation" | 虹膜分割论文(PAP-03) |
| 其他项目的作者名 | `yang2024` — 通常是主作者在其他项目的工作 | 另一篇论文 |
| 其他项目的会议名称 | `miccai2024` 出现在前庭论文中 | 医-工交叉项目 |
| DOI前缀与论文主题无关 | `10.1016/j.patcog` 出现在神经科学论文中 | 模式识别项目 |

## 参考

- quality-gate SKILL.md L0.5 数据诚实门
- quality-gate SKILL.md "Type A 扩展检测：全量虚构 vs 局部虚构"
- 会话记录: 2026-05-25 空闲任务推进 cron
