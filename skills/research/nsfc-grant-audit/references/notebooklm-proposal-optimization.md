# NotebookLM Proposal Optimization Workflow

> Discovered: 2026-05-25 session — RFID hospital asset management proposal optimization
> Complements: notebooklm-review-workflow.md (which covers using NotebookLM as knowledge base)
> This covers: creating a dedicated notebook for a proposal and optimizing it via research + expert review

## Overview

Unlike `notebooklm-review-workflow.md` (which assumes an existing knowledge-base notebook is the review target), this workflow creates a **new notebook specifically for the proposal** and uses NotebookLM's full pipeline (research + Gemini Q&A + content generation) to improve it.

## Workflow

### Phase 1: Setup

```bash
# 1. Create a dedicated notebook for this proposal
notebooklm create "项目名称_优化"    # descriptive title
notebooklm use <new_id>

# 2. Upload the proposal text
# Preferred: Python client add_text (most reliable)
# Fallback: note create (indexed but may take time for Gemini to see it)
# Last resort: source add via CLI (may fail with RPC error)

# Convert .doc → .txt first
libreoffice --headless --convert-to txt:Text proposal.doc
# Upload via note create (fallback when source add fails)
NOTE_CONTENT=$(cat proposal.txt)
notebooklm note create "$NOTE_CONTENT" --title "申报书原文"
```

**Key decision**: Use note create when `source add` fails with RPC errors. Notes ARE indexed by Gemini for Q&A, though they don't appear in the source panel in the web UI.

### Phase 2: Literature Augmentation

```bash
# Launch parallel deep research queries (each covers one dimension)
notebooklm source add-research "query 1 - core technology" --mode deep --no-wait
notebooklm source add-research "query 2 - application cases" --mode deep --no-wait  
notebooklm source add-research "query 3 - Chinese/mandarin specific" --mode deep --no-wait

# Wait for completion (may timeout - import may still succeed partially)
notebooklm research wait --import-all
# Retry if needed:
notebooklm research status    # check if still running
notebooklm research wait --import-all   # retry
```

**Research topic strategy**: Launch 3-4 parallel queries covering:
1. Core technology (e.g., "UHF RFID hospital asset management")
2. Application cases (e.g., "RTLS healthcare asset tracking implementation")
3. Chinese-language specific (e.g., "公立医院 资产管理 RFID 业财融合")
4. Supplementary domain (e.g., "IoMT security healthcare IoT")

### Phase 3: Expert Review via Gemini Role-Play

```bash
# Step 1: Comprehensive review - set Gemini as expert reviewer
notebooklm ask "你是[评审专家角色]。请仔细阅读笔记本中上传的申报书，从以下维度给出评审意见：
1. P0致命问题
2. P1重要问题  
3. 参考文献建议
4. 数据指标修正
5. 结构优化
6. 匿名校验
..."

# Step 2: Targeted follow-ups (one dimension at a time)
notebooklm ask "请直接给出[具体维度]的优化文本，不要分析过程：1. 补充8条参考文献 2. 修正后的指标表 3. 标题修改建议"
```

**Effective role prompts** (tested):
- "你是有10年经验的省级科技项目评审专家"
- "你是一位AI增强型课题评审专家"
- "请用盲审专家视角"

### Phase 4: Compile Optimized Version

Synthesize the Gemini feedback with your own analysis:

1. **P0 fixes** (must fix): Citation gap, data contradictions, anonymous violations, title misalignment
2. **P1 fixes** (important): Technical depth, security design, methodology detail
3. **P2 fixes** (suggested): Buzzword removal, diagram description, structure optimization

Format the output as a complete optimized proposal document.

### Phase 5: Verification

```bash
# Upload optimized version back to the same notebook
notebooklm note create "$OPTIMIZED_CONTENT" --title "申报书_优化版"

# Final verification
notebooklm ask "请对比原文和优化版，检查：1.是否所有P0问题已修复 2.新增引用是否合理 3.指标是否一致 4.语言风格是否保持统一"
```

## Known Limitations

| Issue | Workaround |
|:------|:-----------|
| **Gemini may not immediately index notes** | Wait 30-60s after note create, or add a short delay before asking |
| **add-research may timeout on import** | Sources may still be partially imported despite timeout; check with `source list` |
| **Gemini fact-confabulation** | Gemini may invent specific paper details (volumes, page numbers). Verify all references on PubMed/Semantic Scholar before final submission |
| **Proposal too long for single ask** | Split into sections: background, technology, targets, budget |
