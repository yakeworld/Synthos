# 参考文献补充工作流

> 当 NotebookLM 项目 source <10 篇时，用于定向补充关键参考文献。

## 项目现状（2026-05-27）

| 项目ID | 项目名 | 当前source | 关联论文 | 优先级 |
|:-------|:-------|:----------|:---------|:-------|
| 95509a49 | BPPV三维仿真研究 | 5 PDFs | bppv-minimal-stimulus, bppv-otoconia-simulation, bppv-pd-clinical-review | P0 |
| b6698e12 | 3D眼球模型扭转追踪 | 9篇 | iris-yolo | P1 |
| 468528f8 | CutEye | 1篇 | cuteye-model | P2 |

### 检索方法（避坑版）

### 推荐：paper-manager search（已修复）

> 2026-05-27 修复了 `src/` 结构下的相对导入错误，搜索功能现在可用。

```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager

# 只搜索，不下载（推荐 — 避免被Sci-Hub探测卡住）
python3 main.py search "BPPV canalith repositioning" --limit 5 --no-download

# 搜索+下载（可能慢，8-12s/DOI）
python3 main.py search "BPPV canalith repositioning" --limit 3
```

**注意**：
- 搜索+BibTeX导出：~3秒 ✅
- 下载个别DOI（`download_one.py`）：可用 ✅
- 批量下载所有DOI（`batch_ref_download.py`）：**不推荐** — 付费期刊DOI成功率趋近0

### 不要做的事
- 不要试图批量下载 .bib 文件中的所有 DOI — 付费期刊DOI，成功率趋近0，每条等待180s超时
- 不要用 `batch_ref_download.py` 批量下载 — 同上

### 推荐：arXiv 直搜

```bash
# BPPV 相关
curl -s "https://export.arxiv.org/api/query?search_query=all:BPPV+AND+all:diagnosis&max_results=5&sortBy=relevance" \
  | python3 -c "
import sys, re
text = sys.stdin.read()
entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
for e in entries:
    title = re.search(r'<title>(.*?)</title>', e)
    link = re.search(r'<id>(.*?)</id>', e)
    pdf = re.search(r'<link.*?href=\"(.*?pdf)\".*?title=\"pdf\"', e)
    if title: print(f'TITLE: {title.group(1).strip()}')
    if pdf: print(f'PDF: {pdf.group(1)}')
    print()
"
```

### 推荐：Semantic Scholar 搜DOI+下载

```bash
# 搜索
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=BPPV+canalith+repositioning&limit=5&fields=title,paperId,externalIds,openAccessPdf" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('data', []):
    title = p.get('title', 'N/A')
    paperId = p.get('paperId', 'N/A')
    oa = p.get('openAccessPdf', {})
    if oa and oa.get('url'):
        print(f'{title}')
        print(f'  PDF: {oa[\"url\"]}')
    else:
        print(f'{title} (no OA)')
    print(f'  S2 ID: {paperId}')
    print()
"
```

### 上传到 NotebookLM

```bash
notebooklm source add /path/to/paper.pdf --title "ref-短描述" -n <project_id>
```

## 每条论文的关键引用方向

### BPPV (95509a49)
- BPPV 流行病学与诊断标准
- 后管/水平管复位疗效RCT
- 耳石动力学仿真
- 三维眼动追踪与BPPV
- 前庭康复

### 3D眼球 (b6698e12)
- 3D眼球解剖模型/有限元
- 扭转追踪方法
- 虹膜纹理匹配
- 眼肌力学

### CutEye (468528f8)
- 眨眼检测/眼睑运动
- 视频眼震图
- 计算机视觉眼动分析
- 便携式眼动仪
