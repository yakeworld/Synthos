# PDF内容验证陷阱（2026-05-27 实战）

## 核心陷阱：文件名≠内容

**症状**：`PDF文件名暗示论文A`，但 `pdftotext` 提取的真实标题是论文B。

**根因**：LLM生成引用下载命令时，arXiv ID/DOI被写错或混淆，下载了错误论文但保留了正确文件名。

## 验证流程

### 方法1：pdftotext（最快）

```bash
# 快速提取前5行确认真实内容
pdftotext suspect.pdf - 2>/dev/null | head -5 | tr '\n' ' '
# 第一行通常是标题，第二行是arXiv ID
```

### 方法2：pdfminer（更完整）

```python
from pdfminer.high_level import extract_text
t = extract_text('suspect.pdf')
# 前200字符通常包含标题、arXiv ID、作者
print(t[:200])
```

### 方法3：Semantic Scholar API交叉验证

```python
import requests
# 从bib中拿到DOI后，查这个DOI对应的实际标题
r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
                 params={'fields': 'title'})
actual_title = r.json().get('title', '')
# 比较actual_title与bib中该条目的title是否一致
```

## arXiv ID下载的特殊问题

arXiv ID不是唯一的——同一arXiv号在不同论文目录下可能指向不同内容。这是因为arXiv ID在bib文件中被LLM错误赋值。**不能信任bib中的arXiv ID，必须用pdftotext提取PDF中的真实arXiv ID验证。**

## 快速判断PDF是否正确的规则

| 信号 | 含义 |
|:-----|:------|
| PDF中出现的arXiv ID与bib中一致 | 可能正确。但仍需验证arXiv ID本身是否正确指向了想要的论文 |
| PDF前100字包含论文主题词（iris/eye/pupil/kappa/VOR/BPPV等） | 很可能正确 |
| PDF前100字是纯数学/纯代数/纯图论 | 很可能错误（除非该论文确实引用数学方法论文） |
| PDF大小 < 1KB | 空文件，下载失败 |
| PDF提取文本出现大量乱码+表格错乱 | 扫描版PDF，NotebookLM上传可能导致提取伪影 |

## HTML伪PDF陷阱（2026-05-27 修复）

**场景**：OA URL实质上返回HTML页面（NEJM DOI → Elsevier重定向页），但旧版 `download_paper_sync()` 仅检查HTTP 200 → 保存HTML文件 → 后续步骤视作PDF使用。

**修复**：2026-05-27 在 `download_paper_sync()` 中加入三重验证：
1. Content-Type预检：`text/html` 直接拒绝（除非URL包含"pdf"）
2. `%PDF-` 头部 + `%%EOF` 尾部 + ≥1000B 检查
3. 失败后自动降级到 curl_cffi / 直连 requests 重试

**验证方法**：
```bash
# 快速判断文件是否为真PDF
head -c 5 suspect.pdf
# 应当输出 "%PDF-"
# 如果输出 "<!DOC" 或任意纯文本，则是HTML伪PDF

file suspect.pdf
# 应当输出 "PDF document"
# 如果输出 "HTML document" 则为伪PDF
```
