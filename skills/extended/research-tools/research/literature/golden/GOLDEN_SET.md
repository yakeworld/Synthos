# GOLDEN_SET.md — literature (research-tools)

> 对应原则：P0 证据可溯性（凡数必源）、P1 原子可复现性、凡下必验魔数为准
> golden_set_origin: self_defined
> 单一真理来源：检索/下载/验证三位一体管道的金标准

## 设计依据

本技能为文献检索统一入口（search 检索 + download 下载 + diagnose 诊断）。金标准自设，
设计目标验证：**多源聚合检索返回元数据齐备的候选 records；管线落盘 PDF 每篇过 `%PDF-` 魔数 + pdfinfo 标题验证；diagnose 输出三阶段结构化 JSON；已失效源（S2 废弃字段、PubScholar 关闭）正确降级**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 检索 | jabkit-rs fetch（26 源统一入口） | BibTeX 元数据齐备 |
| 下载 | bban.top CDN 直连 + `%PDF-` 魔数 | 排除串流/伪件 |
| 诊断 | `literature diagnose` 三阶段 | 7 源检索 + DOI 解析 + 12 通道下载测试 |
| 降级/错误 | 2 case | S2 废弃字段 400；PubScholar API 关闭静默空列表 |

## 测试用例表 (cases/)

| case | 类型 | 输入摘要 | 期望结论 |
|------|------|----------|----------|
| case_001 | 正常 | `jabkit-rs fetch --provider=Crossref --query="pupil light reflex ODE" --porcelain` | ~2s 返回 BibTeX 条目，title/authors/DOI/year 齐备 |
| case_002 | 正常(管线) | `python3 literature.py pipeline "iris recognition" --sources crossref pubmed --output-dir ./pdfs` | ./pdfs/ 落盘 12 篇 PDF，每篇 `%PDF-` 魔数 + pdfinfo 标题验证通过 |
| case_003 | 错误路径 | S2 请求仍带 `pdfUrls`/`urls` 字段；PubScholar API 已关闭 | S2 返回 400（Unrecognized or unsupported fields）→ fields 剔除后重试；PubScholar 静默返回空列表，降级其余 4 源 |

## 通过标准

- **检索**：候选 records 的 title/authors/DOI/year 齐备；Crossref 请求不带 `mail` 参数，`order` 为 `desc`/`asc`。
- **下载**：每篇落盘 PDF 以 `%PDF-` 开头（魔数验证），且 pdfinfo 标题与元数据一致（排除串流/伪件）。
- **S2 合规**：fields 不含 `pdfUrls`/`urls`（否则 API 返回 400）；单 key `SEMANTIC_SCHOLAR_API_KEY`。
- **源降级**：PubScholar 无凭证时静默返回空列表，不抛异常；管线继续用其余 4 源（S2/PubMed/CrossRef/arXiv）。
- **诊断**：`literature diagnose` 输出三阶段 JSON（7 源检索 + DOI 解析 + 12 通道下载测试）。

## pass_threshold: 0.80

3 个 case 权重加权分 ≥ 0.80 且全部 critical 检查通过。
critical 检查：case_002 的 PDF 魔数验证、case_003 的源降级不崩溃。

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-07-30 | 初始自设金标准，3 个 case（正常 2 + 错误 1） | Synthos Agent |
