# Reference Directory Cleanup — 论文参考文献目录标准化

## 标准结构（参照 3d-eyeball-iris-segmentation）

```
06-references/
├── references.bib          # 当前Bib文件
├── author2023title.pdf     # 每个被引用的Bib key对应一个PDF
├── Collins2015.pdf         # 符号链接
└── pdfs/                   # 空目录（可选保留）
```

**规则**：
- PDF文件名 = Bib key（大小写一致）
- 符号链接处理多部分Bib key（`Collins2015TRIPOD.pdf` → `Collins2015.pdf`）
- 不需要 `pdfs_md/`、`bibkey-map.json`、`notebooklm-sources.json` 等元数据
- 不需要 `references.bib.bak` 等备份文件

## 清理流程

1. **诊断**：`ls -la 06-references/` + 读取Bib key + 检查PDF匹配
2. **清理根目录**：删除不属于Bib的PDF、元数据、备份文件
3. **从子目录提取**：从pdfs/提取与当前Bib匹配的PDF到根目录
4. **处理名称不匹配**：创建符号链接
5. **删除子目录**：删除pdfs_md/等不再使用的子目录
6. **验证**：最终状态检查

## 实战数据（pima-crispdm 2026-06-18）

| 清理项 | 数量 |
|--------|------|
| 根目录删除旧PDF | 7个 |
| 删除元数据 | 3个（bibkey-map.json, notebooklm-sources.json, REFERENCE_MANIFEST.md） |
| 删除bak文件 | 5个 |
| 从pdfs复制匹配PDF | 8个 |
| 创建符号链接 | 2个 |
| 规范化后PDF/链接 | 18个 |

## 注意事项

1. 不要假设子目录PDF都与当前Bib对应 — 旧管线PDF可能不相关
2. 名称不匹配需检查内容 — `Shams2025.pdf` vs `Shams2023BRFSS`
3. 3d-eyeball标准: 45个PDF在根目录 + references.bib + 空pdfs/
