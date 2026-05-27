---
name: paper-reference-pipeline
description: "论文参考文献全流程管线：NotebookLM筛选→bib生成→本地增强(SS元数据)→PDF获取(3级竞速)→Markdown转换→回传NotebookLM。含D8≥30参考文献标准与自动修复。"
version: 1.1.0
tags: [references, bibtex, pdf, notebooklm, pipeline, d8, quality-check]
---

# 论文参考文献全流程管线

## 核心理念

1. **NotebookLM优先筛选** — 利用Gemini语义理解筛选相关文献
2. **本地增强优化** — Semantic Scholar补元数据（摘要/arXiv/OA链接）
3. **PDF全文获取** — 3级竞速引擎（Sci-Hub → LibGen → MedData）
4. **Markdown转换** — 用MarkItDown转为可读文本（实验性，表格/公式保真度有限）
5. **回传NotebookLM** — 更新项目文献源

## 管线流程

```
NotebookLM筛选/SS搜索 → 生成BibTeX → 本地增强(SS元数据)
  → PDF全文获取(3级竞速+MedData) → Markdown转换 → 回传NotebookLM
```

## 快速命令

```bash
# 工作目录
cd /media/yakeworld/sda2/Synthos/tools/paper-manager

# 1. 搜索生成bib
python3 main.py search "BPPV otoconia" --limit 20 --no-download --output /tmp/refs

# 2. 增强元数据（快，～1s/条）
MEDDATA_USERNAME="wzsrmyy" MEDDATA_PASSWORD="xxx" \
  python3 main.py enhance /tmp/refs/references.bib -o /tmp/enhanced --no-download

# 3. 下载PDF（慢，15-60s/条，涉及3级竞速）
MEDDATA_USERNAME="wzsrmyy" MEDDATA_PASSWORD="xxx" \
  python3 main.py enhance /tmp/refs/references.bib -o /tmp/enhanced --limit 10

# 4. 上传到NotebookLM
for f in /tmp/enhanced/pdfs/*.pdf; do
  notebooklm source add "$f" --title "ref-$(basename $f .pdf)" -n <project_id> --type file
done
```

## 凭据管理（禁止硬编码）

所有API密钥和密码通过环境变量传入，`.env.template` 中有模板：

```
SEMANTIC_SCHOLAR_API_KEY  — SS搜索（无key有rate limit 1req/s）
MEDDATA_USERNAME          — 医数据平台账号
MEDDATA_PASSWORD          — 医数据平台密码
MEDDATA_TOKEN             — 直接token（替代账号密码）
```

`.env` 已加入 `.gitignore`，永不提交GitHub。

## D8 参考文献标准（≥30篇）

高质量论文判定依据：参考文献≥30篇 + Gemini 7维评分。

**自动修复流程**（`tools/paper-manager/auto_fix_d8.py`）：

1. 对每篇参考文献不足的论文，提取主题词
2. Semantic Scholar API搜索相关论文（需 API key，否则429限流）
3. 过滤已有DOI，添加新DOI到.bib
4. 通过竞速引擎下载PDF
5. 上传到NotebookLM

```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
SEMANTIC_SCHOLAR_API_KEY="x" MEDDATA_USERNAME="x" MEDDATA_PASSWORD="x" \
  python3 auto_fix_d8.py
```

**陷阱**：
- SS搜索无API key很快被429限流，脚本需带key运行
- 自动搜索结果多为零散期刊论文，PDF下载成功率约5-20%
- 下载失败不影响.bib文件更新（DOI已加，PDF后续可补）

## 双质量检查（D1-D7 Gemini + D8参考文献）

检查脚本：`outputs/papers/batch_qc_rerun.py`

运行方式：
```bash
cd /media/yakeworld/sda2/Synthos/outputs/papers && python3 batch_qc_rerun.py
```

输出：
- 每篇论文：`{dir}/qc-layer-b.md` （D1-D7评分）
- 参考文献：`{dir}/qc-d8-refs.md` （D8评分）
- 综合日志：`batch-qc-phase2-log.md`

**Tier判定**（D1-D7和D8平均分）：
| Tier | 要求 | 含义 |
|------|------|------|
| T1 | ≥0.85 | 投稿级（Nature/CNS/PAMI） |
| T2 | ≥0.80 | 会议级（CBM/IEEE Access） |
| T3 | ≥0.75 | 标准级 |
| FAIL | <0.75 | 需修改 |

## NotebookLM 源管理

### 命名规则
- 论文PDF：`{论文目录名}-v{版本号}` （如 `pd-dysphagia-2026-v1`）
- 参考文献：`ref-{DOI转文件名}` （如 `ref-10-1056_NEJMcp1309481`）
- **禁止使用 `paper.pdf`**（历史遗留，导致42份重复上传）

### 清理重复
`tools/paper-manager/clean_dupes.py` — 按标题匹配删除同名重复源。

```bash
python3 clean_dupes.py  # 扫描所有项目，删除同名重复
```

**注意**：`notebooklm source clean` 只清理异常/阻塞源，不查标题重复。需用 `delete-by-title` 或 `delete {source_id}` 逐条删除。

### 旧版本清理
检查 `{name}-v1`、`{name}-v2` 多版本，保留最新删除旧版。

## 脚本路径

| 脚本 | 路径 | 用途 |
|------|------|------|
| auto_fix_d8.py | tools/paper-manager/ | D8自动补参考文献 |
| clean_dupes.py | tools/paper-manager/ | NotebookLM重复源清理 |
| batch_qc_rerun.py | outputs/papers/ | 双质量检查全流程 |
| batch_refresh.sh | tools/paper-manager/ | 批量参考PDF下载+上传 |
| clean_and_bib.py | outputs/papers/ | 单项目参考文献→BibTeX |

## 已知问题

1. **MarkItDown学术PDF转换质量差** — 表格变形、公式丢失。Markdown仅作辅助参考，不可替代PDF。
2. **MedData token过期** — 用账号密码模式（`MEDDATA_USERNAME+MEDDATA_PASSWORD`）自动刷新。
3. **NotebookLM `delete-by-title` 可能不生效** — 退回用`delete {source_id}`逐条删。
4. **arXiv PDF直接URL** — `arxiv.org/pdf/XXXX.XXXXX` 返回HTML，必须加 `.pdf` 后缀才有真正的PDF。
