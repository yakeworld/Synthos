# Synthos System Paper — thebibliography D10a 修复实战（2026-06-01）

## 背景

`synthos-system-paper`（32页系统级论文）使用 `\begin{thebibliography}` 模式（非 .bib 文件）。扫描发现：

| 指标 | 值 | 状态 |
|:-----|:---|:-----|
| D8 (bibitem 计数) | 37 | ✅ ≥30 |
| D10a (匹配率) | 33/37 = 67% | ❌ FAIL |
| 孤儿引用 (cite 无 bibitem) | 16 | 必须修复 |
| 僵尸 bibitem (有 bibitem 无 cite) | 4 | 需清理 |

## 修复过程

### Step 1: 僵尸→引用改名（3处）

匹配僵尸 bibitem 与孤儿 cite key 的差异，发现 3 处实为同一论文但 key 格式不同：

| 僵尸 key (bibitem 有, cite 无) | 引用 key (cite 有, bibitem 无) | 修复 |
|:-----------------------------|:-----------------------------|:-----|
| `ars2026academic` | `ars2025academic` | 改年 2026→2025, 保持 ARS Team 作者 |
| `loc2025kilo` | `vo2025kilo` | 改 author 前缀 loc→vo (V. D. Loc) |
| `yang2026aris` | `haiyang2025aris` | 改 author 前缀+年 yang→haiyang, 2026→2025 (H. Yang) |

修复方法（skill_manage action='patch'）：
```
\bibitem{ars2026academic} → \bibitem{ars2025academic}
\bibitem{loc2025kilo}    → \bibitem{vo2025kilo}
\bibitem{yang2026aris}   → \bibitem{haiyang2025aris}
```

### Step 2: 删除 1 个真僵尸

`gao2024scientific` — bibitem 存在但从未被引用，且无对应 cite key。直接删除整个 bibitem 条目。

### Step 3: 新增 13 个缺失 bibitem

在 `\end{thebibliography}` 前插入：

```
alsadi2023prediction   — CKD prediction thesis
anderson2004actr       — ACT-R cognitive architecture (Psych. Review)
anthropic2025claude    — Claude 3.5 Sonnet model card
crewai2024crewai       — CrewAI framework
futurehouse2025paperqa2 — PaperQA2
gupta2021comparative   — Gupta comparative ML study
hong2023metagpt        — MetaGPT (arXiv:2308.00352)
laird2012soar          — Soar cognitive architecture (MIT Press)
mukherjee2023orca      — ORCA distributed DL system (arXiv:2310.01234)
sakana2025ai           — AI Scientist (arXiv:2408.06292)
shinn2023reflexion     — Reflexion agent (arXiv:2303.11366)
significantgravitas2023autogpt — AutoGPT
wang2023voyager        — Voyager embodied agent (arXiv:2305.16291)
```

### Step 4: 更新计数器

```python
count = len(re.findall(r'\\bibitem\{', tex))
tex = re.sub(r'\\begin\{thebibliography\}\{\d+\}',
             rf'\\begin{{thebibliography}}{{{count}}}', tex)
# 37 → 49
```

### Step 5: 编译验证（thebibliography 模式）

```bash
# 第一遍 — 所有新引用报 "undefined"（正常，正在写 .aux）
cd outputs/papers/synthos-system-paper
pdflatex -interaction=nonstopmode synthos-paper.tex
# → 29 "undefined" warnings (全部预期)

# 第二遍 — 交叉引用解析完成
pdflatex -interaction=nonstopmode synthos-paper.tex  
# → 0 undefined, 0 errors, 32 pages, 582KB PDF
```

### Step 6: 同步 companion .bib

`synthos-paper.bib` 也包含 thebibliography 内容（从 .tex 拆分出的引用副本）。同步：

```python
start = tex.find(r'\begin{thebibliography}')
end = tex.find(r'\end{thebibliography}')
with open('synthos-paper.bib', 'w') as f:
    f.write(tex[start:end+len(r'\end{thebibliography}')] + '\n')
```

## 最终结果

| 指标 | 修复前 | 修复后 |
|:-----|:------:|:------:|
| D8 (bibitem 数) | 37 | 49 |
| D10a (匹配率) | 67% | **100%** ✅ |
| 孤儿引用 | 16 | **0** |
| 僵尸 bibitem | 4 | **0** |
| 编译 | ✅ 32pp | ✅ 32pp |

## 关键教训

1. **thebibliography 模式不需要 bibtex** — 只需 `pdflatex × 2`。第一遍全部报 "undefined" 是正常现象。
2. **优先改名而非新增+删除** — 3 处僵尸/引用同名不同 key 的情况，改名校验 bibitem 内容即可，零开销。
3. **必须同步 companion .bib** — 当 .bib 文件也含 thebibliography 内容时，不同步则下次从 .bib 编译时修复丢失。
4. **Python `str.replace` 在 patch 中更可靠** — 批量新增 bibitem 用 replace 追加比逐条 patch 更简单。
5. **更新 `{N}` 计数器** — 容易遗忘，不更新会导致 TeX 分配错误空间，编译警告但不报错。
