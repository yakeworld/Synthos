# DOI交叉验证实战 — SCC论文 (2026-05-30)

## 背景

SCC论文从手写 `thebibliography`（34篇，无DOI）转换为 `.bib` 文件后，手动添加了DOIs。用Crossref API逐条验证后发现 **24% (8/34) 的DOI指向了错误论文**。

## 验证方法

### 1. PDF元数据提取

```python
import os, subprocess

pdf_dir = '/path/to/pdfs'
for f in sorted(os.listdir(pdf_dir)):
    if not f.endswith('.pdf'): continue
    fp = os.path.join(pdf_dir, f)
    # 验证真实性
    with open(fp, 'rb') as fh:
        if fh.read(5) != b'%PDF-': continue
    
    # pdfinfo提取元数据
    info = subprocess.run(['pdfinfo', fp], capture_output=True, text=True, timeout=10)
    
    # pdftotext提取第一页（含标题/作者/期刊）
    first = subprocess.run(['pdftotext', '-f', '1', '-l', '1', fp, '-'], 
                          capture_output=True, text=True, timeout=30)
    
    # 提取DOI
    doi = re.search(r'10\.\d{4,}/[^\s"]+', info.stdout + first.stdout)
```

### 2. Crossref API交叉验证

```python
import json, urllib.request

url = f"https://api.crossref.org/works/{doi}"
req = urllib.request.Request(url, headers={'User-Agent': 'Paper/1.0'})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
msg = data['message']

cr_title = (msg.get('title', [''])[0] or '').lower()[:30]
our_title = bib_title.lower()[:30]

if cr_title != our_title:
    print(f"⛔ DOI points to WRONG paper: Crossref='{cr_title}' vs Bib='{our_title}'")
```

### 3. 用标题搜索正确DOI

```python
import urllib.parse
query = urllib.parse.quote(f"author year keyword title")
url = f"https://api.crossref.org/works?query={query}&rows=5"
# 检查前3个结果，用标题前50字符匹配找正确条目
```

## 发现的错误DOI

| bib条目 | DOI（手写） | 指向论文 | 正确DOI | 正确论文标题 |
|:--------|:------------|:---------|:---------|:-------------|
| Chang2013 | 10.1016/j.ydbio.2013.11.003 | Secretory competence in a gateway endocrine cell | 10.1006/dbio.1999.9457 | Ectopic Noggin blocks sensory and nonsensory organ morphogenesis |
| Geng2013 | 10.1242/dev.097733 | FGF signaling sustains odontogenic fate | 10.1242/dev.098061 | Semicircular canal morphogenesis requires gpr126 |
| Rabbitt1993 | 10.1007/BF00201456 | Mg4Ga8Ge2O20: mineral analog | 10.1007/s004220050536 | Directional coding...vestibular semicircular canals |
| Fritzsch2006 | 10.1016/j.heares.2006.05.010 | Nonlinear properties of otoacoustic emissions | 10.1016/S0361-9230(01)00558-5 | Evolution and development of the vertebrate ear |
| Squires2004 | 10.1016/j.jbiomech.2004.03.019 | Effects of helium-oxygen on endotracheal tubes | (同DOI, 标题不同) | Clinical implications of...BPPV |

## 根因

手动编写bibitem时，DOI是从已知DOI列表"猜测"匹配的。没有去实际验证DOI指向的论文是否与bibitem标题一致。

## 教训

**永远不要信任手动写入的DOI**。每添加一个DOI，必须：
1. 用Crossref API验证该DOI指向的论文标题与bibitem标题匹配
2. 验证期刊名、年份、卷页也匹配
3. 有PDF的话从PDF元数据中提取DOI作为参考
