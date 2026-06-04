---
name: competition-submission
description: End-to-end preparation of AI/tech/innovation competition submissions. Extract requirements, map to scoring criteria, generate documents, produce submission checklist. Covers medical AI, tech innovation, academic conferences, Chinese government grants.
allowed-tools:
- terminal
- file
- web
- search
license: MIT
metadata:
  synthos:
    version: 2.0.0
    author: Synthos
    signature: 'competition_doc: str -> submission_package: dict'
---

# Competition Submission Pipeline

## 核心流程

```
输入(通知PDF/链接)
  ↓
Step 1: 需求提取 → 评分标准/格式要求/截止时间
Step 2: 能力映射 → 项目能力→评分标准矩阵
Step 3: 文档生成 → 技术规格/路线图/视频脚本/申报表
Step 4: 材料整合 → 提交包(zip/PDF)
Step 5: 质量审核 → 完整性/一致性检查
```

## Step 1: 需求提取

从PDF或网页提取竞赛要求：

```bash
# PDF提取
curl -sL "https://..." | python3 -c "
import sys, pdfplumber
with pdfplumber.open(sys.stdin.buffer) as pdf:
    for page in pdf.pages: print(page.extract_text())
"

# 网页提取
curl -sL "https://..." | python3 -c "
import sys, re
html = sys.stdin.read()
# 提取表格/列表等结构化评分标准
"
```

输出结构化清单：`requirements/competition-reqs.json`

## Step 2: 能力映射

| 评分维度 | 权重 | 项目匹配能力 | 证据材料 |
|:---------|:----:|:------------|:---------|
| 创新性 | 30% | Synthos声明式架构 | 论文/架构图 |
| 技术深度 | 25% | 自进化引擎 | evolution日志 |
| 社会价值 | 20% | 医学AI应用 | 论文产出清单 |
| 可行性 | 15% | 已有完整管线 | paper-pipeline |
| 团队实力 | 10% | 论文+专利产出 | CV/成果列表 |

## Step 3: 文档生成

| 文档类型 | 模板 | 工具 |
|:---------|:-----|:-----|
| 技术规格书 | `references/tech-spec-template.md` | Markdown |
| 路线图 | `references/roadmap-template.md` | Mermaid timeline |
| 视频脚本 | `references/video-script-template.md` | 分镜脚本格式 |
| 申报表 | `references/form-filling-guide.md` | python-docx/pdf |
| PPT | `references/presentation-template.md` | python-pptx |

详见各模板文件。

## Step 4-5: 整合与审核

```bash
# 打包
zip -r submission.zip submission/ -x "*/.*"

# 完整性检查
# 检查是否涵盖所有评分维度/格式要求/截止时间
```

## 参考文件

- `references/tech-spec-template.md` — 技术规格书模板
- `references/roadmap-template.md` — 路线图模板
- `references/video-script-template.md` — 视频脚本模板
- `references/form-filling-guide.md` — 中国申报表填写指南
- `references/presentation-template.md` — 答辩PPT模板
