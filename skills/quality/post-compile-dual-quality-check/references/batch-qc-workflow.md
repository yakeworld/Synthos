# Batch QC Workflow — 批量双质检工作流

> 实战于 2026-05-27 Synthos 论文库 42 篇双质检 + 参考PDF整理。处理 42 篇论文的核心教训。

## 执行优先级

1. **缺报告论文优先** — 扫描所有目录，找缺少 `quality-report.md` 的论文（通常 2-5 篇）
2. **异常报告修复** — 检查已有报告是否全零分（Layer B API 解析错误导致，见 SKILL.md 陷阱节）
3. **批量 Layer A** — 剩余论文仅验证现有报告分数是否仍合理，不重复评审
4. **NotebookLM Layer B** — 仅对缺报告/异常论文上传并做 Gemini 评审

## 参考PDF内容验证

🟠 **致命发现（2026-05-27）：多个论文的 pdfs/ 目录中文件名与内容不符**

| 文件名 | 所在论文 | 实际内容 |
|:-------|:---------|:---------|
| chaudhary2019opensource.pdf | iris-3d-anatomical-opt | Dedekind 半环域（抽象代数） |
| perry2020keypoints.pdf | iris-3d-anatomical-opt | 流行病建模 |
| chaudhary2019.pdf | iris-yolo | 图论 Erdos-Posa 性质 |
| chen2023.pdf | iris-yolo | 表情估计 |
| sapkota2026.pdf | iris-yolo | 编码理论 |

**根因**：LLM 下载参考PDF时 arXiv ID 或 DOI 写错，下载了错误论文但保留了正确文件名。常规文件系统检查（文件存在）无法发现此问题。

**检测流程**：
```bash
# 对每个参考PDF，提取真实标题
pdftotext pdfs/xxx.pdf - | head -5

# 对比 references.bib 中的 title 字段
grep -A 10 '{bibkey}' references.bib | grep title
```

**修复**：从 bib 提取正确 DOI/arXiv → 重新下载 → 覆盖错误文件。

## notebooklm-sources.json 结构

每篇论文在双质检完成后应有此文件：

```json
{
  "paper": "paper-name",
  "notebook_id": "ec5c4b1f",
  "bib_entry_count": 48,
  "existing_pdfs": 5,
  "bibkeys_expected": ["ref1", "ref2", ...],
  "refs-md": [
    {"bibkey": "ref1", "size_kb": 1024.5}
  ]
}
```

## 全量扫描脚本（Python）

当需要批量扫描 40+ 论文时，用 Python 避免 shell 背景进程问题：

```python
# 关键：使用 subprocess 而非 shell 循环
# 避免：bash 背景进程的终端组设置失败
# 避免：Argument list too long（大 MD 内容）
import subprocess, tempfile

# 失败模式1：shell背景进程
subprocess.run(["notebooklm", "source", "add", content, "--type", "text"],
               capture_output=True, text=True, timeout=120)

# 失败模式2：大内容作为命令行参数（>2MB触发OSError）
# 修复：写临时文件，传路径
with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
    f.write(md_content)
    tmp_path = f.name
subprocess.run(["notebooklm", "source", "add", tmp_path, "--type", "text",
                "--title", bibkey], capture_output=True, timeout=120)
os.unlink(tmp_path)
```

## 质量矩阵汇总

双质检完成后，产出全景评分矩阵：

| 等级 | 数量 | 论文 |
|:-----|:----:|:-----|
| T1 (≥0.85) | N | ... |
| T2 (≥0.80) | N | ... |
| T3 (≥0.75) | N | ... |
| <T3 | N | ... |
