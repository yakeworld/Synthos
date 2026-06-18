# 参考文献目录标准化模式 — 参照3d-eyeball-iris-segmentation（2026-06-18 实战）

## 标准结构

```
06-references/
├── references.bib          # Bib文件（当前Bib的唯一来源）
├── author2023title.pdf     # PDF文件名 = Bib key（如 Chawla2002.pdf）
├── Collins2015TRIPOD.pdf   # 符号链接 → Collins2015.pdf
├── Lundberg2017SHAP.pdf    # 符号链接 → Lundberg2017.pdf
└── (空 pdfs/ 子目录可选)
```

## 核心规则

1. **根目录扁平化**: PDF + .bib 直接在根目录，不嵌套子目录
2. **PDF名 = Bib key**: 大小写一致（如 `Chawla2002.pdf`）
3. **多部分Bib key**: 如 `Collins2015TRIPOD` → 实际PDF为 `Collins2015.pdf`，符号链接 `ln -sf Collins2015.pdf Collins2015TRIPOD.pdf`
4. **不需要子目录**: pdfs/、pdfs_md/ 为空或删除
5. **不需要元数据**: bibkey-map.json、notebooklm-sources.json、REFERENCE_MANIFEST.md 全部删除
6. **不需要备份**: references.bib.bak* 全部删除

## 清理流程

```bash
Step 1: 从根目录删除所有不属于当前Bib的文件
  → 对每个文件，grep references.bib看是否有匹配key，无匹配则删除

Step 2: 从pdfs/子目录提取匹配PDF到根目录
  → 对每个bib key，在pdfs/中找case-insensitive匹配
  → 匹配的PDF复制到根目录

Step 3: 对名称不匹配的Bib key创建符号链接
  → ln -sf Collins2015.pdf Collins2015TRIPOD.pdf

Step 4: 删除不再使用的子目录
  → 删除pdfs/（若空或不再被使用）
  → 删除pdfs_md/

Step 5: 删除元数据文件
  → 删除bibkey-map.json、notebooklm-sources.json、REFERENCE_MANIFEST.md

Step 6: 删除备份文件
  → 删除references.bib.bak*
```

## 注意事项

- 旧管线PDF可能完全不相关，不要假设pdfs子目录中的PDF都对应当前Bib
- 名称不匹配（如 `Shams2025.pdf` vs `Shams2023BRFSS`）需要检查内容
- 3d-eyeball标准: 45个PDF + references.bib + 空pdfs/子目录 = 46项
- 缺失PDF的Bib key标记为需下载，不计入D10a计算
