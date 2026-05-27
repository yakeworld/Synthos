---
name: dual-quality-check-v2
description: "Synthos D1-D10十维论文双质量检查：Gemini评审+参考文献标准+全文覆盖+引用质量+文件命名"
version: 2.0.0
tags: [quality, review, d1-d10, evolution, synchos]
---

# Dual Quality Check v2 — D1-D10 十维评审

## 十维评审矩阵

| 维度 | 内容 | 方法 | 阈值 |
|------|------|------|------|
| D1 | 科学贡献 | NotebookLM Gemini | ≥0.85 T1 |
| D2 | 方法学严谨性 | NotebookLM Gemini | ≥0.85 T1 |
| D3 | 结果可信度 | NotebookLM Gemini | ≥0.85 T1 |
| D4 | 完整性 | NotebookLM Gemini | ≥0.85 T1 |
| D5 | 清晰性 | NotebookLM Gemini | ≥0.85 T1 |
| D6 | 新颖性 | NotebookLM Gemini | ≥0.85 T1 |
| D7 | 引用质量 | NotebookLM Gemini | ≥0.85 T1 |
| **D8** | **参考文献数量** | .bib / .tex 条目计数 | **≥30篇** |
| **D9** | **全文覆盖率** | 已下载PDF / .bib中DOI数 | **≥0.80** |
| **D10** | **引用质量** | NotebookLM发现未引用高质量文献 | **人工评估** |

**最终评分 = avg(D1-D10中可获取的维度)**

## 文件命名规范

```
强制格式: {论文目录名}-v{版本号}.pdf
          e.g. pd-dysphagia-2026-v1.pdf
禁止:     paper.pdf (覆盖/冲突风险)
```

## 进化数据

每次运行 `qc_v2_d1d10.py` 自动追加到 `outputs/papers/qc-evolution.json`：
```json
[
  {"timestamp": "2026-05-28T00:30", "results": {"paper": {"tier": "T1", "final": 0.93, ...}}}
]
```

## D9 全文覆盖率

检查.pdfs/目录中已下载PDF数 / .bib中DOI数。
**注意**：参考PDF可能存放在 `pdfs/` 或 `enhanced_refs/pdfs/` 下，质检应扫描两个路径。

```bash
# 统一PDF存储位置
find <paper_dir> -path "*/enhanced_refs/pdfs/*.pdf" -exec cp {} <paper_dir>/pdfs/ \;

# 单DOI下载
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
MEDDATA_USERNAME="wzsrmyy" MEDDATA_PASSWORD="..." python3 download_one.py <doi> <output.pdf>
```

## D10 引用质量检查（NotebookLM）

```bash
notebooklm use <project_id>
notebooklm ask "List 3-5 high-impact papers NOT cited in {paper}-v1 but should be."
```

## 进化循环（GEPA）

```
Gather (发现问题) → Extract (提取规律) → Pattern (形成技能) → Apply (再次应用)
                              ↕
                         Evolution Log
```

每次质检发现问题→更新技能→记录进化路径→下次质检适用新标准。

## 陷阱

1. **`_fetch_semantic_scholar_data_sync` 可能是空桩** — paper-manager 中此方法原为 `return entry` 不做任何查表。若增强.bib时无元数据补充，检查此方法是否已实现SS API调用。
2. **D10取决于NotebookLM项目文献源** — 源数过少时Gemini无法推荐有效未引用论文。补充文献后再跑D10。
