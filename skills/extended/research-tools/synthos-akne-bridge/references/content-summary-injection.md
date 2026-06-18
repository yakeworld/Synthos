# Source Node Content Summary Injection

## 2026-06-13 实施记录

为 AKNE 图谱中全部 1145 个 source 节点注入内容摘要。

## 注入结构

每个 source 节点 metadata 包含:
- `content_summary`: 结构化摘要（H1 + H2[:2] + [科学假设] + [开放问题] + 前100词）
- `content_hash`: MD5(content[:500])
- `word_count`: 文件词数
- `has_hypothesis`: boolean
- `has_open_question`: boolean
- `h1`, `h2_first`

## 执行结果

- 1145/1145 source 全部更新
- graph.json 从 2MB → 2.87MB（+43%）
- 0 未找到，0 空文件

## 注意事项

- 仅截取前 3KB，长文件丢失后部
- 手动执行，未来需集成到 ingest 管线
- embedding 单独存入 vectors.db

## 相关

- 向量化: `references/vectorization-completion.md`
- 桥接脚本 full 模式依赖 content_summary 做图内内容搜索