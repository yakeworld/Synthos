# SCC论文引用修正实战 — 2026-05-30

> `scc-mathematical-morphology` 论文 D10a=100% 但发现4个深层引用问题

## 问题清单

| BibKey | 问题类型 | 严重度 | 原文 | 修正后 |
|:-------|:---------|:------:|:-----|:-------|
| Smith2021 | φ虚构引用 | 🔴 | PLoS One 16 e0248560 | 删除（所有数据库查无此文） |
| Damiano1996 | 期刊/标题全错 | 🔴 | Ann Biomed Eng 24:136-149 | J Fluid Mech 307:333-372 |
| Boselli2014 | 标题不符 | 🟡 | "computational model...otoconia settling" | J Biomech 47:1853-1860 |
| Epp2010 | 冗余引用 | 🟢 | 教科书 | 删除（Manoussaki2008已覆盖） |

## 验证方法

每个条目均通过 OpenAlex API 验证：
```bash
curl -s "https://api.openalex.org/works/doi:10.1017/s0022112096000146" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('title',''))"
```

## 修复步骤

### 1. 定位所有引用位置
```bash
grep -n 'Smith2021' v4-paper.tex
# 两个位置：\cite{} in text + \bibitem{} in thebibliography
```

### 2. 删除虚构引用
```python
# text中的\cite: 用 sed 或 .replace()
content = content.replace(r'\cite{Wimmer2019,Sieber2019,Smith2021,Chacko2018}',
                          r'\cite{Wimmer2019,Sieber2019,Chacko2018}')
# bibitem: 直接删除整行
```

### 3. 修正错误记录（保留bibkey不变）
```python
# 只改journal/title/volume/pages，保留bibkey
# 这样\cite{Damiano1996}无需改动
```

### 4. 空行清理
```python
import re
with open('v4-paper.tex') as f: content = f.read()
# 压缩连续3+空行为2空行
content = re.sub(r'\n{3,}', '\n\n', content)
with open('v4-paper.tex', 'w') as f: f.write(content)
```

### 5. 编译验证
```bash
pdflatex v4-paper.tex  # 第一轮：可能有natbib警告
pdflatex v4-paper.tex  # 第二轮：0 undefined
```

### 6. 引用数验收
```bash
grep -c 'Smith2021' v4-paper.tex  # 应为0
```

### 7. REFERENCE_MANIFEST同步
- 更新 `06-references/REFERENCE_MANIFEST.md`
- 记录每条修正的验证来源

### 8. 提交包同步
```bash
cp 01-manuscript/v4-paper.pdf 02-submission/manuscript-v4.pdf
cp 01-manuscript/v4-paper.pdf 02-submission/manuscript.pdf
```

## 坑

- **patch工具在LaTeX上的局限**：`skill_manage(action='patch', ...)` 在含有`\cite`的LaTeX行上经常失败（因为`\\\\`转义问题）。改用`python3`的`content.replace()`或`sed -i`处理。
- **删除后的上下文验证**：Smith2021在`\cite{Wimmer2019,Sieber2019,Smith2021,Chacko2018}`中——确认删除后剩余3篇引用在逻辑上仍然完整。
- **引用数变动**：43→41篇（-2），bibitem编号自动重排，LaTeX自动处理。
