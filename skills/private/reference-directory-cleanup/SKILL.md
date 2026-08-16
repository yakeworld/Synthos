---
name: reference-directory-cleanup
description: 1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
signature: 'reference-directory-cleanup -> private: synthetic skill for reference
  directory cleanup'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
    signature: 'reference-directory-cleanup -> private: synthetic skill for reference
      directory cleanup'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---

|
| 根目录删除旧PDF | 7个 |
| 根目录删除旧元数据 | 3个（bibkey-map.json, notebooklm-sources.json, REFERENCE_MANIFEST.md） |
| 删除bak文件 | 5个 |
| 从pdfs复制匹配PDF到根目录 | 8个 |
| 创建符号链接 | 2个 |
| 规范化后根目录PDF/链接 | 18个 |
| Bib总数 | 29个 |

## 注意事项

1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
2. **名称不匹配需要检查内容** — 如 `Shams2025.pdf` vs `Shams2023BRFSS` 需验证内容
3. **3d-eyeball标准**: 45个PDF在根目录 + references.bib + 空pdfs/子目录
4. **Bib清理顺序**：先清理bib中的无效条目，再删除.tex中的残留引用，最后重新编译。详见 `paper-pipeline/SKILL.md`。

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 子目录（`pdfs/`）PDF 逐个与当前 `references.bib` 条目内容比对，未假设自动对应；不匹配者移入 `_archive/` 而非直接删除
- [ ] 文件名与 bibkey 不一致者（如 `Shams2025.pdf` vs `Shams2023BRFSS`）已用 `pdfinfo` 或打开首页验证标题/作者后再操作
- [ ] Bib 清理按序执行：清理 `references.bib` 无效条目 → 删除 `.tex` 残留 `\cite{}` → `pdflatex` 重新编译
- [ ] 子目录已有 PDF 时根目录创建 symlink 指向原文件，未重复复制（避免双份漂移）
- [ ] 清理完成后 `pdflatex paper.tex` 跑通 0 error + 0 undefined reference，方可视为完成
- [ ] 根目录最终状态核对：规范化后 PDF/链接数、Bib 总数与清理记录一致（旧元数据/bak 已清）

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## Golden 集合 · GOLDEN SET

- **Golden Input**: `pdfs/` 子目录含 12 个旧管线 PDF + 根目录 `references.bib` 29 条目，含名称不匹配项（`Shams2025.pdf` vs `Shams2023BRFSS`）
- **Golden Output**: 按 REFE-001/002 逐个比对归档 8 个不匹配 PDF 至 `_archive/`，名称不匹配者 `pdfinfo` 验证后改名对齐，子目录已有 PDF 建 symlink（REFE-004）；`pdflatex paper.tex` 0 error + 0 undefined reference
- **Golden Error**: `pdflatex` 报 undefined reference 或 `.tex` 残留 `\cite{}` 指向已删 bib 条目 → 触发 REFE-003，须按序清理 bib → 删 .tex 残留 → 重编译，禁止乱序

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Reference Directory Cleanup