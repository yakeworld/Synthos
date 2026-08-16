---
name: knowledge-acquisition
description: knowledge-acquisition 金测集 — 检索与下载的可执行测试
---

# 金测集: knowledge-acquisition

> 来源: SKILL.md Golden 集合（L138-142）。验证检索→下载两步闭环（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | jabkit-rs 检索 | 25s 内产出 BibTeX，不用弃用 Java jabkit |
| case_002 | doi-fetch 下载验证 | PDF 通过 head -c 5 = %PDF-（5 字节）+ pdfinfo 标题核对 |
| case_003 | 错误路径 | 误用 Java jabkit 挂起 / 魔数校验 4 字节失败 → 标下载失败不入库 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 25s 内产出 BibTeX 条目
- case_002: 魔数 5 字节 + 标题一致
- case_003: 失败路径正确标记，不伪造成功

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命（case_003） |

## 关联

- SKILL.md Genes: KA-001~006
- 工具契约: tools/jabkit-rs.md, tools/doi-fetch.md
