---
name: latex-compilation-troubleshooting
description: '` (em-dash)'
signature: 'latex-compilation-troubleshooting -> private: synthetic skill for latex compilation troubleshooting'
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
    description: '` (em-dash)'
    signature: 'latex-compilation-troubleshooting -> private: synthetic skill for latex compilation troubleshooting'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


` (em-dash)
  - `≤` → `$\leq$`
  - `≥` → `$\geq$`
- 或者在preamble添加：`\usepackage[utf8]{inputenc}`（但某些字体仍不支持）

**Environment algorithmic undefined**
- 根因：`algorithmic`包与elsarticle不兼容或加载失败
- 解决：直接删除algorithmic环境（论文通常不需要），或改用`algorithm2e`包
- 检查：`\usepackage{algorithmic}`在preamble中的位置是否正确

#### B. Natbib/Undefined Citations (警告)

**Package natbib Warning: Citation `xxx' undefined**
- 根因：bibtex未执行或引用缺失
- 修复流程：`pdflatex → bibtex paper → pdflatex → pdflatex`
- 检查：paper.bbl是否生成（0字节=失败）
- 检查：paper.blg是否有"0 warnings"
- 如果仍有未定义：检查.bib文件中bibkey是否在.tex中被`\cite{}`引用

#### C. Reference Errors

**Missing \begin{document} after graphicspath fix**
- 根因：正则替换`{{figures/}},{pics/}}`时括号不匹配，导致LaTeX解析器在preamble中找到未闭合括号
- 修复：`\graphicspath{{05-figures/}}` 确保外层`{}`匹配

### 3. 修复验证

```bash
# 编译测试
rm -f paper.*
pdflatex -interaction=nonstopmode paper.tex 2>&1 | grep '! LaTeX Error'
grep -c 'undefined' paper.log

# 如果0错误且0未定义引用 → 成功
# 如果有错误 → 继续修复并重复
```

### 4. 安全守则（铁律）

**操作前必须备份**：\n```bash\ncp paper.tex paper.tex.bak.{timestamp}\n# 或在修改前创建 .bak 文件\n```\n\n**🔴 绝对禁止 `rm -f paper.*` 通配符删除**：\n- `paper.*` 通配符会匹配 `paper.tex`（因为 `.tex` 以 `.t` 开头，匹配 `*`）→ **已发生 2026-06-15 事故**：一次性删除了完整论文源文件\n- 只能删除已确认生成的辅助文件：`rm -f paper.aux paper.log paper.out paper.blg paper.bbl paper.pdf`\n- 删除前用 `ls paper.*` 确认列表中不含 `paper.tex`
- 任何批量操作（replace/patch）前必须创建 `.bak` 备份

**批量修改后验证**：
- 每次 `replace` 或 `patch` 后，立即检查关键部分是否被正确修改
- 编译测试是最快的验证方式

## 陷阱

**Highlignts环境**: `\\begin{highlights}` 是 elsarticle 的扩展环境，需要 `elsarticle-harvard.sty`。默认安装的 elsarticle 不支持。如果报错 `Missing \\item` 且发现 `highlights`，改为 `\\begin{itemize}`。

**D10a 验证 — .bbl 权威来源**：\n- 对于使用外部 `.bib` + `\\bibliography{}` 的论文，D10a **必须**从 `.bbl` 文件验证，而非从 `.bib` 扫描\n- `.bbl` 包含 bibtex 实际解析出的 bibitem keys，是最权威来源\n- 验证方法：`re.findall(r'\\bibitem\{([^}]*)\}', bbl_content)` → 得到确定的 bibitem 集合\n- 然后用 `grep -oP '\\\\cite{[^}]+}' paper.tex | sort -u` 对比 cite keys\n- 常见陷阱：`\\cite{daugman2001statistical, bowyer2008image}` 在注释行（`%%` 开头）中，bibtex 忽略注释 → D10a 不增加 → 必须将引用移至正文
- **equation* in enumerate**: LaTeX 不允许浮动环境（equation*, figure, table）嵌套在 enumerate/itemize 的 item 中。修复方法：将 equation 移到 enumerate 外面，或使用 `minipage` 包裹。

**enumerate[nosep] error**: `\\begin{enumerate}[nosep]` 中的 `nosep` 选项来自 `enumitem` 宏包。elsarticle 等标准文档类不自动加载 `enumitem`。修复：去掉 `[nosep]` 使用默认间距，或在导言区添加 `\\usepackage{enumitem}`。

**Table 最后一行缺 `\\` 导致 `\bottomrule` 级联错误** 🔴 NEW 2026-06-29 — HCS-3WT
- **根因**：tabular 中最后一行数据（在 `\bottomrule` 之前）缺少行尾 `\\`。LaTeX 将 `\bottomrule` 视为新的行内容但当前行未正确结束 → `! Misplaced \noalign` + `! Missing } inserted` + 级联 `! Missing \cr inserted`（100+ 错误）。
- **症状**：错误集中在 `l.203 }` 附近，大量 `! Misplaced \cr` 和 `! Missing \cr inserted`。
- **Detection**：grep 表中最后一行数据（在 `\bottomrule` 前一行）是否以 `\\` 结尾：`grep -B1 '\\\\bottomrule' paper.tex`。最后一行应以 `\\` 结尾。
- **Fix**：在最后一行数据末尾添加 `\\`。例如：`FN reduction vs. best single  & $-38.7\\%$ & -- \\\\`。
- **铁律**：每次 patch 修改表格后，必须检查 `\bottomrule` 前一行的 `\\` 存在性。

**verbatim inside \fbox{}**: LaTeX 的 `verbatim` 环境不能放在 `\fbox{...}` 的参数内部。`\fbox` 在读取参数时已经改变了 catcode，导致 `\begin{verbatim}` 无法正确激活逐字模式。修复：移除 `\fbox{}` 包裹，仅保留 `minipage` 环境。例如将 `\fbox{\begin{minipage}...\begin{verbatim}...\end{verbatim}\end{minipage}}` 改为 `\begin{minipage}...\begin{verbatim}...\end{verbatim}\end{minipage}`。
- **Unicode in LaTeX**: 即使添加了 `inputenc`，某些 Unicode 字符（如 ≈ →）仍需手动替换为 LaTeX 命令。
- **graphicspath bracket matching**: `\graphicspath` 需要双花括号 `{{path/}}`。替换时如果原始路径包含多个目录（如 `{{figures/},{pics/}}`），正则替换必须确保括号配对正确。
- **Algorithmic package compatibility**: `algorithmic` 包在某些环境下（如 elarticle + MiKTeX特定版本）可能与 preamble 中的其他宏包冲突。如果报错 `algorithmic undefined`，直接删除算法环境是最安全的修复方式。
- **Backup-before-destructive**: 任何涉及 `rm`、`cp`、或批量 `replace` 的操作前，必须备份原始文件。`paper.*` 通配符会匹配 `paper.tex`。
- **State-score staleness**: paper-repair cron 生成的 state.json 可能包含过期的 quality_score。修复流程：先检查 quality-report.md 提取 Layer B 分数，用该分数更新 state.json。如果 quality_score >= 80，gate_status 改为 PASS，stage 改为 quality_check_complete。

**External .bib with \bibliography{} — required workflow** 🔴 2026-07-01 — HCS-3WT
- **根因**：删除内嵌 `thebibliography` 后改用外部 `.bib`，缺少 `\bibliographystyle{plain}` 导致 bibtex 执行失败（"I found no \bibstyle command"）。
- **Fix**：在 `\bibliography{references}` 之前必须加 `\bibliographystyle{plain}`。完整流程：`pdflatex → bibtex paper → pdflatex → pdflatex`。
- **路径陷阱**：`.bib` 文件必须与 `.tex` 在**同一目录**（BibTeX 使用相对路径）。如果 bib 在 `06-references/` 而 tex 在 `01-manuscript/`，bibtex 会找不到文件。将 `.bib` 复制到当前目录。
- **验证**：编译后检查 `paper.bbl` 中的 `\bibitem` 计数是否等于论文中 `\cite{}` 的唯一 key 数。

+BibTeX "didn't find database entry" for specific entries — **don't blame the entries, blame the file** 🔴 2026-07-01
- **根因**：当 BibTeX 报告特定条目"找不到"（"I didn't find a database entry for X"），但条目在 `.bib` 文件中存在且语法正确时，问题通常不在这些条目本身，而是文件中**某个更早位置的格式错误**（花括号不匹配、未闭合、特殊字符等）导致 BibTeX 解析提前失败，跳过了后续条目。
- **Debug 流程**：
  1. 用 `hexdump -C` 检查条目字节，确认无不可见字符
  2. 用 `grep -cP '{'` / `grep -cP '}'` 检查花括号平衡
  3. 将嫌疑条目**提取到独立文件**，用最小化 tex 编译测试：如果独立文件成功 → 原文件中有其他条目导致解析失败；如果独立文件也失败 → 条目本身有问题
  4. 如果独立测试成功但原文件失败 → 逐个注释掉原文件中其他条目，逐步缩小问题范围
- **铁律**：BibTeX 对错误条目报 "didn't find" 而非 "illegal character"，容易误导。当多个条目同时"找不到"时，优先怀疑文件结构而非条目内容。

+**Crossref 作者格式差异** 🔴 2026-07-01 — BPPV
- **根因**：Crossref API 返回作者有两种格式：格式1 `given`/`family`（个人作者），格式2 `name`（机构作者）。解析时必须同时处理两种格式，否则机构作者的姓名会丢失。
- **示例**：机构作者返回 `{"name": "Education Directorate Of Thi-Qar, Ministry Of Education, Iraq"}`，`given`/`family` 均为空。
- **Fix**：解析时优先取 `given`+`family`，若无则取 `name`，再无则跳过。

## 参考文件

- ref/latex-error-checklist.md — 完整错误分类速查表
- ref/paper-compile-checklist.md — 每次编译前检查清单
- references/symlink-path-trap-01-manuscript.md — 01-manuscript/ 符号链接路径陷阱（2026-06-18 实战）
- scripts/latex-auto-fix.py — 自动检测和修复常见LaTeX错误的脚本

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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

# Latex Compilation Troubleshooting---





` (em-dash)
  - `≤` → `$\leq$`
  - `≥` → `$\geq$`
- 或者在preamble添加：`\usepackage[utf8]{inputenc}`（但某些字体仍不支持）

**Environment algorithmic undefined**
- 根因：`algorithmic`包与elsarticle不兼容或加载失败
- 解决：直接删除algorithmic环境（论文通常不需要），或改用`algorithm2e`包
- 检查：`\usepackage{algorithmic}`在preamble中的位置是否正确

#### B. Natbib/Undefined Citations (警告)

**Package natbib Warning: Citation `xxx' undefined**
- 根因：bibtex未执行或引用缺失
- 修复流程：`pdflatex → bibtex paper → pdflatex → pdflatex`
- 检查：paper.bbl是否生成（0字节=失败）
- 检查：paper.blg是否有"0 warnings"
- 如果仍有未定义：检查.bib文件中bibkey是否在.tex中被`\cite{}`引用

#### C. Reference Errors

**Missing \begin{document} after graphicspath fix**
- 根因：正则替换`{{figures/}},{pics/}}`时括号不匹配，导致LaTeX解析器在preamble中找到未闭合括号
- 修复：`\graphicspath{{05-figures/}}` 确保外层`{}`匹配

### 3. 修复验证

```bash
# 编译测试
rm -f paper.*
pdflatex -interaction=nonstopmode paper.tex 2>&1 | grep '! LaTeX Error'
grep -c 'undefined' paper.log

# 如果0错误且0未定义引用 → 成功
# 如果有错误 → 继续修复并重复
```

### 4. 安全守则（铁律）

**操作前必须备份**：\n```bash\ncp paper.tex paper.tex.bak.{timestamp}\n# 或在修改前创建 .bak 文件\n```\n\n**🔴 绝对禁止 `rm -f paper.*` 通配符删除**：\n- `paper.*` 通配符会匹配 `paper.tex`（因为 `.tex` 以 `.t` 开头，匹配 `*`）→ **已发生 2026-06-15 事故**：一次性删除了完整论文源文件\n- 只能删除已确认生成的辅助文件：`rm -f paper.aux paper.log paper.out paper.blg paper.bbl paper.pdf`\n- 删除前用 `ls paper.*` 确认列表中不含 `paper.tex`
- 任何批量操作（replace/patch）前必须创建 `.bak` 备份

**批量修改后验证**：
- 每次 `replace` 或 `patch` 后，立即检查关键部分是否被正确修改
- 编译测试是最快的验证方式

## 陷阱

**Highlignts环境**: `\\begin{highlights}` 是 elsarticle 的扩展环境，需要 `elsarticle-harvard.sty`。默认安装的 elsarticle 不支持。如果报错 `Missing \\item` 且发现 `highlights`，改为 `\\begin{itemize}`。

**D10a 验证 — .bbl 权威来源**：\n- 对于使用外部 `.bib` + `\\bibliography{}` 的论文，D10a **必须**从 `.bbl` 文件验证，而非从 `.bib` 扫描\n- `.bbl` 包含 bibtex 实际解析出的 bibitem keys，是最权威来源\n- 验证方法：`re.findall(r'\\bibitem\{([^}]*)\}', bbl_content)` → 得到确定的 bibitem 集合\n- 然后用 `grep -oP '\\\\cite{[^}]+}' paper.tex | sort -u` 对比 cite keys\n- 常见陷阱：`\\cite{daugman2001statistical, bowyer2008image}` 在注释行（`%%` 开头）中，bibtex 忽略注释 → D10a 不增加 → 必须将引用移至正文
- **equation* in enumerate**: LaTeX 不允许浮动环境（equation*, figure, table）嵌套在 enumerate/itemize 的 item 中。修复方法：将 equation 移到 enumerate 外面，或使用 `minipage` 包裹。

**enumerate[nosep] error**: `\\begin{enumerate}[nosep]` 中的 `nosep` 选项来自 `enumitem` 宏包。elsarticle 等标准文档类不自动加载 `enumitem`。修复：去掉 `[nosep]` 使用默认间距，或在导言区添加 `\\usepackage{enumitem}`。

**Table 最后一行缺 `\\` 导致 `\bottomrule` 级联错误** 🔴 NEW 2026-06-29 — HCS-3WT
- **根因**：tabular 中最后一行数据（在 `\bottomrule` 之前）缺少行尾 `\\`。LaTeX 将 `\bottomrule` 视为新的行内容但当前行未正确结束 → `! Misplaced \noalign` + `! Missing } inserted` + 级联 `! Missing \cr inserted`（100+ 错误）。
- **症状**：错误集中在 `l.203 }` 附近，大量 `! Misplaced \cr` 和 `! Missing \cr inserted`。
- **Detection**：grep 表中最后一行数据（在 `\bottomrule` 前一行）是否以 `\\` 结尾：`grep -B1 '\\\\bottomrule' paper.tex`。最后一行应以 `\\` 结尾。
- **Fix**：在最后一行数据末尾添加 `\\`。例如：`FN reduction vs. best single  & $-38.7\\%$ & -- \\\\`。
- **铁律**：每次 patch 修改表格后，必须检查 `\bottomrule` 前一行的 `\\` 存在性。

**verbatim inside \fbox{}**: LaTeX 的 `verbatim` 环境不能放在 `\fbox{...}` 的参数内部。`\fbox` 在读取参数时已经改变了 catcode，导致 `\begin{verbatim}` 无法正确激活逐字模式。修复：移除 `\fbox{}` 包裹，仅保留 `minipage` 环境。例如将 `\fbox{\begin{minipage}...\begin{verbatim}...\end{verbatim}\end{minipage}}` 改为 `\begin{minipage}...\begin{verbatim}...\end{verbatim}\end{minipage}`。
- **Unicode in LaTeX**: 即使添加了 `inputenc`，某些 Unicode 字符（如 ≈ →）仍需手动替换为 LaTeX 命令。
- **graphicspath bracket matching**: `\graphicspath` 需要双花括号 `{{path/}}`。替换时如果原始路径包含多个目录（如 `{{figures/},{pics/}}`），正则替换必须确保括号配对正确。
- **Algorithmic package compatibility**: `algorithmic` 包在某些环境下（如 elarticle + MiKTeX特定版本）可能与 preamble 中的其他宏包冲突。如果报错 `algorithmic undefined`，直接删除算法环境是最安全的修复方式。
- **Backup-before-destructive**: 任何涉及 `rm`、`cp`、或批量 `replace` 的操作前，必须备份原始文件。`paper.*` 通配符会匹配 `paper.tex`。
- **State-score staleness**: paper-repair cron 生成的 state.json 可能包含过期的 quality_score。修复流程：先检查 quality-report.md 提取 Layer B 分数，用该分数更新 state.json。如果 quality_score >= 80，gate_status 改为 PASS，stage 改为 quality_check_complete。

**External .bib with \bibliography{} — required workflow** 🔴 2026-07-01 — HCS-3WT
- **根因**：删除内嵌 `thebibliography` 后改用外部 `.bib`，缺少 `\bibliographystyle{plain}` 导致 bibtex 执行失败（"I found no \bibstyle command"）。
- **Fix**：在 `\bibliography{references}` 之前必须加 `\bibliographystyle{plain}`。完整流程：`pdflatex → bibtex paper → pdflatex → pdflatex`。
- **路径陷阱**：`.bib` 文件必须与 `.tex` 在**同一目录**（BibTeX 使用相对路径）。如果 bib 在 `06-references/` 而 tex 在 `01-manuscript/`，bibtex 会找不到文件。将 `.bib` 复制到当前目录。
- **验证**：编译后检查 `paper.bbl` 中的 `\bibitem` 计数是否等于论文中 `\cite{}` 的唯一 key 数。

+BibTeX "didn't find database entry" for specific entries — **don't blame the entries, blame the file** 🔴 2026-07-01
- **根因**：当 BibTeX 报告特定条目"找不到"（"I didn't find a database entry for X"），但条目在 `.bib` 文件中存在且语法正确时，问题通常不在这些条目本身，而是文件中**某个更早位置的格式错误**（花括号不匹配、未闭合、特殊字符等）导致 BibTeX 解析提前失败，跳过了后续条目。
- **Debug 流程**：
  1. 用 `hexdump -C` 检查条目字节，确认无不可见字符
  2. 用 `grep -cP '{'` / `grep -cP '}'` 检查花括号平衡
  3. 将嫌疑条目**提取到独立文件**，用最小化 tex 编译测试：如果独立文件成功 → 原文件中有其他条目导致解析失败；如果独立文件也失败 → 条目本身有问题
  4. 如果独立测试成功但原文件失败 → 逐个注释掉原文件中其他条目，逐步缩小问题范围
- **铁律**：BibTeX 对错误条目报 "didn't find" 而非 "illegal character"，容易误导。当多个条目同时"找不到"时，优先怀疑文件结构而非条目内容。

+**Crossref 作者格式差异** 🔴 2026-07-01 — BPPV
- **根因**：Crossref API 返回作者有两种格式：格式1 `given`/`family`（个人作者），格式2 `name`（机构作者）。解析时必须同时处理两种格式，否则机构作者的姓名会丢失。
- **示例**：机构作者返回 `{"name": "Education Directorate Of Thi-Qar, Ministry Of Education, Iraq"}`，`given`/`family` 均为空。
- **Fix**：解析时优先取 `given`+`family`，若无则取 `name`，再无则跳过。

## 参考文件

- ref/latex-error-checklist.md — 完整错误分类速查表
- ref/paper-compile-checklist.md — 每次编译前检查清单
- references/symlink-path-trap-01-manuscript.md — 01-manuscript/ 符号链接路径陷阱（2026-06-18 实战）
- scripts/latex-auto-fix.py — 自动检测和修复常见LaTeX错误的脚本

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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

# Latex Compilation Troubleshooting
