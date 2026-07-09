---
name: knowledge-acquisition
category: core
signature: "redirect -> extended/research-tools/research/literature"
description: "REDIRECT — 知识获取功能已合并至文献统一入口 skills/extended/research-tools/research/literature"
redirect_to: "extended/research-tools/research/literature"
version: 2.1.0
---

# REDIRECT

此技能（知识获取认知原子）的功能已完全合并至 **`extended/research-tools/research/literature`**。

**调用方法：** `skill_view(name='extended/research-tools/research/literature')`

literature 技能包含：
- `literature.py search` — 7源统一检索
- `literature.py download` — PDF下载
- `literature.py pipeline` — 搜索→下载→报告管线
- `literature.py test` — 连通性测试

所有脚本在 `scripts/literature.py`（统一CLI入口），7个数据源适配器，59个参考文档。
