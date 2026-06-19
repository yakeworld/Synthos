# BibTeX D10a 修复工作流（v1 — 2026-06-19）

## 场景

论文参考文献有 ≥60 条（G1 通过），但 D10a（覆盖率）只有 50-60%。原因：bib 条目多但正文中实际引用少。

## 修复步骤

### Step 1: 诊断当前状态

```python
import re, os

tex_path = 'paper.tex'
bib_path = 'references.bib'

# 正文中所有 cite 键
with open(tex_path, 'r') as f:
    tex = f.read()
cites = re.findall(r'\\cite[ps]?\{([^}]+)\}', tex)
all_keys = [k.strip() for c in cites for k in c.split(',')]
unique_cited = set(k for k in all_keys if not k.startswith('<') and k != 'lamport94')

# bib 条目
with open(bib_path, 'r') as f:
    bib = f.read()
bib_entries = set(re.findall(r'@\w+\{(\w+),', bib))

d10a = len(unique_cited & bib_entries) / len(bib_entries)
orphaned = bib_entries - unique_cited
print(f"D10a: {d10a*100:.1f}%")
print(f"Orphaned: {len(orphaned)} entries")
```

### Step 2: 分类孤立条目

按相关性分类孤立条目：

```python
# 高相关：直接关联论文主题
high_relevance = [k for k in orphaned if any(kw in k.lower() for kw in 
    ['daugman', 'he2008', 'tan2010', 'chen', 'feng2022', 'venkateswarlu', 'garbin', 
     'palmero', 'proencca', 'bowyer', 'guestrin', 'huo2021', 'lu2016', 'kuang2022',
     'lee2008', 'lee2012', 'tsukada', 'newman', 'rathnayake', 'yin2023'])]

# 中相关：补充性引用
medium_relevance = [k for k in orphaned if k not in high_relevance]
```

### Step 3: 在 Related Work 中补充引用

**原则：按章节分区补充，不要只在末尾堆砌**

关键补充区域：
1. **Introduction** — 背景/动机段落
2. **Related Work → Traditional Methods** — 经典方法引用
3. **Related Work → Deep Learning Methods** — 深度学习引用
4. **Related Work → 3D Modeling / Eye Tracking** — 领域特定引用
5. **Dataset / Methodology** — 数据和方法论引用

Patch 技巧：每次 patch 用旧字符串作为上下文，确保只修改一处。

### Step 4: 验证修复

```python
# 重新统计
cites_new = re.findall(r'\\cite[ps]?\{([^}]+)\}', open(tex_path).read())
all_keys_new = [k.strip() for c in cites_new for k in c.split(',')]
unique_cited_new = set(k for k in all_keys_new if not k.startswith('<'))
d10a_new = len(unique_cited_new & bib_entries) / len(bib_entries)

assert d10a_new >= 0.85, f"D10a still {d10a_new:.1%} < 85%"
```

## 常见陷阱

1. **`\\citep` vs `\citep`** — patch 后 LaTeX 反斜杠会变成双反斜杠，导致编译失败。必须立即用二次 patch 修正。
2. **Orphan 条目不要全部删除** — 即使不引用，某些条目（如数据集引用、经典方法引用）对学术严谨性重要。保留 ≤6 个孤儿可接受。
3. **不要为了凑数添加无关引用** — 新引用必须在语义上匹配被引用的段落内容。
4. **检查已引用键是否仍在 bib 中** — 补充引用时可能遗漏了某些条目未正确添加到 bib。

## 成功案例

3d-eyeball-iris-segmentation 论文：
- 起始：D10a = 54.1%（33/61），孤儿 = 28
- 经过 7 次 patch，补充 24 处引用位置
- 最终：D10a = 93.4%（57/61），孤儿 = 4
- 质量评分从 81 → 93.5
