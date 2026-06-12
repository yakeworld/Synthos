# BibTeX DOI 审计与修复参考

> 双质检 D7 < 0.80 的常见客观原因：引用元数据错误

## 常见错误类型

### 类型 A：重复 DOI
**现象**：两条不同论文的 bib 条目有完全相同 DOI
**检测**：`grep -oP 'doi\s*=\s*\{[^}]+\}' references.bib | sort | uniq -d`
**修复**：对每个重复 DOI：
1. 用 `pdfinfo` 检查两篇 PDF 是否相同
2. 确认哪条是正确的，哪条是错误复制的
3. 对错误条目：删除 DOI 行（或查正确的 DOI 替换）

### 类型 B：期刊名与 DOI 前缀不匹配
**现象**：DOI 前缀（如 `10.1109/` = IEEE）与期刊名（如 "Mobile Information Systems" = Hindawi）矛盾
**检测**：抽查 DOI 前缀与期刊出版商的一致性：
| 前缀 | 出版社 |
|:-----|:-------|
| `10.1109/` | IEEE |
| `10.1016/` | Elsevier |
| `10.1007/` | Springer |
| `10.1155/` | Hindawi |
| `10.1038/` | Nature |
**修复**：查对该论文的正确 DOI，更新 bib 条目

### 类型 C：缺失 DOI
**现象**：会议论文或期刊文章无 DOI 字段
**检测**：`grep -c '^@' refs.bib && grep -c 'doi\s*=' refs.bib` — 如果 bib 条目数远大于有 DOI 的条目数
**修复**：IEEE/Springer 论文大多可通过 DOI.org 查询

### 类型 D：PDF 文件与 bib 条目不匹配

## ⭐ 类型 E：LLM 生成的假 DOI（2026-05-31 新发现）

**现象**：DOI 格式完全正确（如 `10.1016/j.compbiomed.2025.109456`），期刊前缀匹配，但该 DOI 在 Crossref/SS/PubMed 中不存在。对应 bib 条目也是 LLM 虚构的。

**与类型B的区别**：类型B的DOI真实存在但前缀选错；类型E的DOI不存在，整条条目虚构。

**检测**：逐条 Crossref API 验证：
```bash
grep -oP 'doi\s*=\s*\K\{[^}]+\}' references.bib | tr -d '{}' | while read doi; do
  status=$(curl -s --max-time 8 "https://api.crossref.org/works/$doi" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','ERROR'))")
  echo "$doi => $status"
done | grep -v 'ok'
```

**额外标题一致性检查**（DOI存在但指向其他论文）：
```bash
curl -s "https://api.crossref.org/works/10.xxxx/xxxxx" | python3 -c "
import sys,json; m=json.load(sys.stdin).get('message',{})
t=(m.get('title',[''])[0] or '')[:30]; print(t)
"
```

**修复**：
- 假 DOI → SS 搜索 bib 标题 → 要么找到真实论文修正 DOI，要么删除条目
- DOI 存在但标题不匹配 → 修正 bib 中的 DOI 或删除条目
- 替换来源优先从已有 PDF 的参考文献列表挖掘

**实战统计**（pima-crispdm 2026-05-31）：45 条中 15 条假 DOI (33%) + 2 条 DOI 真实但指向其他论文。
**现象**：`pdfinfo` 返回的元数据（标题/作者）与 bib 条目中的不符
**检测**：
```bash
# 对每个有 file= 的 bib 条目，检查 pdfinfo 元数据
for bibkey in $(grep -oP '^\@\w+\{(\K[^,]+)' references.bib); do
  pdf=$(grep -A10 "^@.*{$bibkey," references.bib | grep 'file\s*=' | grep -oP '\{[^}]+\}')
  if [ -n "$pdf" ]; then
    echo "$bibkey → $(pdfinfo "${pdf//:/}" 2>/dev/null | grep 'Title:' | head -1)"
  fi
done
```
**修复**：删除错误的 `file=` 行，添加 `% NOTE: PDF needs verification`

## 快速审计脚本

```bash
# 1. 全文引用数
echo "总引用实例: $(grep -oP '\\cite[pt]?\{[^}]+\}' paper.tex | wc -l)"

# 2. 唯一引用数
echo "唯一引用: $(grep -oP '\\cite[pt]?\{[^}]+\}' paper.tex | tr ',' '\n' | sed 's/cite[pt]*{//' | sort -u | wc -l)"

# 3. Bib 条目数 vs 有 DOI 的条数
bib_count=$(grep -c '^@' references.bib)
doi_count=$(grep -c 'doi\s*=' references.bib)
echo "Bib 条目: $bib_count, 有 DOI: $doi_count (覆盖率: $(echo "scale=1; $doi_count*100/$bib_count" | bc)%)"

# 4. 重复 DOI 检查
dups=$(grep -oP 'doi\s*=\s*\{[^}]+\}' references.bib | sort | uniq -d)
if [ -n "$dups" ]; then echo "⚠️ 重复 DOI:"; echo "$dups"; else echo "✅ 无重复 DOI"; fi

# 5. DOI 前缀抽查（仅检查已知模式）
echo "--- DOI 前缀分布 ---"
grep -oP 'doi\s*=\s*\{10\.\d+/\K[^}]+' references.bib | grep -oP '^[^0-9]+' | sort | uniq -c | sort -rn
```

## 实战案例（2026-05-26）

**3D Eyeball Model-Constrained Iris Segmentation** 论文 bib 文件修复：
1. `proencca2010iris` 与 `wang2002study` 共享相同 DOI `10.1016/j.imavis.2009.03.003`
   - pdfinfo 确认 `wang2002study.pdf` 实际是 Proença 的论文
   - 修复：删除 `wang2002study` 的错误 DOI 和 file 行
2. `li2019efficient` 期刊为 "Mobile Information Systems"（Hindawi），但 DOI 为 `10.1109/ISMAR55827.2022.00053`（IEEE ISMAR）
   - 修复：DOI 更正为 `10.1155/2019/4568929`（Hindawi 格式）
   - 原始 ISMAR DOI 移至 `lu2022neural`（正确的论文）
3. `lu2022neural` 无 DOI 字段
   - 修复：补充 `doi = {10.1109/ISMAR55827.2022.00053}`
