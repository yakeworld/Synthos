---



name: sci-paper-standard-structure
description: "Directory index for sci-paper-standard-structure: sci-paper-standard-structure"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "topic: str, outline: dict, references: list[Ref] -> paper_draft: PaperDraft (sections, citations, quality_score)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `paper_type: str, domain: str` — 用户请求描述、上下文信息
- **output**: `structure_spec: dict — 论文结构规范`

> 对应原则：P2（机械原子暴露输入输出规范）



# Sci Paper Standard Structure

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.

## Linked Reference Files

| File | Description |
|------|-------------|
| `references/latex-compilation.md` | Full BibTeX-based compilation chain (pdflatex → bibtex × 3) |
| `references/inline-thebibliography-compilation.md` | Paper 182 session: siunitx incompatibility, abstract math mode, dvipdfm SDict warnings, inline vs BibTeX |
| `references/prewriting-gap-analysis.md` | Gap analysis methodology |
| `references/source-to-methods-extraction.md` | Source extraction to methods mapping |
| `references/system-description-paper-structure.md` | System description paper template |
| `references/template-synthos-meta-paper.md` | Synthos meta-paper template |
| `references/comparative-gap-analysis.md` | Comparative gap analysis |
| `references/fstring-pitfalls.md` | Python f-string LaTeX escape pitfalls |
