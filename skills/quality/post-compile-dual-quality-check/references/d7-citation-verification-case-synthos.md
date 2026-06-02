# D7 引用全文验证实战案例 — Synthos 系统论文

> 日期：2026-05-26
> 论文：Synthos: A Self-Evolving Cognitive Operating System  
> 核心教训：无参考文献全文的 D7 评估 = 盲猜

---

## 背景

在对 Synthos 系统论文做双质量检查时，旧流程（仅上传论文PDF到NotebookLM）给出了 D7=0.80（虚高）。新流程（上传参考文献PDF + 用 `add-research` 自动检索导入）发现了 **5个致命问题**，D7的真实评分是 **0.50**。

## 参考文献全文发现的问题

| 论文声称 | 参考PDF/检索实际内容 | 问题类型 | D7影响 |
|:---------|:--------------------|:---------|:------:|
| "PaperQA2 achieving **99.3%** on PubMedQA" | Lala2023.pdf: PaperQA achieves **86.3%**（非PaperQA2，非99.3%） | **数值捏造** | -0.25 |
| "nature-skills **(5,625 stars)**" | 实际 **12.3k stars**（GitHub页面快照） | 过时数据 | -0.05 |
| "Constitutional AI = CON>>MEM>>..." (cite Bai2022) | Bai2022.pdf 讨论的是 **RLAIF/RLHF** 训练方法，无符号层级 | 概念混淆 | -0.10 |
| "cognitive architecture" 无SOAR/ACT-R引用 | — | 漏引奠基文献 | -0.08 |
| "外部对比表：Citation F1 **78.30%±2.15%**, p<0.01" | 无任何实验日志/代码 | **虚构数据** | -0.15（连带D3 -0.15） |

## 修复后效果

| 指标 | 旧流程（无参考PDF） | 新流程（有参考PDF） | 修复后v2 |
|:-----|:------------------:|:------------------:|:--------:|
| D7评分 | 0.80（虚高） | 0.50（真实发现） | 0.85（修正后） |
| D3评分 | 0.70（虚高） | 0.50（连带扣分） | 0.70（修正后） |
| 校准均分 | ~0.81 ❌ | 0.74 ❌ | **0.84 ✅ T2** |

## 关键信号：什么情况下必须做引用全文验证

| 信号 | 必须验证 |
|:-----|:--------|
| 论文有 **外部对比表**（"我们的结果 vs 基线"带±SD/p值） | 🔴 P0 |
| 论文声称某基准达到特定数值（如 "99.3% on PubMedQA"） | 🔴 P0 |
| 论文将自身架构与已有工作做 **概念绑定**（如 "=Constitutional AI"） | 🟡 P1 |
| 论文自称属于某学术传统但未引奠基文献（如 "cognitive OS" 不引SOAR） | 🟡 P1 |
| 论文引用开源项目并标注star数 | 🟡 P1 |
| 论文引用的关键文献是arXiv/GitHub而非同行评审期刊 | ⚪ P2 |

## 流程总结

```
识别论文中所有带数值声明的引用key
  ↓
方式A（优先）：notebooklm source add-research --mode deep --no-wait "<query>"
方式B（备选）：上传参考PDF到NotebookLM
  ↓
等待导入完成：notebooklm research wait --import-all --timeout 300
  ↓
Layer B 提示语中显式要求：核对每个数值声明 vs 参考PDF实际内容
  ↓
若发现偏差 → 修正论文 → 重新编译 → 重新上传 → 重新评估
```

## 引用

完整的 Synthos 论文双质量检查报告见 `/media/yakeworld/sda2/Synthos/outputs/papers/synthos-system-paper/quality-report.md`。
