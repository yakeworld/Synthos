# NotebookLM-Integrated Grant Review Workflow

This reference captures the pattern of using NotebookLM as the knowledge base during a grant review and reconstruction session. The workflow leverages NotebookLM's indexed sources and AI summarization as the primary analysis engine.

## Session Pattern (Discovered in Practice)

### Step 1: Select the Notebook
```bash
notebooklm use "<partial_id>"    # e.g., "d5d2e76a"
```

### Step 2: Gather Full Context
```bash
notebooklm status                # Confirm active notebook
notebooklm summary               # AI-generated summary
notebooklm source list           # All sources with types and status
notebooklm note list             # Existing notes
notebooklm metadata              # Full structured metadata
```

### Step 3: Query for Specific Information (Short Questions, Multi-Turn)
```bash
# Ask for source classification
notebooklm ask "请将所有文献按主题分类，用简短列表回答"

# Ask for technical route
notebooklm ask "核心技术路线是什么？涉及哪些关键技术模块？请简洁列出"

# Ask for innovation points
notebooklm ask "这个项目的创新点和科学价值是什么？"

# Ask for data scale and design
notebooklm ask "这个项目的预期样本量、队列构成和临床试验设计是什么样的？"
```

### Step 4: Ask for Review
```bash
# Initial review
notebooklm ask "请从以下角度全面评审这个基金申请书：1）立项依据的科学问题是否清晰；2）研究内容是否完整；3）技术路线是否可行；4）创新性是否足够；5）研究基础是否扎实；6）预期成果是否明确；7）预算和进度是否合理。逐条给出具体修改意见。"

# Follow up with detail on specific sections
notebooklm ask "请详细列出国内外研究现状，包括ADHD诊断的现有方法及其局限性、二维眼动在ADHD中的应用现状、三维眼动追踪技术的发展、以及现有ML在ADHD筛查中的应用。请给出具体文献引用信息。"
```

### Step 5: Compile and Write
After gathering all information from NotebookLM queries:
1. Synthesize findings into a structured review document
2. Reconstruct the full application following NSFC standards
3. Save both files to the filesystem

### Step 6: Push Back to NotebookLM
```bash
# Add as sources
notebooklm source add /path/to/review_comments.md
notebooklm source add /path/to/reconstructed_application.md

# Create a note for reference
notebooklm note create "Summary of review and reconstruction" -t "评审与重构总结"

# Ask for final verification
notebooklm ask "请确认两个新增来源文件是否已被正确索引。然后基于这两个新文件生成最终摘要。"
```

## Key Discoveries

1. **60-second timeout**: `notebooklm ask` times out at 60s on long questions. Always ask short, focused questions.
2. **Multi-turn is automatic**: Follow-up questions automatically continue the same conversation.
3. **Metadata is richer than source list**: `notebooklm metadata` gives structured data; `notebooklm source list` shows table output.
4. **Sources are indexed immediately**: After `notebooklm source add`, sources show as "ready" — no explicit wait needed for PDFs and Markdown.
5. **Ask is better than file read**: The notebook's AI has already processed and indexed the sources. Asking via `notebooklm ask` gives better contextual analysis than reading raw files.
