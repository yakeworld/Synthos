# NotebookLM 源文件去重

> **2026-05-23 更新**：NotebookLM CLI v0.5.0 已内置 `source clean` 命令，自动检测并删除重复/错误/不可用 source。此脚本保留为备用方案。

## 推荐方案：`source clean`（内置命令）

```bash
# 预览（不删除）
notebooklm source clean -n <notebook_id> --dry-run

# 执行清理
notebooklm source clean -n <notebook_id> -y

# JSON 格式输出（便于程序化处理）
notebooklm source clean -n <notebook_id> --dry-run --json
```

**优点**：自动处理所有类型（重复、错误、访问受限），以 10 个一批次避免限流。

## 备用方案：手动去重脚本

当 `source clean` 不可用（旧版 CLI）时使用。

**场景**：`add-research --import-all` 可能导入大量重复来源。Notebook 有 source 数量上限。

**验证**：2026-05-23 实战：Synthos Notebook 228→111 sources（删 117 重复）。

### 去重策略

同标题保留最早创建的一个，删除其余。

### Python 脚本

```python
#!/usr/bin/env python3
"""Deduplicate NotebookLM sources - keep first, delete rest."""
import asyncio, sys
from collections import defaultdict

sys.path.insert(0, '/home/yakeworld/.local/share/pipx/venvs/notebooklm-py/lib/python3.12/site-packages')
from notebooklm.auth import AuthTokens
from notebooklm.client import NotebookLMClient

NB = "<notebook_id>"  # 替换为实际 Notebook ID

async def main():
    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        sources = await client.sources.list(NB)
        print(f"Total: {len(sources)}")
        
        groups = defaultdict(list)
        for s in sources:
            groups[s.title.strip() or "(untitled)"].append((s.id, s.created_at))
        
        deleted = 0
        for title, items in groups.items():
            if len(items) > 1:
                items.sort(key=lambda x: x[1] or "")
                for sid, _ in items[1:]:
                    await client.sources.delete(NB, sid)
                    deleted += 1
                    await asyncio.sleep(0.3)  # Rate limit
        
        remaining = await client.sources.list(NB)
        print(f"Deleted: {deleted}")
        print(f"Remaining: {len(remaining)}")

asyncio.run(main())
```
