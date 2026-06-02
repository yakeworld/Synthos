# SCC论文引用质量检查报告（实战范例 2026-05-30）

> 34篇引用，100%有真实全文PDF，100%在正文中有明确引用位置。
> 报告生成脚本: `07-quality/ref-citation-quality-report.md`

## 报告结构

```
# 首部 — 元信息（论文标题、版本、总数、PDF覆盖率）
| # | BibKey | PDF | 类型 | 引用位置 | 引用依据 |
|---|--------|:---:|:-----|:---------|:---------|
| 1 | Boselli2014 | ✅ | clinical BPPV | Discussion | 提供计算模型参考框架 |
| 2 | Bradshaw2010 | ✅ | computational modeling | Introduction | 提供形态测量对比基准 |
...

## 逐篇详细分析
### 1. Boselli2014
- 条目: F. Boselli, et al., Quantitative analysis of BPPV fatigue...
- 全文: ✅ 本地PDF已验证
- 引用次数: 1 处
- 引用位置:
  - [Discussion] L351: `...Previous computational models of BPPV mechanics \cite{Squires2004, Boselli2014}...`
- 知识点:
  - BPPV仿真方法背景——前人BPPV模型假设恒定半径圆形/椭圆管几何
- 引用依据: 提供BPPV计算模型参考框架

## 总结
| 指标 | 值 | 判定 |
| 总引用数 | 34 | ✅ ≥30 |
| 有PDF全文 | 34 (100%) | ✅ ≥80% |
```

## 每篇需核查的维度

1. **BibItem元数据** — 作者/标题/期刊/卷/页必须与数据库一致（OpenAlex验证）
2. **PDF真实性** — 读取前5字节确认`%PDF-`，排除HTML伪装
3. **引用位置** — 在正文中找到每个`\cite{}`的位置，确认上下文适当
4. **知识点** — 该引用支撑本文的哪个具体论述/数据/方法
5. **引用依据** — 为何选这篇而不是其他同类文献
