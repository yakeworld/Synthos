# Multi-Version .tex File Verification — 2026-05-31 实战

## 场景

批量 D8/D10a 扫描显示某论文异常（如 bppv-otoconia-simulation: D8=32, D10a=25%），
但上一轮已知此论文已被修复（D10a=100%）。

## 根因

论文目录有多个 `.tex` 文件，脚本聚合了所有文件的引用：
- `article.tex`（旧版，287行）～ 10 条引用，2 个孤儿引用
- `article_improved.tex`（新版，573行）～ 32 条引用，0 个孤儿引用

旧版引用未被清理的 bib 条目 → 产生大量僵尸条目 → D10a 虚低。

## 验证技术

```python
import re, os

pd = '/path/to/paper-dir'

# 1. 列出所有 .tex 文件
for root, dirs, files in os.walk(pd):
    for f in files:
        if f.endswith('.tex'):
            fp = os.path.join(root, f)
            print(f'  {fp} ({os.path.getsize(fp)} bytes)')

# 2. 对每个文件分别算 D10a
for fname in ['article.tex', 'article_improved.tex']:  # 也可用 glob
    fp = os.path.join(pd, fname)
    if not os.path.isfile(fp):
        continue
    
    tex = open(fp).read()
    lines = [l for l in tex.split('\n') if not l.strip().startswith('%')]
    active = '\n'.join(lines)
    
    cites = set()
    for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', active):
        for k in m.group(1).split(','):
            cites.add(k.strip())
    
    bib = open(os.path.join(pd, 'references.bib')).read()  # 适配路径
    bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib))
    
    orphan = cites - bib_keys
    zombie = bib_keys - cites
    d10a = 100.0 * len(cites & bib_keys) / len(bib_keys) if bib_keys else 0
    
    print(f'{fname}:')
    print(f'  Cited: {len(cites)}, Bib: {len(bib_keys)}')
    print(f'  Orphan: {len(orphan)}, Zombie: {len(zombie)}')
    print(f'  D10a: {d10a:.0f}%')

# 3. 选择引用计数多、孤儿少的版本作为真实活跃版本
```

## 判断规则

| 指标 | 旧版特征 | 活跃版特征 |
|:-----|:---------|:-----------|
| 文件大小 | 小（如 8KB） | 大（如 26KB） |
| 引用数 | 少（~10） | 多（~32） | 
| 孤儿引用 | 有（引用了已删除的 bibkey） | 无 |
| 文件名提示 | article.tex / v2-paper.tex | article_improved.tex / v4-paper.tex |

## 实战验证

| 论文 | 旧版 | 活跃版 | 旧版 D10a | 活跃版 D10a |
|:-----|:-----|:-------|:---------:|:-----------:|
| bppv-otoconia-simulation | article.tex (287行) | article_improved.tex (573行) | 25% | 100% |
| scc-mathematical-morphology | v2-paper.tex (45KB) | v4-paper.tex (44KB) | — | 100% |

## 修复

`bulk_d8_scan.py` v2.0 使用优先级文件选择：

```python
priority_order = [
    'article_improved.tex',  # 最优先
    'v4-paper.tex',          # 最新主版本
    'paper.tex',             # 通用
    'main.tex',              # 通用
    'article.tex',           # 旧版后备
]
```

选出的文件显示在 `Active .tex` 列，便于手动验证。
