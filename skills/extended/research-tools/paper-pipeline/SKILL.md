---
name: paper-pipeline
category: extended/research-tools
signature: "redirect -> extended/research-tools/research/literature"
description: "REDIRECT — 论文管线已合并至文献统一入口 skills/extended/research-tools/research/literature"
redirect_to: "extended/research-tools/research/literature"
version: 2.0.0
---

# REDIRECT

此技能（论文管线）的功能已完全合并至 **`extended/research-tools/research/literature`**。

`literature.py pipeline` 实现"搜索→下载→报告"完整管线：

```bash
cd /media/yakeworld/sda2/Synthos/skills/extended/research-tools/research/literature/scripts
python3 literature.py pipeline "topic" --sources crossref pubmed openalex --max 15 --output-dir /path/to/results
```

更多细节见 `skill_view(name='extended/research-tools/research/literature')`。
