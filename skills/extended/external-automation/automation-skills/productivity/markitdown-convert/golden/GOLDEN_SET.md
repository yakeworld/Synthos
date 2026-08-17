---
name: markitdown-convert
description: markitdown-convert 金测集 — PDF/Office→Markdown 转换的可执行测试
---

# 金测集: markitdown-convert

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (MARK-001~007) + IO_CONTRACT。
> 核心能力：用微软 MarkItDown（`uvx markitdown`）将 PDF/DOCX/PPTX/Excel 转为 Markdown；
> PDF→MD 是论文管线下载后的**强制步骤**，失败时回退 `pdftotext`，再失败写占位而非静默跳过。
> IO_CONTRACT: input `file_path: str` → output `md_path: str`（含 status/回退标记）。
> 每个 case 验证命令选择、回退策略与错误处理（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：单文件学术 PDF→Markdown | `uvx markitdown input.pdf > pdfs_md/input.md`（MARK-002）；输出 >50 chars 且保留章节标题/公式；依赖以 `[pdf]` extra 安装（MARK-006） |
| case_002 | 正常：批量转换含缓存跳过与回退 | 已有 `.md` 且 >100 chars 的文件跳过（缓存）；markitdown 失败自动回退 `pdftotext` 并标记 `⚠️`（MARK-002） |
| case_003 | 错误路径：无文本层/损坏 PDF | markitdown 与 pdftotext 均返回 0 字符 → 写入 `[PDF无法提取文本]` 占位而非静默跳过（MARK-003）；建议 arXiv/PMC 替代版、手动摘要或 marker-pdf OCR（MARK-007） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 命令必须为 `uvx markitdown <pdf> > <md>` 形式；输出文件存在、>50 chars、非空；不得在未装 `[pdf]` extra 时执行（否则 `MissingDependencyException`，MARK-006）
- case_002: 缓存文件（已存在且 >100 chars）不得重复转换；markitdown 失败的文件必须走 `pdftotext` 回退且标记 `⚠️`；回退后仍 <100 chars 才允许写占位
- case_003: 双路径均 0 字符时必须写占位文件 `[PDF无法提取文本 — 需手动补摘要或走OCR]`，禁止静默跳过；错误报告须含上下文（哪个文件、两条命令的输出字符数）与恢复建议（≥2 条：替代版本/手动摘要/OCR）
- 所有 case: 批量场景须排除引用/模板类 PDF（`*reference*`/`*template*`/`*graphical*`/作者年格式），主论文未转错目标（MARK-004）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 命令 / 结果结构 / 回退与占位结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 命令按 SKILL.md 精确结构匹配（`uvx markitdown <file> > <out>`），文件路径可不同
- 结果必须是 dict，键名稳定（`status`, `md_path`, `chars`, `fallback` 等）
- 错误路径必须同时含 `error` 上下文与 `recovery` 建议两个字段（异常约束）

## 关联

- SKILL.md Genes: MARK-001~007
- SKILL.md 验证清单: 6 项（依赖安装 / pdfs_md 对应 / 回退占位 / 引用过滤 / 损坏替代路径 / frontmatter）
- 相关技能: knowledge-acquisition（下载后触发本技能）, notebooklm-cli（MD 供 NotebookLM 索引）, knowledge-base-audit
