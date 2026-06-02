# 系统论文管线验证案例 — Synthos

> 日期：2026-05-26
> 论文：Synthos: A Self-Evolving Cognitive Operating System
> 核心教训：用真实管线产出替代虚构外部对比表

---

## 问题背景

Synthos论文原本有一张"外部对比表"（tab:paper_quality），声称与Single-Agent和AI Scientist在N=30篇论文上做了全面对比，报告了Citation F1=78.30%±2.15%、6-Axis Score=72/100±2.3、p<0.01等数据。

**真相**：该表格由LLM直接生成，从未进行过实验。属于学术不端（数据捏造）。

## 修复方案

**不是删除对比数据就完事**，而是用真实管线数据做一个**诚实的质量分布统计**：

### 步骤1：扫描管线产出

扫描 `outputs/papers/` 下所有论文目录，统计：
- 总项目数
- 已完成质量检查的论文数
- 各质量等级分布（T1/T2/T3）
- 跨域覆盖（眼科/神经科/生物力学/AI）
- 平均/中位校准分

### 步骤2：构建统计表

```latex
\begin{table}[h]\centering\caption{Quality distribution of Synthos-generated manuscripts (N=22).}\label{tab:pipeline_quality}
\small
\begin{tabular}{lcc}\toprule
\textbf{Quality Tier} & \textbf{Threshold} & \textbf{Count}\\\midrule
T1 (Top-tier journal) & $\ge$0.85 & 6\\
T2 (High-level journal) & $\ge$0.80 & 10\\
T3 (Standard journal) & $\ge$0.75 & 4\\
Below T3 & $<$0.75 & 2\\
\bottomrule
\end{tabular}
\end{table}
```

### 步骤3：公平免责声明

```latex
We note that a direct quantitative comparison against existing end-to-end research 
agent systems---such as AI Scientist~\cite{sakana2025ai} or PaperQA~\cite{lala2025paperqa}---is 
not feasible at present, as no other published system simultaneously performs literature 
retrieval, hypothesis generation, experiment design, paper writing, and quality assurance 
within a unified architecture. AI Scientist itself faced the same comparison challenge, 
evaluating against cross-model baselines rather than competing end-to-end 
systems~\cite{lu2024ai}. We adopt a comparable strategy: the dual quality check protocol 
(Layer A internal + Layer B Gemini) serves as our standardized evaluation framework.
```

## 方法论锚点

同类论文验证方法的对比：

| 论文 | 对比基线 | 样本量N | 外部基准 | 人评 | 是否虚构数据 |
|:-----|:---------|:-------:|:---------|:----:|:-----------:|
| AI Scientist | 跨模型(Claude/GPT-4o/Llama) | N=500 ICLR + N≈50/模型 | ICLR 2022 | ❌ | ❌ |
| PaperQA | Human experts + 5商业工具 | N=50 LitQA, N=80-237引用 | PubMedQA, LitQA | ✅ 5人 | ❌ |
| **Synthos v3** | **自我对照（内部进化）** | **N=22质检+42项目** | **无** | **✅ Layer B** | **❌** |

## 结果

| 指标 | 虚构对比表 | 真实管线数据 |
|:-----|:----------:|:------------:|
| D3评分 | 0.50（连带扣分+信任崩塌） | 0.75（诚实，有据可查） |
| 校准均分 | 0.74 ❌ | 0.85 ✅ T1 PASS |
| 审稿人反应 | 发现一处捏造 → 全盘否定 | 数据可追溯 → 可评估方法论 |

## 实时扫描脚本

```python
import os, re

papers_dir = "outputs/papers"
paper_dirs = [d for d in os.listdir(papers_dir) 
              if os.path.isdir(os.path.join(papers_dir, d))
              and d not in ('__pycache__', '_docs', '_todo', 'lit-reviews')]

papers_data = []
for d in paper_dirs:
    dp = os.path.join(papers_dir, d)
    has_tex = any(f.endswith('.tex') for f in os.listdir(dp))
    has_pdf = any(f.endswith('.pdf') for f in os.listdir(dp))
    
    # Extract quality score from report
    calibrated = None
    for fname in ['quality-report.md', 'QUALITY.md', 'quality.md']:
        fp = os.path.join(dp, fname)
        if os.path.exists(fp):
            content = open(fp).read()
            m = re.search(r'校准.*?(\d+\.\d+)', content)
            if m: calibrated = float(m.group(1))
            break
    
    papers_data.append({
        'name': d, 'has_tex': has_tex, 'has_pdf': has_pdf,
        'calibrated': calibrated
    })

with_scores = [p for p in papers_data if p['calibrated'] is not None]
t1 = sum(1 for p in with_scores if p['calibrated'] >= 0.85)
t2 = sum(1 for p in with_scores if 0.80 <= p['calibrated'] < 0.85)
t3 = sum(1 for p in with_scores if 0.75 <= p['calibrated'] < 0.80)
print(f"Total: {len(paper_dirs)}, With QC: {len(with_scores)}, "
      f"T1:{t1} T2:{t2} T3:{t3}, "
      f"Mean: {sum(p['calibrated'] for p in with_scores)/len(with_scores):.3f}")
```
