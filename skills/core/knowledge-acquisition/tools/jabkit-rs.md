---
name: tool-jabkit-rs
category: tool
description: jabkit-rs 检索工具精确契约 — CLI 参数、输出格式、错误码、降级路由
version: 1.0.0
---

# jabkit-rs — 检索工具契约

> **工程层**：本文档只定义工具调用的事实契约（CLI 参数、输出、错误行为）。
> 何时用、为何用、降级决策逻辑见上层 `SKILL.md`（哲学层）。

## 工具身份

| 项 | 值 |
|----|-----|
| 二进制 | `~/.local/bin/jabkit-rs`（Rust 编译版） |
| 来源 | yakeworld/jabref fork 编译版（S2 已修复） |
| 已弃用 | `jabkit`（Java wrapper）— 执行即挂起，2026-08-14 实测 261s 无结果 |
| 实测基准 | 25s 内产出 BibTeX（2026-08 实测） |

## CLI 契约

```bash
jabkit-rs fetch --provider=<源> --query="<关键词>" --porcelain
```

| 参数 | 必填 | 说明 |
|------|:----:|------|
| `--provider` | ✅ | 检索源（见下表） |
| `--query` | ✅ | 检索关键词 |
| `--porcelain` | 可选 | 稳定输出模式，行为同旧版 |

## Provider 表（26 源中的常用 5 源）

| 源 | 领域 | 说明 | 凭据 |
|----|------|------|------|
| `Crossref` | 全学科 | 最快，无 key | 无 |
| `Medline`/`PubMed` | 生物医学 | 需 NCBI key | NCBI API key |
| `SemanticScholar` | 全学科 | ✅ 已修复（本地 recompiled 版带 x-api-key） | 内置 key |
| `arXiv` | 预印本 | 最新研究 | 无 |
| `OpenAlex` | 全学科 | 100 req/s | 无 |

## 输出契约

- 标准输出：**BibTeX** 条目流
- 无匹配：空输出 + 非零退出码
- 多源合并：逐源调用后合并 BibTeX

## 错误处理

| 症状 | 判定 | 处置 |
|------|------|------|
| 打印 "Java 25 is available…" 后无输出 | 误用 Java `jabkit` | 改用 `jabkit-rs` |
| 请求挂起 > 60s | 源不可达/挂死 | Ctrl-C 后切换 provider 重试 |
| `--porcelain` 输出异常 | 版本行为差异 | 以实测为准，更新本文档 |

## Medline 特殊流程（需要 PMID）

```bash
# DOI → PMID（NCBI esearch），再经 Medline provider 检索
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<DOI>[doi]&retmode=json"
```

## 版本纪律

- 工具变更（参数/输出/弃用）以**实测**为准，改动后立即更新本文档
- 弃用即弃用：`jabkit`（Java）挂起无输出，只用 `jabkit-rs`（Rust 编译版）
