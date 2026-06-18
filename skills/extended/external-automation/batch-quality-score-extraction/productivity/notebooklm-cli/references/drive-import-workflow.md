# Google Drive → NotebookLM 批量导入实战

> 2026-06-01 验证：SCC 34/34 PDF via Drive ✅，Pima 35/40 ✅

## 核心流程

```bash
# 1. 上传 PDF 到 Drive（保持目录整洁）
rclone copy /path/to/pdfs/*.pdf googledrive:paper-refs/

# 2. 获取文件 ID 列表
rclone lsjson googledrive:paper-refs/ | python3 -c "
import json, sys
for item in json.load(sys.stdin):
    print(f\"{item['ID']}|{item['Name']}\")
" > /tmp/drive_files.txt

# 3. 批量导入（逐个，间隔0.5s）
while IFS='|' read -r fid name; do
  title="${name%.pdf}"
  notebooklm source add-drive "$fid" "$title" --mime-type pdf -n <notebook_id>
  sleep 0.5
done < /tmp/drive_files.txt

# 4. 清理 error/duplicate
notebooklm source clean -n <notebook_id> -y
```

## 限制

| 文件类型 | Drive 导入 | 直传 |
|:---------|:-----------|:-----|
| PDF | ✅ `add-drive --mime-type pdf` 即时 ready | ✅ `source add file.pdf` |
| Markdown (.md) | ❌ "API returned no data" | ✅ `source add file.md` |
| 图片型/扫描 PDF | ❌ Drive 不索引 | ⚠️ 需 OCR 转 MD |

## 顽固文件清单（持续失败的 5 篇）

Pima 论文内 5 篇 PDF 无论 Drive 还是直传均无法处理：

| 文件 | 大小 | Drive | MD 直传 | 建议 |
|:-----|:----:|:-----:|:-------:|:-----|
| Chawla2002.pdf | 2.8MB | ❌ API no data | ❌ 超时 120s | 网页端手动上传 |
| Liao2023.pdf | 1.4MB | ❌ API no data | ❌ 超时 120s | 网页端手动上传 |
| Pranto2020.pdf | 205KB | ❌ API no data | ❌ 超时 120s | 网页端手动上传 |
| Ribeiro2016.pdf | 277KB | ❌ API no data | ❌ 超时 120s | 网页端手动上传 |
| Wirth2000.pdf | 353KB | ❌ API no data | ❌ 超时 120s | 网页端手动上传 |

所有文件均验证为有效 PDF（`%PDF-` 头，有效 md5）。失败原因为 NotebookLM 服务器处理逻辑限制。

## 性能对比

| 指标 | Drive 导入 (34篇 SCC) | MD 直传 (40篇 Pima) |
|:-----|:--------------------:|:------------------:|
| 成功率 | 34/34 = **100%** | 35/40 = 87.5% |
| 处理速度 | **即时 ready** | 120s+ 每篇 |
| 总耗时 | ~17s (34×0.5s间隔) | ~5min + 超时重试 |
