---
name: reference-directory-cleanup
description: 1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
signature: 'reference-directory-cleanup -> private: synthetic skill for reference directory cleanup'
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
    signature: 'reference-directory-cleanup -> private: synthetic skill for reference directory cleanup'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
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

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Reference Directory Cleanup---

## 约束规则 · RULES
1. **子目录 PDF 不自动对应**：`pdfs/` 等子目录下 PDF 可能来自旧管线，删除/迁移前必须逐个与当前 `references.bib` 条目内容比对，不匹配则移入 `_archive/`。
2. **名称不匹配查内容**：文件名与 bibkey 不一致（如 `Shams2025.pdf` vs `Shams2023BRFSS`）时，用 `pdfinfo` 或打开 PDF 首页验证标题/作者，确认对应关系后再操作。
3. **Bib 清理顺序**：先清理 `references.bib` 中无效条目 → 再删除 `.tex` 中残留 `\\cite{}` 引用 → 最后 `pdflatex` 重新编译验证 0 undefined reference，禁止乱序操作。
4. **符号链接而非复制**：PDF 在子目录已存在时，根目录创建 symlink 指向原文件，不重复复制（避免双份漂移）。
5. **清理后编译验证**：所有删除/迁移完成后必须 `pdflatex paper.tex` 跑通 0 error + 0 undefined reference，再视为清理完成。
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[REFE-001]** 子目录PDF与当前Bib对应关系不明 → 必须逐个与 `references.bib` 条目内容比对，不匹配则移入 `_archive/` 而非直接删除
- **[REFE-002]** 文件名与 bibkey 不一致（如年份/后缀差异） → 使用 `pdfinfo` 或打开首页验证标题/作者，确认对应关系后再执行操作
- **[REFE-003]** 执行Bib清理任务 → 严格遵循“清理bib无效条目 → 删除.tex残留引用 → 重新编译”的顺序，禁止乱序操作
- **[REFE-004]** PDF在子目录已存在且需根目录访问 → 创建符号链接（symlink）指向原文件，避免复制导致的双份数据漂移
- **[REFE-005]** 清理或迁移操作完成后 → 必须执行 `pdflatex` 编译验证，确保 0 error 且 0 undefined reference 方可视为完成
- **[REFE-006]** 处理旧管线遗留文件 → 不假设子目录PDF与当前项目相关，需基于证据驱动原则核查每个文件的有效性

## 示例 · EXAMPLES

> 基于本技能 RULES / Genes / VERIFICATION 的真实流程构造的语义化示例。

1. **子目录旧PDF不自动对应**（RULES #1 / REFE-001 / REFE-006）
   输入：`pdfs/` 下残留 12 个旧管线 PDF，根目录 `references.bib` 有 29 个条目。
   操作：逐个比对 `pdfs/` 内 PDF 与当前 bib 条目（标题/作者/年份），不匹配者移入 `_archive/`（8 个归档），匹配者保留。
   验证：`ls pdfs/` 无残留旧 PDF；`_archive/` 内 8 个文件可列出；根目录 PDF 数与清理记录一致，`pdflatex` 编译 0 error + 0 undefined reference（VERIFICATION 末项）。

2. **文件名与 bibkey 年份不一致**（RULES #2 / REFE-002 / VERIFICATION #2）
   输入：根目录存在 `Shams2025.pdf`，但 bibkey 为 `Shams2023BRFSS`。
   操作：用 `pdfinfo Shams2025.pdf`（或打开首页）核查真实标题/作者/年份，确认其对应 `Shams2023BRFSS` 条目后改名对齐。
   验证：`pdfinfo` 输出年份/标题与 bibkey 一致；`pdflatex paper.tex` 重新编译 0 undefined reference（REFE-005）。

3. **子目录已有PDF不重复复制**（RULES #4 / REFE-004 / VERIFICATION #4）
   输入：根目录需访问某 PDF，且该 PDF 已存在于 `pdfs/` 子目录。
   操作：在根目录创建 symlink 指向 `pdfs/` 原文件，而非 `cp` 复制。
   验证：`ls -l` 显示该文件为符号链接（`->`），`readlink` 解析回 `pdfs/` 原路径，磁盘仅一份实体文件（无双份漂移）。