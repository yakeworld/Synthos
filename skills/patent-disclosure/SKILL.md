---
name: patent-disclosure
description: "中国专利挖掘发现与交底书生成全流程：扫描项目文档挖掘专利点、讨论融合、基于脱敏模版生成技术交底书、CNIPA查新、生成后自检含逻辑闭环与公式参数一致性 | Patent mining, prior-art search, and disclosure drafting for Chinese patents."
version: "1.8.5-synthos-2"
author: "handsomestWei (original) + Synthos absorbed v1.8.5"
synthos_absorption_source: "https://github.com/handsomestWei/patent-disclosure-skill"
synthos_absorption_date: "2026-05-21"
synthos_absorption_score: 4.6
synthos_absorption_license: "Apache-2.0"
tags: [patent, disclosure, cnipa, prior-art, chinese-patent, extended-skill]
---

# 专利挖掘发现与交底书生成

## 原理层·文言

> 技有所创，创有所保。专利者，创新之盾也。
> 挖掘在平时，发现于细微。不放过一个改进，不遗漏一个变体。
> 交底之书，以清为上。使同行可解，使审查可明。

##
> **Synthos 整合版本**：1.8.5-synthos-2

---

## 原理层 · 文言

### 专利本源论

专利之授，以三性为纲。一曰**新颖**：凡在先技术中未见其方者，谓之新。二曰**创造**：本领域之常人不思易得，谓之创。三曰**实用**：可施于产业，生其实效，谓之用。三性既立，专利乃可成焉。

### 交底书体要

交底书之作，贵在尽述三事：所解技术问题为何、技术方案如何构成、有益效果如何显现。三者贯通，如鼎之三足，缺一不可。背景宜溯源而指其弊，方案宜分模块而陈其理，效果宜引参数而证其实。文辞须令代理者一览而通，不劳创造之思。

### 查新原道

查新之道，先官后民。以**国知局公布公告**为根本，Google 学术与 Patents 为补充。凡检索所得 `abstract`，必消化其意而后重述，不得臆造，不得大段袭抄。每引一文，必附可访之链，且验其可达。

### 迭代变通

交底之成，非一蹴可几。每轮修正，必标新时。旧稿不覆，新篇另出。两稿并存，以资对照。修正有二：一曰**合并**，补新材料、扩其章节；二曰**纠正**，改其谬误、正其观点。皆须留修订记录于案，以便追溯。

### 脱敏守正

凡涉业务之私、分类之名、数值之实、品牌之号，当抽象为通用语、化名代其实、约数为范围、削名为「某系统」。令方案可公之于世，无害于密。

---

## 方法层 · 白话

### 总纲

本技能覆盖 **专利点挖掘 → 查新与差异化 → 交底书生成 → 自检完善 → 迭代修正** 全流程。

流程分为 **主流程（8步）** 与 **迭代模式（2种）**：

| 阶段 | 步骤 | 用途 |
|:----:|:-----|:-----|
| **主流程** | Step 1 | `intake.md` — 边界与输入确认 |
| | Step 2 | `project_scan.md` — 项目文档扫描 |
| | Step 3–4 | `patent_points_analyzer.md` — 候选专利点挖掘与融合选定 |
| | Step 5 | `prior_art_search.md` — CNIPA联网查新 |
| | Step 6 | `disclosure_preview.md` — 全文前摘要预览 |
| | Step 7 | `disclosure_builder.md` + `template_reference.md` — 交底书生成 |
| | Step 8 | `disclosure_self_check.md` — 内部自检 |
| **迭代** | 补充扩展 | `merger.md` — 增量合并 |
| | 纠错修正 | `correction_handler.md` — 对话纠正 |

### 触发条件

以下任一情况启用：
- 用户明确提及：专利挖掘、专利点、技术交底书、交底书、专利交底书、查新、现有技术对比等
- 斜杠指令：`/patent-disclosure`
- **迭代模式**：用户意图明显是在已有交底书或上一轮输出上继续工作

### 核心约束

1. **查新优先 CNIPA**：优先使用 `tools/cnipa_epub_search.py`（中国专利公布公告），失败降级 WebSearch
2. **Office 必转**：`.docx` / `.pptx` 必须先经 `tools/docx_to_md.py` / `tools/pptx_to_md.py` 转换为 Markdown 再扫描，不得跳过
3. **交底书规范**：
   - 正文不得含自检清单
   - 系统框图与流程图用 mermaid（`tools/mermaid_render.py` 渲染为 PNG）
   - "abstract" 必用：CNIPA 检索结果中 abstract 字段须消化后重写，不得编造
   - 每引一文须附可验 URL
4. **交付命名**：`{案件名}_{YYYYMMDDHHmmss}.md` + 同名 `.docx`，不覆盖旧稿
5. **迭代必留记录**：每次合并/纠正后须追加 `交底书修订对话记录.md`

### 工具安装

```bash
pip install -r tools/requirements.txt           # docx & pptx 转换
pip install -r tools/requirements-cnipa.txt     # CNIPA 查新
python -m playwright install chromium           # CNIPA WAF 绕过
npm install -g @mermaid-js/mermaid-cli          # mermaid 渲染
```

---

## 命令层 · English

### Directory Structure

| Path | Description |
|------|-------------|
| `SKILL.md` | This file — trigger conditions, step index, principles |
| `prompts/` | Step-by-step instruction templates (11 files) |
| `tools/` | Python extension scripts (CNIPA search, mermaid render, docx/pptx conversion) |
| `docs/` | Original repo documentation |
| `examples/` | Fictional case materials |

### Key Command Patterns

**Office conversion:**
```bash
python3 tools/docx_to_md.py -i "<input.docx>" -o "<output.md>"
python3 tools/pptx_to_md.py -i "<input.pptx>" -o "<output.md>"
```

**CNIPA prior-art search (one term per call):**
```bash
python3 tools/cnipa_epub_search.py <search_term_1>
python3 tools/cnipa_epub_search.py <search_term_2>
```

**Disclosure rendering + Word output:**
```bash
python3 tools/mermaid_render.py -i "<draft.md>" -o "<CaseName_YYYYMMDDHHmmss.md>"
```

**Iteration log:**
```bash
python3 tools/iteration_dialog_log.py --case-dir "{case_dir}" --kind merge --user "{summary}" --summary "{abstract}" --artifacts "{file.md},{file.docx}"
```

### Step Execution Order

1. Read `prompts/intake.md` → confirm boundary with user
2. Read `prompts/project_scan.md` → scan project docs (convert Office first)
3. Read `prompts/patent_points_analyzer.md` → list 3–5 candidate points, fuse
4. Read `prompts/prior_art_search.md` → CNIPA search (split terms, one call per term)
5. Read `prompts/disclosure_preview.md` → show structured summary for user confirmation
6. Read `prompts/disclosure_builder.md` + `template_reference.md` → generate full disclosure
7. Read `prompts/disclosure_self_check.md` → run internal checks (never write to output)
8. **Iteration**: Read `prompts/iteration_context.md` → select `merger.md` or `correction_handler.md` → produce new timestamped file

### Alignment with Agent4S Framework

This skill is a verified **Agent4S L3 (Single-Process Intelligent Agent)** implementation:

| Agent4S L3 Component | Skill Implementation |
|:---------------------|:---------------------|
| **Reasoning** | LLM-driven multi-step analysis (patent mining → prior art → disclosure) |
| **Context Engineering** | `prompts/` step-by-step templates + `iteration_context.md` state tracking |
| **MCP** | `tools/` Python scripts as MCP-like tool endpoints; `skill_view` for tool discovery |
| **Self-Check** | `disclosure_self_check.md` — quality gate before delivery |

To upgrade to standard MCP: each `tools/*.py` script can be wrapped as an MCP server, enabling interoperability with any MCP-compatible AI system (Claude Code, Codex, etc.). See `docs/mcp-migration-guide.md` (planned).

---

## Synthos Absorption Record

| Field | Value |
|:------|:------|
| Source | `handsomestWei/patent-disclosure-skill` |
| Version | v1.8.5 → synthos-2 (principles restructured) |
| Absorbed | 2026-05-21 |
| License | Apache-2.0 |
