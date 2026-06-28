---
name: reference-directory-cleanup
description: 论文参考文献目录标准化清理 — 参照3d-eyeball-iris-segmentation标准，将06-references/从混乱状态恢复为扁平结构。
version: 1.0.0
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: "paper_dir: str -> cleaned_dir: dict"
    related_skills:
    - paper-pipeline
    - quality-gate
    - pdf-download-racing
---

# Reference Directory Cleanup

## 目标状态

论文 `06-references/` 目录的标准结构（参照 3d-eyeball-iris-segmentation）：

```
06-references/
├── references.bib          # 当前Bib文件
├── author2023title.pdf     # 每个被引用的Bib key对应一个PDF
├── Collins2015.pdf         # 符号链接
└── pdfs/                   # 空目录（可选保留）
```

**关键规则**：
- PDF 文件名 = Bib key（大小写一致）
- 符号链接处理多部分 Bib key（如 `Collins2015TRIPOD.pdf` → `Collins2015.pdf`）
- **不需要** `pdfs/` 子目录（不再使用时删除）
- **不需要** `pdfs_md/`、`bibkey-map.json`、`notebooklm-sources.json` 等元数据文件
- **不需要** `references.bib.bak` 等备份文件

## 执行流程

### Step 1: 诊断当前状态

```bash
paper_dir="<paper_path>/06-references/"
cd "$paper_dir"

# 列出所有文件
ls -la

# 检查子目录
ls -d */

# 读取当前Bib
grep -oP '@\w+\{\K[^,]+' references.bib

# 检查PDF与Bib的匹配关系
for f in *.pdf; do
    key=$(basename "$f" .pdf)
    grep -q "@${key}," references.bib && echo "MATCH: $f" || echo "ORPHAN: $f"
done
```

### Step 2: 清理根目录非Bib文件

```bash
# 删除不属于当前Bib的文件
bib_keys=$(grep -oP '@\w+\{\K[^,]+' references.bib)
for f in *; do
    [ -d "$f" ] && continue  # 跳过子目录
    is_bib=false
    for key in $bib_keys; do
        [[ "$f" == "$key"* || "$f" == *"$key"* ]] && is_bib=true && break
    done
    if [ "$is_bib" = false ] && [[ "$f" != "*.pdf" ]]; then
        echo "DELETE: $f (not in Bib)"
    fi
done
```

### Step 3: 从子目录提取匹配PDF

```bash
# 从 pdfs/ 子目录提取匹配当前Bib的PDF到根目录
for key in $bib_keys; do
    for f in pdfs/*.pdf; do
        [ -e "$f" ] || continue
        base=$(basename "$f" .pdf)
        if echo "$base" | grep -qi "$key"; then
            cp "$f" "${key}.pdf"
            echo "EXTRACT: pdfs/$f → $key.pdf"
        fi
    done
done
```

### Step 4: 处理名称不匹配

```bash
# 对名称不匹配的Bib key创建符号链接
for key in $bib_keys; do
    # 检查是否有匹配的PDF（大小写不敏感）
    match=$(ls *.pdf 2>/dev/null | grep -i "$key" | head -1)
    if [ -n "$match" ] && [ "$match" != "${key}.pdf" ]; then
        ln -sf "$(basename "$match")" "${key}.pdf"
        echo "LINK: ${key}.pdf → $(basename "$match")"
    fi
done
```

### Step 5: 删除不需要的子目录

```bash
# 删除不再使用的子目录
[ -d "pdfs/" ] && rmdir "pdfs/" 2>/dev/null && echo "DELETED: pdfs/"
[ -d "pdfs_md/" ] && rmdir "pdfs_md/" 2>/dev/null && echo "DELETED: pdfs_md/"
```

### Step 6: 删除备份和元数据文件

```bash
# 删除备份文件
rm -f references.bib.bak*

# 删除元数据文件
rm -f bibkey-map.json notebooklm-sources.json REFERENCE_MANIFEST.md
```

### Step 7: 验证

```bash
# 最终状态检查
echo "=== 最终状态 ==="
echo "PDF/链接数: $(ls -1 *.pdf 2>/dev/null | wc -l)"
echo "Bib条目数: $(grep -oP '@\w+\{\K[^,]+' references.bib | wc -l)"
echo "子目录: $(ls -d */ 2>/dev/null || echo '无')"

# 验证链接
ls -la *.pdf | grep ->
```

## 实战数据（pima-crispdm 2026-06-18）

| 清理项 | 数量 |
|--------|------|
| 根目录删除旧PDF | 7个 |
| 根目录删除旧元数据 | 3个（bibkey-map.json, notebooklm-sources.json, REFERENCE_MANIFEST.md） |
| 删除bak文件 | 5个 |
| 从pdfs复制匹配PDF到根目录 | 8个 |
| 创建符号链接 | 2个 |
| 规范化后根目录PDF/链接 | 18个 |
| Bib总数 | 29个 |

## 注意事项

1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
2. **名称不匹配需要检查内容** — 如 `Shams2025.pdf` vs `Shams2023BRFSS` 需验证内容
3. **3d-eyeball标准**: 45个PDF在根目录 + references.bib + 空pdfs/子目录
4. **Bib清理顺序**：先清理bib中的无效条目，再删除.tex中的残留引用，最后重新编译。详见 `paper-pipeline/SKILL.md`。

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
